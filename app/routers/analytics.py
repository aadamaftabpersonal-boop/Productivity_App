from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models import User, WeaknessRecord, ConceptTag, CodeSubmission, ReviewResult
from app.routers.reviewer import get_current_user
from app.weakness.matcher import load_concept_index

router = APIRouter(prefix="/weakness", tags=["analytics"])


@router.get("/analytics")
async def get_weakness_analytics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns dynamic concept mastery radar scores, domain breakdowns, and weakness resolution stats."""
    concept_index = await load_concept_index(db)

    # Fetch all user weakness records
    wr_result = await db.execute(
        select(WeaknessRecord, ConceptTag)
        .join(ConceptTag, WeaknessRecord.concept_tag_id == ConceptTag.id)
        .where(WeaknessRecord.user_id == current_user.id)
    )
    user_records = {ct.canonical_name: wr for wr, ct in wr_result.all()}

    # Compute pentagon / radar mastery score for all taxonomy concepts
    mastery_radar = []
    for canonical_name, tag in concept_index.items():
        if tag.canonical_name != canonical_name:  # skip aliases, use canonical
            continue
        wr = user_records.get(canonical_name)
        gap_count = wr.gap_count if wr else 0
        mastery_pct = max(0, 100 - gap_count * 25)
        mastery_radar.append({
            "concept_id": str(tag.id),
            "canonical_name": tag.canonical_name,
            "display_name": tag.display_name,
            "gap_count": gap_count,
            "mastery_percent": mastery_pct,
            "is_active_weakness": wr.is_active_weakness if wr else False,
        })

    # Domain breakdown metrics (CP, ML, SWE)
    domain_stats = {}
    for domain in ("cp", "ml", "swe"):
        sub_res = await db.execute(
            select(func.count(CodeSubmission.id))
            .where(CodeSubmission.user_id == current_user.id, CodeSubmission.domain == domain)
        )
        sub_count = sub_res.scalar() or 0

        domain_stats[domain] = {
            "total_submissions": sub_count,
        }

    # Weakness Resolution Velocity
    active_count = sum(1 for item in mastery_radar if item["is_active_weakness"])
    resolved_count = sum(1 for item in mastery_radar if item["gap_count"] == 0 and item["mastery_percent"] == 100)

    return {
        "user_id": str(current_user.id),
        "mastery_radar": mastery_radar,
        "active_weakness_count": active_count,
        "resolved_weakness_count": resolved_count,
        "domain_stats": domain_stats,
    }
