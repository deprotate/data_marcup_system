from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.DBHelper import db_helper
from ..users.auth import app_users
from .schemas import OverallStats, TemplateStats, TemplateStatsItem
from .crud import get_overall_counts, get_per_template_stats

router = APIRouter(prefix="/stats", tags=["stats"])
current_user = app_users.current_user()

@router.get("/overall", response_model=OverallStats)
async def overall_stats(
    user=Depends(current_user),
    db: AsyncSession = Depends(db_helper.session_dependency),
):
    counts = await get_overall_counts(db, owner_id=user.id)
    return OverallStats(**counts)

@router.get("/templates", response_model=TemplateStats)
async def templates_stats(
    user=Depends(current_user),
    db: AsyncSession = Depends(db_helper.session_dependency),
):
    items_data = await get_per_template_stats(db, owner_id=user.id)
    items = [TemplateStatsItem(**d) for d in items_data]
    return TemplateStats(templates=items)
