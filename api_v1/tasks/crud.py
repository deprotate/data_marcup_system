# app/crud/tasks.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Assignment, Annotation, Task
from app.db.session import get_session
from app.ai import ask_ai  # наша функция ИИ

async def pick_next_assignment(user_id: UUID, db: AsyncSession = Depends(get_session)) -> Assignment | None:
    # пример: берём первое свободное "new"
    stmt = (
        select(Assignment)
        .where(Assignment.user_id == user_id, Assignment.status == 'new')
        .order_by(Assignment.assigned_at)
        .limit(1)
        .with_for_update(skip_locked=True)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def generate_ai_suggestion(payload: dict) -> str:
    # здесь можно кэшировать или делать вызов внешнего сервиса
    return await ask_ai(payload)

async def store_submission(
    assignment_id: UUID,
    user_id: UUID,
    body: SubmitTaskRequest,
    db: AsyncSession = Depends(get_session),
) -> Annotation:
    # помечаем задание
    await db.execute(
        update(Assignment)
        .where(Assignment.id == assignment_id, Assignment.user_id == user_id)
        .values(status = 'done' if not body.skipped else 'skipped',
                completed_at = datetime.utcnow())
    )
    ann = Annotation(
        assignment_id=assignment_id,
        answer=body.answer,
        comment=body.comment
    )
    db.add(ann)
    await db.commit()
    return ann
