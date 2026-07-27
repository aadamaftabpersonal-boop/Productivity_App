from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import User, Contest, ContestTrack
from app.schemas import ContestOut, TrackContestRequest
from app.contests.sync import sync_contests
from app.routers.reviewer import get_current_user  # reuse auth dependency

router = APIRouter(prefix="/contests", tags=["contests"])


from app.contests.codeforces_import import import_codeforces_history
from pydantic import BaseModel

class CodeforcesImportRequest(BaseModel):
    handle: str
    count: int = 50

@router.post("/sync", status_code=status.HTTP_200_OK)
async def trigger_sync(db: AsyncSession = Depends(get_db)):
    """Manually trigger a refresh. In prod, call this from a cron/scheduled job instead."""
    result = await sync_contests(db)
    return result


from app.contests.leetcode_sync import import_leetcode_user_submissions

class CodeforcesImportRequest(BaseModel):
    handle: str
    count: int = 50

class LeetCodeImportRequest(BaseModel):
    handle: str
    count: int = 50

@router.post("/import/codeforces", status_code=status.HTTP_200_OK)
async def import_cf_user_history(
    payload: CodeforcesImportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        current_user.codeforces_handle = payload.handle
        await db.commit()
        res = await import_codeforces_history(db, current_user.id, payload.handle, payload.count)
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/import/leetcode", status_code=status.HTTP_200_OK)
async def import_leetcode_user_history(
    payload: LeetCodeImportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        current_user.leetcode_handle = payload.handle
        await db.commit()
        res = await import_leetcode_user_submissions(payload.handle, payload.count, db=db, user_id=current_user.id)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))






@router.get("/upcoming", response_model=list[ContestOut])
async def list_upcoming(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Contest)
        .where(Contest.is_finished == False)
        .order_by(Contest.start_time.asc())
    )
    return result.scalars().all()


@router.post("/track", status_code=status.HTTP_201_CREATED)
async def track_contest(
    payload: TrackContestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contest_result = await db.execute(select(Contest).where(Contest.id == payload.contest_id))
    if not contest_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Contest not found")

    track = ContestTrack(user_id=current_user.id, contest_id=payload.contest_id)
    db.add(track)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Already tracking this contest")

    return {"message": "Contest tracked"}


@router.get("/tracked", response_model=list[ContestOut])
async def list_tracked(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Contest)
        .join(ContestTrack, ContestTrack.contest_id == Contest.id)
        .where(ContestTrack.user_id == current_user.id)
        .order_by(Contest.start_time.asc())
    )
    return result.scalars().all()


@router.delete("/track/{contest_id}", status_code=status.HTTP_204_NO_CONTENT)
async def untrack_contest(
    contest_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(ContestTrack).where(
            ContestTrack.user_id == current_user.id,
            ContestTrack.contest_id == contest_id,
        )
    )
    track = result.scalar_one_or_none()
    await db.delete(track)
    await db.commit()


from app.contests.warmup import generate_warmup_ladder
from app.weakness.resurface import get_active_weaknesses

@router.get("/warmup")
async def get_warmup_ladder(
    company: str = "meta",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    active_records = await get_active_weaknesses(db, current_user.id)
    user_weaknesses = []
    for r in active_records:
        if hasattr(r, "concept_tag") and r.concept_tag:
            user_weaknesses.append(r.concept_tag.canonical_name)

    ladder = generate_warmup_ladder(company=company, user_weaknesses=user_weaknesses)
    return {"company": company, "ladder": ladder}


from app.contests.post_mortem import generate_post_mortem

@router.get("/{contest_id}/post-mortem")
async def get_contest_post_mortem(
    contest_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        pm = await generate_post_mortem(db, str(current_user.id), contest_id)
        return pm
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
