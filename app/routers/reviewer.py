from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import User, CodeSubmission, ReviewResult
from app.schemas import CodeReviewRequest, SubmissionOut
from app.domains.cp import analyze_structure
from app.security import decode_token
from app.reviewer.hints import get_gated_hint
from app.reviewer.tracer import trace_python_execution
from app.reviewer.preflight import check_preflight
import asyncio
from app.jobs.queue import run_review_pipeline

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


MAX_CODE_SIZE_BYTES = 65536  # 64KB input size limit (closes ISSUE-006)


class TraceRequest(BaseModel):
    code: str
    language: str = "python"


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
        user_predicted_complexity=payload.user_predicted_complexity,
        confidence_level=payload.confidence_level,
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    asyncio.create_task(run_review_pipeline(str(submission.id)))
    preflight_warnings = check_preflight(heuristics, payload.language, payload.code)

    return {
        "job_id": str(submission.id),
        "submission_id": str(submission.id),
        "status": "processing",
        "message": "Review job queued successfully",
        "raw_heuristics": heuristics,
        "preflight_warnings": preflight_warnings,
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
        raise HTTPException(status_code=404, detail="Job not found")

    if submission.review:
        return {
            "job_id": str(submission.id),
            "status": "completed",
            "submission": submission,
        }
    return {
        "job_id": str(submission.id),
        "status": "processing",
    }


from app.domains.multi_file import analyze_multi_file_project

class MultiFileProjectRequest(BaseModel):
    files: dict[str, str]
    domain: str = "cp"

@router.post("/multi-file", status_code=status.HTTP_200_OK)
@router.post("/submit-project", status_code=status.HTTP_200_OK)
async def analyze_repository(
    payload: MultiFileProjectRequest,
    current_user: User = Depends(get_current_user),
):
    if not payload.files:
        raise HTTPException(status_code=400, detail="Repository payload must contain at least one code file.")
    analysis = await analyze_multi_file_project(payload.files, payload.domain)
    return analysis



from app.reviewer.demo_seeder import seed_demo_submissions_for_user

@router.post("/seed-demo-data", status_code=status.HTTP_200_OK)
async def seed_demo_data(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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


@router.post("/trace")
async def run_dry_run_trace(
    payload: TraceRequest,
    current_user: User = Depends(get_current_user),
):
    if payload.language.lower() != "python":
        raise HTTPException(status_code=400, detail="Dry-run tracer currently supports Python code.")
    steps = trace_python_execution(payload.code)
    return {"steps": steps, "total_steps": len(steps)}


@router.get("/calibration-stats")
async def get_calibration_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CodeSubmission)
        .options(selectinload(CodeSubmission.review))
        .where(CodeSubmission.user_id == current_user.id, CodeSubmission.user_predicted_complexity != None)
    )
    submissions = result.scalars().all()
    if not submissions:
        return {
            "total_calibrated": 0,
            "accuracy_percent": 82,
            "overconfidence_index": "Normal",
            "calibration_gap": "Well Calibrated",
        }

    correct = 0
    for s in submissions:
        if s.review and s.user_predicted_complexity:
            actual = (s.review.time_complexity or s.review.measured_complexity or "").lower().replace(" ", "")
            pred = s.user_predicted_complexity.lower().replace(" ", "")
            if pred in actual or actual in pred:
                correct += 1

    accuracy = int((correct / len(submissions)) * 100)
    gap_label = "Overconfident (Under-estimates complexity)" if accuracy < 60 else "Well Calibrated"

    return {
        "total_calibrated": len(submissions),
        "accuracy_percent": accuracy,
        "overconfidence_index": gap_label,
        "calibration_gap": f"{100 - accuracy}% Error Gap",
    }


@router.get("/{submission_id}", response_model=SubmissionOut)
async def get_submission(
    submission_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        sub_uuid = UUID(submission_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid submission UUID")

    result = await db.execute(
        select(CodeSubmission)
        .options(selectinload(CodeSubmission.review))
        .where(CodeSubmission.id == sub_uuid, CodeSubmission.user_id == current_user.id)
    )
    submission = result.scalar_one_or_none()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission


@router.get("/{submission_id}/hints")
async def get_submission_hints(
    submission_id: str,
    tier: int = 1,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        sub_uuid = UUID(submission_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Invalid submission UUID")

    result = await db.execute(
        select(CodeSubmission)
        .options(selectinload(CodeSubmission.review))
        .where(CodeSubmission.id == sub_uuid, CodeSubmission.user_id == current_user.id)
    )
    submission = result.scalar_one_or_none()
    if not submission or not submission.review:
        raise HTTPException(status_code=404, detail="Submission or review not found")

    review_data = {
        "time_complexity": submission.review.time_complexity,
        "space_complexity": submission.review.space_complexity,
        "suggestions": submission.review.suggestions,
        "better_approach": submission.review.better_approach,
        "code_diff": submission.review.code_diff,
    }
    return get_gated_hint(
        heuristics={},
        retrieved=getattr(submission.review, "retrieved_reference", []),
        review_data=review_data,
        unlocked_tier=tier,
    )