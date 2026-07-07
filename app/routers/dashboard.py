from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import User, CodeSubmission, WeaknessRecord, ConceptTag, Contest, ContestTrack
from app.schemas import DashboardOut, UserOut, ActiveWeaknessOut
from app.routers.reviewer import get_current_user
from app.weakness.resurface import get_resurface_item

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardOut)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # recent submissions (last 5)
    sub_result = await db.execute(
        select(CodeSubmission)
        .options(selectinload(CodeSubmission.review))
        .where(CodeSubmission.user_id == current_user.id)
        .order_by(CodeSubmission.created_at.desc())
        .limit(5)
    )
    recent_submissions = sub_result.scalars().all()

    # active weaknesses
    weakness_result = await db.execute(
        select(WeaknessRecord, ConceptTag)
        .join(ConceptTag, WeaknessRecord.concept_tag_id == ConceptTag.id)
        .where(WeaknessRecord.user_id == current_user.id, WeaknessRecord.is_active_weakness == True)
        .order_by(WeaknessRecord.gap_count.desc())
    )
    active_weaknesses = [
        ActiveWeaknessOut(concept=ct.display_name, gap_count=wr.gap_count, last_flagged_at=wr.last_flagged_at)
        for wr, ct in weakness_result.all()
    ]

    # resurface item (may be None if nothing eligible — that's expected, not an error)
    resurface_item = await get_resurface_item(db, current_user.id)

    # upcoming contests (next 10)
    upcoming_result = await db.execute(
        select(Contest)
        .where(Contest.is_finished == False)
        .order_by(Contest.start_time.asc())
        .limit(10)
    )
    upcoming_contests = upcoming_result.scalars().all()

    # tracked contests
    tracked_result = await db.execute(
        select(Contest)
        .join(ContestTrack, ContestTrack.contest_id == Contest.id)
        .where(ContestTrack.user_id == current_user.id)
        .order_by(Contest.start_time.asc())
    )
    tracked_contests = tracked_result.scalars().all()

    return DashboardOut(
        user=UserOut.model_validate(current_user),
        recent_submissions=recent_submissions,
        active_weaknesses=active_weaknesses,
        resurface_item=resurface_item,
        upcoming_contests=upcoming_contests,
        tracked_contests=tracked_contests,
    )