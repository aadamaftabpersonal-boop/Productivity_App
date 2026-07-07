from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import User, CodeSubmission, ReviewResult
from app.schemas import CodeReviewRequest, SubmissionOut
from app.security import decode_token
from app.reviewer.tree_analysis import analyze_structure
from app.reviewer.llm_review import get_review

router = APIRouter(prefix="/reviewer", tags=["reviewer"])
bearer_scheme = HTTPBearer()


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    try:
        decoded = decode_token(creds.credentials)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    if decoded.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid token type")

    result = await db.execute(select(User).where(User.id == decoded["sub"]))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


@router.post("/submit", response_model=SubmissionOut, status_code=status.HTTP_201_CREATED)
async def submit_code(
    from app.weakness.service import process_review_for_weaknesses
    await process_review_for_weaknesses(db, submission.id, current_user.id)
    payload: CodeReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        heuristics = analyze_structure(payload.code, payload.language)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    submission = CodeSubmission(
        user_id=current_user.id,
        language=payload.language,
        problem_title=payload.problem_title,
        problem_statement=payload.problem_statement,
        code=payload.code,
    )
    db.add(submission)
    await db.flush()  # get submission.id before commit

    try:
        review_data = get_review(
            code=payload.code,
            language=payload.language,
            heuristics=heuristics,
            problem_title=payload.problem_title,
            problem_statement=payload.problem_statement,
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=502, detail=f"Review generation failed: {str(e)}")

    review = ReviewResult(
        submission_id=submission.id,
        time_complexity=review_data["time_complexity"],
        space_complexity=review_data["space_complexity"],
        concepts=review_data["concepts"],
        suggestions=review_data["suggestions"],
        better_approach=review_data["better_approach"],
        score=review_data["score"],
        raw_heuristics=heuristics,
    )
    db.add(review)
    await db.commit()

    result = await db.execute(
        select(CodeSubmission)
        .options(selectinload(CodeSubmission.review))
        .where(CodeSubmission.id == submission.id)
    )
    return result.scalar_one()


@router.get("/history", response_model=list[SubmissionOut])
async def get_history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CodeSubmission)
        .options(selectinload(CodeSubmission.review))
        .where(CodeSubmission.user_id == current_user.id)
        .order_by(CodeSubmission.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{submission_id}", response_model=SubmissionOut)
async def get_submission(
    submission_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CodeSubmission)
        .options(selectinload(CodeSubmission.review))
        .where(CodeSubmission.id == submission_id, CodeSubmission.user_id == current_user.id)
    )
    submission = result.scalar_one_or_none()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission