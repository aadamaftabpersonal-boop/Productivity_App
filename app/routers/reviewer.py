from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.weakness.service import process_review_for_weaknesses

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


from app.reviewer.complexity_sandbox import measure_empirical_complexity, cross_check_complexity

MAX_CODE_SIZE_BYTES = 65536  # 64KB input size limit (closes ISSUE-006)


import asyncio
from app.jobs.queue import run_review_pipeline


@router.post("/submit", status_code=status.HTTP_202_ACCEPTED)
async def submit_code(
    payload: CodeReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if len(payload.code.encode("utf-8")) > MAX_CODE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"Code size exceeds maximum limit of {MAX_CODE_SIZE_BYTES // 1024}KB",
        )

    try:
        heuristics = analyze_structure(payload.code, payload.language)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    submission = CodeSubmission(
        user_id=current_user.id,
        domain=payload.domain,
        language=payload.language,
        problem_title=payload.problem_title,
        problem_statement=payload.problem_statement,
        code=payload.code,
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    # Launch background job pipeline asynchronously (closes ISSUE-004)
    asyncio.create_task(run_review_pipeline(str(submission.id)))

    return {
        "job_id": str(submission.id),
        "submission_id": str(submission.id),
        "status": "processing",
        "message": "Review job queued successfully",
    }


@router.get("/job/{job_id}")
async def get_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CodeSubmission)
        .options(selectinload(CodeSubmission.review))
        .where(CodeSubmission.id == job_id, CodeSubmission.user_id == current_user.id)
    )
    submission = result.scalar_one_or_none()
    if not submission:
        raise HTTPException(status_code=404, detail="Job/Submission not found")

    if submission.review is None:
        return {"job_id": job_id, "status": "processing", "review": None}

    return {
        "job_id": job_id,
        "status": "completed",
        "submission": submission,
    }


from app.domains.multi_file import analyze_multi_file_project
from pydantic import BaseModel


class MultiFileProjectRequest(BaseModel):
    domain: str = "cp"  # "cp" | "swe"
    files: dict[str, str]


@router.post("/submit-project", status_code=status.HTTP_200_OK)
async def submit_multi_file_project(
    payload: MultiFileProjectRequest,
    current_user: User = Depends(get_current_user),
):
    if not payload.files:
        raise HTTPException(status_code=400, detail="Files dictionary cannot be empty")
    
    res = await analyze_multi_file_project(payload.files, payload.domain)
    return res




from app.reviewer.demo_seeder import seed_demo_submissions_for_user

@router.post("/seed-demo-data", status_code=status.HTTP_200_OK)
async def seed_demo_data(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Seeds 15+ realistic bad code submissions into the database for live demonstration & stress testing."""
    res = await seed_demo_submissions_for_user(db, current_user.id)
    return res


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