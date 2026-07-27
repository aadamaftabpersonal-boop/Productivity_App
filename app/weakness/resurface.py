import random
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import WeaknessRecord, ConceptTag, SubmissionConcept, CodeSubmission
from app.weakness.problem_bank import PROBLEM_BANK


async def get_active_weaknesses(db: AsyncSession, user_id) -> list[WeaknessRecord]:
    result = await db.execute(
        select(WeaknessRecord)
        .options(selectinload(WeaknessRecord.concept_tag) if hasattr(WeaknessRecord, "concept_tag") else selectinload("*"))
        .where(WeaknessRecord.user_id == user_id, WeaknessRecord.is_active_weakness == True)
        .order_by(WeaknessRecord.gap_count.desc())
    )
    return result.scalars().all()


async def get_resurface_item(db: AsyncSession, user_id) -> dict | None:
    """Picks ONE weakness to resurface using FSRS-inspired stability_days scheduling.
    
    Alternates between active reconstruction of user's own flagged code and fresh bank problems.
    Skips weaknesses resurfaced before stability_days interval expires.
    """
    result = await db.execute(
        select(WeaknessRecord, ConceptTag)
        .join(ConceptTag, WeaknessRecord.concept_tag_id == ConceptTag.id)
        .where(WeaknessRecord.user_id == user_id, WeaknessRecord.is_active_weakness == True)
        .order_by(WeaknessRecord.gap_count.desc())
    )
    rows = result.all()
    if not rows:
        return None

    now = datetime.now(timezone.utc)
    eligible = [
        (wr, ct) for wr, ct in rows
        if wr.last_resurfaced_at is None
        or now >= (wr.last_resurfaced_at + timedelta(days=getattr(wr, "stability_days", 1.0)))
    ]
    if not eligible:
        return None

    weakness_record, concept_tag = eligible[0]  # highest gap_count first
    old_submission = None

    # alternate: even gap_count -> resurface own submission, odd -> fresh problem
    mode = "own_submission" if weakness_record.gap_count % 2 == 0 else "fresh_problem"

    if mode == "own_submission":
        sub_result = await db.execute(
            select(CodeSubmission)
            .join(SubmissionConcept, SubmissionConcept.submission_id == CodeSubmission.id)
            .where(
                SubmissionConcept.concept_tag_id == concept_tag.id,
                SubmissionConcept.was_flagged_as_gap == True,
                CodeSubmission.user_id == user_id,
            )
            .order_by(CodeSubmission.created_at.desc())
            .limit(1)
        )
        old_submission = sub_result.scalar_one_or_none()
        if old_submission:
            item = {
                "mode": "own_submission",
                "concept": concept_tag.display_name,
                "concept_tag_id": str(concept_tag.id),
                "submission_id": str(old_submission.id),
                "problem_title": old_submission.problem_title or "Previous Submission",
                "instruction": f"Re-attempt this problem from scratch, without looking at your old code. You were flagged on {concept_tag.display_name} here {weakness_record.gap_count} time(s).",
            }
            weakness_record.last_resurfaced_at = now
            await db.commit()
            return item

    # fallback to fresh_problem if no old submission found, or mode selected fresh_problem
    bank = PROBLEM_BANK.get(concept_tag.canonical_name, [])
    if not bank:
        return None
    problem = random.choice(bank)
    item = {
        "mode": mode,
        "concept": concept_tag.display_name,
        "concept_tag_id": str(concept_tag.id),
        "problem_title": old_submission.problem_title if mode == "own_submission" and old_submission else problem["title"],
        "url": problem["url"] if mode == "fresh_problem" or not old_submission else None,
        "submission_id": str(old_submission.id) if mode == "own_submission" and old_submission else None,
        "instruction": f"Virtual Contest Rep: Target your weakness in {concept_tag.display_name}. 30-minute timer starts now!",
        "time_limit_minutes": 30,
        "initial_cf_points": 500,
    }
    weakness_record.last_resurfaced_at = now
    await db.commit()
    return item


async def record_resurface_result(
    db: AsyncSession, user_id, concept_tag_id, success: bool, time_taken_seconds: int = 0
) -> dict:
    """Decay-on-success logic with FSRS-inspired stability_days growth/decay.
    
    If success=True: double stability_days (up to 30.0 days cap) and decay gap_count by 1.
    If success=False: halve stability_days (down to 1.0 day floor) and increment gap_count by 1.
    """
    result = await db.execute(
        select(WeaknessRecord).where(
            WeaknessRecord.user_id == user_id,
            WeaknessRecord.concept_tag_id == concept_tag_id,
        )
    )
    record = result.scalar_one_or_none()
    if not record:
        return {"error": "Weakness record not found"}

    current_stability = getattr(record, "stability_days", 1.0)

    if success:
        record.gap_count = max(0, record.gap_count - 1)
        record.stability_days = min(30.0, current_stability * 2.0)
        if record.gap_count < 2:
            record.is_active_weakness = False
        points_earned = max(100, 500 - int(time_taken_seconds / 60) * 2)
    else:
        record.gap_count += 1
        record.stability_days = max(1.0, current_stability / 2.0)
        record.is_active_weakness = True
        points_earned = 0

    record.updated_at = datetime.now(timezone.utc)
    await db.commit()

    return {
        "success": success,
        "new_gap_count": record.gap_count,
        "new_stability_days": record.stability_days,
        "is_active_weakness": record.is_active_weakness,
        "cf_points_earned": points_earned,
    }