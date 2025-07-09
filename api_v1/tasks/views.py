# app/api/tasks.py
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from app.schemas.task_schemas import NextTaskResponse, SubmitTaskRequest, SubmitTaskResponse
from app.crud.tasks import (
    pick_next_assignment,
    store_submission,
    generate_ai_suggestion,
)
from app.core.auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.get("/next", response_model=NextTaskResponse)
async def get_next_task(user = Depends(get_current_user)):
    """
    Берём из очереди next assignment.
    Сразу рассчитываем ai_suggestion (медленно) или возвращаем None и запускаем background.
    """
    assignment = await pick_next_assignment(user.id)
    if not assignment:
        raise HTTPException(404, "Задания закончились")
    # вариант: сразу получить подсказку синхронно
    ai_text = await generate_ai_suggestion(assignment.task.payload)
    return NextTaskResponse(
        assignment_id=assignment.id,
        task_id=assignment.task.id,
        type=assignment.task.type.name,
        payload=assignment.task.payload,
        ai_suggestion=ai_text,
    )

@router.post("/{assignment_id}/submit", response_model=SubmitTaskResponse)
async def submit_task(
    assignment_id: UUID,
    body: SubmitTaskRequest,
    background_tasks: BackgroundTasks,
    user = Depends(get_current_user),
):
    """
    Сохраняем ответ, помечаем задание как done/skipped.
    В background можно сразу запустить recompute AI для следующего задания.
    """
    submission = await store_submission(assignment_id, user.id, body)
    # опционально – в фоне запускаем предзапуск AI для следующего
    background_tasks.add_task(_warmup_next_ai, submission.task_id)
    # можно сразу вернуть следующую команду
    next_asg = await pick_next_assignment(user.id)
    next_resp = (await get_next_task(user)) if next_asg else None
    return SubmitTaskResponse(status="ok", next_assignment=next_resp)

async def _warmup_next_ai(task_id: UUID):
    # здесь просто вызываем нашу функцию ИИ без await, чтобы кешировать модель
    await generate_ai_suggestion_by_task_id(task_id)
