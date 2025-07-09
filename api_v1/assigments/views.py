from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.DBHelper import db_helper
from ...api_v1.users.auth import fastapi_users
from ..core.models.users import User
from .schemas import NextAssignmentResponse, AnnotationCreate, AssignmentStatus
from . import crud

router = APIRouter(
    prefix="/assignments",
    tags=["assignments"],
)

@router.get("/next", response_model=NextAssignmentResponse)
async def get_next(
    user: User = Depends(fastapi_users.current_user()),
    db: AsyncSession = Depends(db_helper.session_dependency),
):
    """
    Выдать следующее задание (Assignment) текущему аннотатору:
    - если есть существующее статус=new → вернуть его,
    - иначе найти Task, который:
        * не создан этим пользователем,
        * ещё не назначен ему,
      создать Assignment и сразу запросить ai_suggestion,
      сохранить и вернуть.
    """
    assignment = await crud.get_next_assignment(db, user_id=user.id)
    if not assignment:
        # ничего не осталось
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Новых заданий нет"
        )
    return assignment


