from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from ..core.DBHelper import db_helper
from ..core.models.task_templates import TaskTemplate
from .schemas import TaskTemplateCreate, TaskTemplateRead
from . import crud
from ..core.models.users import User
from ..users.auth import app_users

router = APIRouter(
    prefix="/task_templates",
    tags=["task_templates"],
)


@router.get("/", response_model=list[TaskTemplateRead])
async def list_templates(
    user: User = Depends(app_users.current_user()),
    db: AsyncSession = Depends(db_helper.session_dependency),
):
    """
    Вернуть все шаблоны, принадлежащие текущему user.id
    """
    templates = await crud.get_templates_by_owner(db, owner_id=user.id)
    return templates



@router.post("/", response_model=TaskTemplateRead, status_code=status.HTTP_201_CREATED)
async def create_template(
    data: TaskTemplateCreate,
    user: User = Depends(app_users.current_user()),
    db: AsyncSession = Depends(db_helper.session_dependency),
):
    """
    Создать новый шаблон от имени user.id, если он ещё не превысил лимит в 50.
    """
    # проверим лимит
    count = await crud.count_templates(db, owner_id=user.id)
    if count >= 50:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Превышен лимит в 50 шаблонов"
        )

    try:
        tpl = await crud.create_template(db, owner_id=user.id, data=data)
    except ValueError as e:
        # например, если name уже занят
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=str(e))
    return tpl


@router.get("/{template_name}", response_model=TaskTemplateRead)
async def get_template(
    template_name: str,
    user: User = Depends(app_users.current_user()),
    db: AsyncSession = Depends(db_helper.session_dependency),
):
    """
    Вернуть шаблон по name, только если он принадлежит текущему пользователю.
    """
    tpl = await crud.get_template_by_name(db, owner_id=user.id, name=template_name)
    if not tpl:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Шаблон не найден")
    return tpl


@router.delete("/{template_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    template_name: str,
    user: User = Depends(app_users.current_user()),
    db: AsyncSession = Depends(db_helper.session_dependency),
):
    deleted = await crud.delete_template(db, owner_id=user.id, name=template_name)
    if not deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Шаблон не найден")
