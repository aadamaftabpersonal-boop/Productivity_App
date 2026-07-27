from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models import User, CodeSubmission, WeaknessRecord, ConceptTag
from app.routers.reviewer import get_current_user

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


@router.get("", response_model=list[dict])
async def get_tech_club_leaderboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns gamified Tech Club Hall of Fame ranking members by Mastery & Weakness Resolution."""
    users_result = await db.execute(select(User))
    users = users_result.scalars().all()

    leaderboard = []
    for user in users:
        # Count submissions
        sub_res = await db.execute(
            select(func.count(CodeSubmission.id)).where(CodeSubmission.user_id == user.id)
        )
        total_subs = sub_res.scalar() or 0

        # Count active vs resolved weaknesses
        wr_res = await db.execute(
            select(WeaknessRecord).where(WeaknessRecord.user_id == user.id)
        )
        records = wr_res.scalars().all()
        active_weaknesses = sum(1 for r in records if r.is_active_weakness)
        total_gaps = sum(r.gap_count for r in records)

        mastery_score = max(0, 100 - total_gaps * 15)

        # Generate achievement badges
        badges = []
        if total_subs >= 5:
            badges.append("AST Master")
        if mastery_score >= 80:
            badges.append("Algorithm Architect")
        if active_weaknesses == 0 and total_subs > 0:
            badges.append("Flawless Code Specialist")
        if not badges:
            badges.append("Club Apprentice")

        leaderboard.append({
            "user_id": str(user.id),
            "full_name": user.full_name or user.email.split("@")[0],
            "email": user.email,
            "mastery_score": mastery_score,
            "total_submissions": total_subs,
            "active_weaknesses": active_weaknesses,
            "badges": badges,
        })

    # Sort descending by mastery score, then total submissions
    leaderboard.sort(key=lambda x: (x["mastery_score"], x["total_submissions"]), reverse=True)
    return leaderboard
