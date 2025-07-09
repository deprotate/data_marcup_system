from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.DBHelper import db_helper
from .schemas import TaskCreate, TaskRead
from . import crud
from ...api_v1.users.auth import fastapi_users
from ..core.models.users import User

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)

@router.get("/", response_model=list[TaskRead])
async def list_tasks(
    user: User = Depends(fastapi_users.current_user()),
    db: AsyncSession = Depends(db_helper.session_dependency),
):
    """
    Вернуть все задачи, созданные текущим пользователем.
    """
    tasks = await crud.get_tasks_by_owner(db, owner_id=user.id)
    return tasks

@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    user: User = Depends(fastapi_users.current_user()),
    db: AsyncSession = Depends(db_helper.session_dependency),
):
    """
    Создать задачу по шаблону template_name, с контентом content,
    и привязать к текущему пользователю.
    """
    try:
        task = await crud.create_task(
            db,
            owner_id=user.id,
            template_name=data.template_name,
            content=data.content,
        )
    except ValueError as e:
        # например, если шаблон не найден или content не валиден
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))

    return task

@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int,
    user: User = Depends(fastapi_users.current_user()),
    db: AsyncSession = Depends(db_helper.session_dependency),
):
    """
    Вернуть задачу по ID, только если она принадлежит текущему пользователю.
    """
    task = await crud.get_task_by_id(db, task_id=task_id, owner_id=user.id)
    if not task:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
    return task



@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    user: User = Depends(fastapi_users.current_user()),
    db: AsyncSession = Depends(db_helper.session_dependency),
):
    """
    Удалить задачу, если она принадлежит текущему пользователю.
    """
    deleted = await crud.delete_task_by_owner(db, task_id=task_id, owner_id=user.id)
    if not deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Задача не найдена")
