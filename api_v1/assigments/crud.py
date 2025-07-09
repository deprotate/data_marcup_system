from sqlalchemy import select, and_, not_, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..core.models.assignments import Assignment
from ..core.models.tasks import Task
from ..core.models.task_templates import TaskTemplate
from ..core.ai import get_ai_suggestion  # ваша stub-функция

async def get_next_assignment(db: AsyncSession, user_id: int):
    # 1) ищем уже созданные новые
    q = await db.execute(
        select(Assignment)
        .where(Assignment.user_id == user_id, Assignment.status == "new")
        .join(Assignment.task)
        .options(joinedload(Assignment.task).joinedload(Task.template))
    )
    assignment = q.scalars().first()
    if assignment:
        return format_assignment(assignment)

    # 2) создаём новый
    # 2.1) найти Task, не созданный этим user, и не в assignments
    subq = select(Assignment.task_id).where(Assignment.user_id == user_id)
    q2 = await db.execute(
        select(Task, TaskTemplate)
        .join(TaskTemplate, Task.template_id == TaskTemplate.id)
        .where(
            Task.created_by_id != user_id,
            not_(Task.id.in_(subq))
        )
        .order_by(Task.created_at)
        .limit(1)
    )
    row = q2.first()
    if not row:
        return None

    task, template = row
    # 2.2) создать Assignment
    new_a = Assignment(task_id=task.id, user_id=user_id)
    db.add(new_a)
    await db.flush()  # чтобы new_a.id появился

    # 2.3) получить AI-подсказку
    ai = await get_ai_suggestion(task.content)
    new_a.ai_suggestion = ai
    await db.commit()
    await db.refresh(new_a)

    # 2.4) подгрузить связи для ответа
    await db.refresh(new_a, attribute_names=["task", "task.template"])
    return format_assignment(new_a)

def format_assignment(assignment: Assignment) -> NextAssignmentResponse:
    return NextAssignmentResponse(
        assignment_id=assignment.id,
        task_id=assignment.task.id,
        template_name=assignment.task.template.name,
        content=assignment.task.content,
        options=assignment.task.template.options,
        ai_suggestion=assignment.ai_suggestion,
    )
