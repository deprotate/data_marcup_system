from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from uuid import UUID

from ..annotations.schemas import AnnotationCreate
from ..core.models.tasks import Task
from ..core.models.task_templates import TaskTemplate
from ..core.models.assignments import Assignment
from ..core.models.annotations import Annotation


async def find_or_create_assignment_for_user(
    db: AsyncSession,
    user_id: UUID,
) -> dict | None:
    """
    1) Поищем уже выданное (new/in_progress) задание для user_id.
    2) Если нет — найдём первый Task без Assignment для этого user_id и создадим его.
    3) Вернём dict с полями для NextAssignmentResponse.
    """
    # 1) Существует ли назначение в работе?
    q = await db.execute(
        select(Assignment)
        .where(
            Assignment.user_id == user_id,
            Assignment.status.in_(["new", "in_progress"])
        )
        .order_by(Assignment.assigned_at)
        .options(joinedload(Assignment.task).joinedload(Task.template))
    )
    assignment = q.scalars().first()

    # 2) Если не найдено — создадим
    if assignment is None:
        # подзапрос: все task_id, что уже получал этот пользователь
        subq = select(Assignment.task_id).where(Assignment.user_id == user_id)
        q2 = await db.execute(
            select(Task)
            .where(~Task.id.in_(subq))
            .order_by(Task.created_at)
            .options(joinedload(Task.template))
        )
        task = q2.scalars().first()
        if task is None:
            return None

        assignment = Assignment(task_id=task.id, user_id=user_id)
        db.add(assignment)
        await db.commit()
        await db.refresh(assignment)
        # заново подгружаем связь task + template
        await db.refresh(assignment, attribute_names=["task"])
        await db.refresh(assignment.task, attribute_names=["template"])

    # 3) Собираем ответ
    tpl: TaskTemplate = assignment.task.template
    return {
        "assignment_id": assignment.id,
        "task_id":       assignment.task.id,
        "template_name": tpl.name,
        "content":       assignment.task.content,
        "options":       tpl.options,
        "ai_suggestion": assignment.ai_suggestion,
    }


async def submit_annotation(
    db: AsyncSession,
    assignment_id: UUID,
    user_id: UUID,
    data: AnnotationCreate,
) -> None:
    """
    1) Проверить, что такое Assignment существует и принадлежит user_id.
    2) Убедиться, что он ещё не выполнен.
    3) Проверить корректность option_index (диапазон и custom_answer).
    4) Сохранить Annotation и обновить статус Assignment → done.
    """
    # 1)
    q = await db.execute(
        select(Assignment)
        .where(
            Assignment.id == assignment_id,
            Assignment.user_id == user_id
        )
        .options(joinedload(Assignment.task).joinedload(Task.template))
    )
    assignment = q.scalars().first()
    if assignment is None:
        raise ValueError("Assignment не найден или не принадлежит пользователю")
    # 2)
    if assignment.status == "done":
        raise ValueError("Assignment уже завершён")

    # 3) Валидация варианта
    tpl: TaskTemplate = assignment.task.template
    opts = tpl.options
    idx = data.option_index
    if idx < 0 or idx >= len(opts):
        raise ValueError(f"option_index {idx} вне диапазона [0..{len(opts)-1}]")
    if opts[idx]["type"] == "custom" and not data.custom_answer:
        raise ValueError("Для варианта custom необходимо поле custom_answer")

    # 4) Сохраняем аннотацию
    ann = Annotation(
        assignment_id=assignment_id,
        option_index=idx,
        custom_answer=data.custom_answer,
        comment=data.comment,
    )
    db.add(ann)

    # обновляем статус задания
    assignment.status = "done"
    assignment.completed_at = func.now()

    await db.commit()


async def get_assignment_status(
    db: AsyncSession,
    assignment_id: UUID,
    user_id: UUID,
) -> dict | None:
    """
    Вернуть status, ai_suggestion и данные аннотации (если есть).
    """
    q = await db.execute(
        select(Assignment)
        .where(
            Assignment.id == assignment_id,
            Assignment.user_id == user_id
        )
        .options(joinedload(Assignment.annotations))
    )
    assignment = q.scalars().first()
    if assignment is None:
        return None

    # берём первую аннотацию (cross-check будет позже)
    ann = assignment.annotations[0] if assignment.annotations else None

    return {
        "status":         assignment.status,
        "ai_suggestion":  assignment.ai_suggestion,
        "answer":         ann.option_index if ann else None,
        "custom_answer":  ann.custom_answer if ann else None,
        "comment":        ann.comment if ann else None,
    }
