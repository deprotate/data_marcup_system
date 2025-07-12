from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from ..annotations.schemas import AnnotationCreate
from ..core.DBHelper import db_helper
from ..core.models.users import User
from ..users.auth import app_users
from .schemas import (
    NextAssignmentResponse,
    AssignmentStatus,
)
from . import crud

router = APIRouter(
    prefix="/assignments",
    tags=["assignments"],
)

current_user = app_users.current_user()


@router.get("/next", response_model=NextAssignmentResponse)
async def get_next(
    user: User = Depends(app_users.current_user()),
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


@router.get("/next", response_model=NextAssignmentResponse)
async def get_next_assignment(
    user: User = Depends(current_user),
    db: AsyncSession = Depends(db_helper.session_dependency),
):
    """
    Выдать следующее задание для разметки.
    """
    assignment = await crud.find_or_create_assignment_for_user(db, user.id)

    if assignment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Нет доступных заданий")

    return assignment


@router.post("/{assignment_id}/annotate", status_code=status.HTTP_201_CREATED)
async def submit_annotation(
    assignment_id: UUID,
    data: AnnotationCreate,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(db_helper.session_dependency),
):
    """
    Принять аннотацию от пользователя.
    """
    try:
        await crud.submit_annotation(
            db=db,
            assignment_id=assignment_id,
            user_id=user.id,
            data=data,
        )
    except ValueError as e:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{assignment_id}/status", response_model=AssignmentStatus)
async def get_annotation_status(
    assignment_id: UUID,
    user: User = Depends(current_user),
    db: AsyncSession = Depends(db_helper.session_dependency),
):
    """
    Получить статус: был ли сделан ответ, какая подсказка от ИИ и т.д.
    """
    status_data = await crud.get_assignment_status(db, assignment_id, user.id)
    if not status_data:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Задание не найдено")
    return status_data
