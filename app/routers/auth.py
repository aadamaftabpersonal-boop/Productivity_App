from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.database import get_db
from app.models import User, RefreshToken
from app.schemas import UserCreate, UserLogin, UserOut, TokenPair, RefreshRequest
from app.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token
)

router = APIRouter(prefix="/auth", tags=["auth"])


async def issue_token_pair(db: AsyncSession, user: User) -> TokenPair:
    access = create_access_token(str(user.id), user.role)
    refresh, jti, expires_at = create_refresh_token(str(user.id))

    db.add(RefreshToken(jti=jti, user_id=user.id, expires_at=expires_at))
    await db.commit()

    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=TokenPair)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    return await issue_token_pair(db, user)


@router.post("/refresh", response_model=TokenPair)
async def refresh_token(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        decoded = decode_token(payload.refresh_token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    if decoded.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    jti = decoded["jti"]
    user_id = decoded["sub"]

    result = await db.execute(select(RefreshToken).where(RefreshToken.jti == jti))
    stored = result.scalar_one_or_none()

    if not stored:
        raise HTTPException(status_code=401, detail="Refresh token not recognized")

    # Reuse detection: if a revoked token is presented again, treat as compromise
    if stored.revoked:
        await db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked == False)
            .values(revoked=True)
        )
        await db.commit()
        raise HTTPException(status_code=401, detail="Token reuse detected, all sessions revoked")

    if stored.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired")

    user_result = await db.execute(select(User).where(User.id == user_id))
    user = user_result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    # Rotate: revoke old, issue new
    new_pair = await issue_token_pair(db, user)
    new_decoded = decode_token(new_pair.refresh_token)

    stored.revoked = True
    stored.replaced_by_jti = new_decoded["jti"]
    await db.commit()

    return new_pair


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        decoded = decode_token(payload.refresh_token)
    except ValueError:
        return  # already invalid, nothing to do

    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.jti == decoded.get("jti"))
        .values(revoked=True)
    )
    await db.commit()