from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..core.models.task_templates import TaskTemplate
from ..core.models.tasks import Task
from ..core.models.assignments import Assignment

async def get_overall_counts(db: AsyncSession, owner_id: str) -> dict:
    # 1) Шаблоны
    total_templates = await db.scalar(
        select(func.count())
        .select_from(TaskTemplate)
        .where(TaskTemplate.owner_id == owner_id)
    )
    # 2) Задачи
    total_tasks = await db.scalar(
        select(func.count())
        .select_from(Task)
        .where(Task.created_by_id == owner_id)
    )
    # 3) Назначения по этим задачам
    subq = select(Task.id).where(Task.created_by_id == owner_id)
    total_assignments = await db.scalar(
        select(func.count())
        .select_from(Assignment)
        .where(Assignment.task_id.in_(subq))
    )
    completed = await db.scalar(
        select(func.count())
        .select_from(Assignment)
        .where(Assignment.task_id.in_(subq), Assignment.status == "done")
    )
    skipped = await db.scalar(
        select(func.count())
        .select_from(Assignment)
        .where(Assignment.task_id.in_(subq), Assignment.status == "skipped")
    )

    return {
        "total_templates":    total_templates,
        "total_tasks":        total_tasks,
        "total_assignments":  total_assignments,
        "completed":          completed,
        "skipped":            skipped,
    }


async def get_per_template_stats(db: AsyncSession, owner_id: str) -> list[dict]:
    # вытаскиваем все шаблоны с их задачами и assignments
    q = await db.execute(
        select(TaskTemplate)
        .where(TaskTemplate.owner_id == owner_id)
        .options(
            joinedload(TaskTemplate.tasks)
            .joinedload(Task.assignments)
        )
    )
    templates = q.scalars().all()

    result = []
    for tpl in templates:
        tasks = tpl.tasks
        tasks_created = len(tasks)
        total_assignments = sum(len(t.assignments) for t in tasks)
        completed = sum(
            1 for t in tasks for a in t.assignments if a.status == "done"
        )
        skipped = sum(
            1 for t in tasks for a in t.assignments if a.status == "skipped"
        )
        result.append({
            "template_id":      tpl.id,
            "template_name":    tpl.name,
            "tasks_created":    tasks_created,
            "total_assignments": total_assignments,
            "completed":        completed,
            "skipped":          skipped,
        })
    return result
