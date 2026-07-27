from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User, WeaknessRecord, ConceptTag
from app.schemas import ActiveWeaknessOut, ResurfaceOut
from app.routers.reviewer import get_current_user
from app.weakness.resurface import get_resurface_item

router = APIRouter(prefix="/weakness", tags=["weakness"])


@router.get("/active", response_model=list[ActiveWeaknessOut])
async def list_active_weaknesses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(WeaknessRecord, ConceptTag)
        .join(ConceptTag, WeaknessRecord.concept_tag_id == ConceptTag.id)
        .where(WeaknessRecord.user_id == current_user.id, WeaknessRecord.is_active_weakness == True)
        .order_by(WeaknessRecord.gap_count.desc())
    )
    rows = result.all()
    return [
        ActiveWeaknessOut(
            concept=ct.display_name,
            gap_count=wr.gap_count,
            last_flagged_at=wr.last_flagged_at,
        )
        for wr, ct in rows
    ]


from app.weakness.resurface import get_resurface_item, record_resurface_result
from pydantic import BaseModel

class CompleteResurfaceRequest(BaseModel):
    concept_tag_id: str
    success: bool
    time_taken_seconds: int = 0


@router.get("/resurface", response_model=ResurfaceOut)
async def resurface(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = await get_resurface_item(db, current_user.id)
    if not item:
        raise HTTPException(status_code=404, detail="No weakness to resurface right now — either no active weaknesses, or all are in cooldown")
    return item


@router.post("/resurface/complete")
async def complete_resurface_item(
    payload: CompleteResurfaceRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    res = await record_resurface_result(
        db, current_user.id, payload.concept_tag_id, payload.success, payload.time_taken_seconds
    )
    if "error" in res:
        raise HTTPException(status_code=404, detail=res["error"])
    return res