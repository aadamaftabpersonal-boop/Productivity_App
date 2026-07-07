import random
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import WeaknessRecord, ConceptTag, SubmissionConcept, CodeSubmission
from app.weakness.problem_bank import PROBLEM_BANK

RESURFACE_COOLDOWN_HOURS = 24  # don't resurface the same weakness more than once a day


async def get_active_weaknesses(db: AsyncSession, user_id) -> list[WeaknessRecord]:
    result = await db.execute(
        select(WeaknessRecord)
        .options(selectinload(WeaknessRecord.concept_tag) if hasattr(WeaknessRecord, "concept_tag") else selectinload("*"))
        .where(WeaknessRecord.user_id == user_id, WeaknessRecord.is_active_weakness == True)
        .order_by(WeaknessRecord.gap_count.desc())
    )
    return result.scalars().all()


async def get_resurface_item(db: AsyncSession, user_id) -> dict | None:
    """Picks ONE weakness to resurface, alternating between:
    - the user's own old flagged submission (active reconstruction)
    - a fresh problem from the curated bank
    Skips weaknesses resurfaced within the cooldown window."""

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
        or (now - wr.last_resurfaced_at).total_seconds() > RESURFACE_COOLDOWN_HOURS * 3600
    ]
    if not eligible:
        return None

    weakness_record, concept_tag = eligible[0]  # highest gap_count first

    # alternate: even gap_count -> resurface own submission, odd -> fresh problem
    # (simple deterministic alternation, not random, so behavior is explainable)
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
                "submission_id": str(old_submission.id),
                "problem_title": old_submission.problem_title,
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
        "mode": "fresh_problem",
        "concept": concept_tag.display_name,
        "problem_title": problem["title"],
        "url": problem["url"],
        "instruction": f"You've been flagged on {concept_tag.display_name} {weakness_record.gap_count} time(s). Try this problem to target it directly.",
    }
    weakness_record.last_resurfaced_at = now
    await db.commit()
    return item