from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models import SubmissionConcept, WeaknessRecord, CodeSubmission, ReviewResult
from app.weakness.matcher import load_concept_index, match_text_to_concept

GAP_THRESHOLD = 2  # flagged 2+ times => becomes an active weakness, not a one-off


async def process_review_for_weaknesses(db: AsyncSession, submission_id, user_id) -> None:
    """Call this right after a ReviewResult is created. Extracts concepts,
    tags which ones were flagged as gaps (from `suggestions`), links them to the submission,
    and updates per-user weakness aggregates."""

    result = await db.execute(select(ReviewResult).where(ReviewResult.submission_id == submission_id))
    review = result.scalar_one_or_none()
    if not review:
        return

    concept_index = await load_concept_index(db)

    # concepts used/relevant (not necessarily gaps)
    matched_used = set()
    for concept_text in review.concepts:
        tag = match_text_to_concept(concept_text, concept_index)
        if tag:
            matched_used.add(tag.id)

    # concepts flagged as actual gaps (from suggestions' issue/fix text — this is the stronger signal)
    matched_gaps = set()
    for suggestion in review.suggestions:
        issue_text = suggestion.get("issue", "") + " " + suggestion.get("fix", "")
        tag = match_text_to_concept(issue_text, concept_index)
        if tag:
            matched_gaps.add(tag.id)

    all_concept_ids = matched_used | matched_gaps
    for concept_id in all_concept_ids:
        db.add(SubmissionConcept(
            submission_id=submission_id,
            concept_tag_id=concept_id,
            was_flagged_as_gap=(concept_id in matched_gaps),
        ))

    now = datetime.now(timezone.utc)
    for concept_id in matched_gaps:
        stmt = pg_insert(WeaknessRecord).values(
            user_id=user_id,
            concept_tag_id=concept_id,
            gap_count=1,
            last_flagged_at=now,
            is_active_weakness=False,
        )
        stmt = stmt.on_conflict_do_update(
            constraint="uq_user_concept",
            set_={
                "gap_count": WeaknessRecord.gap_count + 1,
                "last_flagged_at": now,
            },
        )
        await db.execute(stmt)

    await db.commit()

    # second pass: promote to active_weakness if threshold crossed
    result = await db.execute(
        select(WeaknessRecord).where(
            WeaknessRecord.user_id == user_id,
            WeaknessRecord.concept_tag_id.in_(matched_gaps) if matched_gaps else False,
        )
    )
    for record in result.scalars().all():
        if record.gap_count >= GAP_THRESHOLD and not record.is_active_weakness:
            record.is_active_weakness = True
    await db.commit()