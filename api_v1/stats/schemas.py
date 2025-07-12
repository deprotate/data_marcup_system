from pydantic import BaseModel, Field
from typing import Literal, Annotated
from uuid import UUID


class OverallStats(BaseModel):
    total_templates: Annotated[int, Field(description="Всего шаблонов у пользователя")]
    total_tasks: Annotated[int, Field(description="Всего создано задач")]
    total_assignments: Annotated[int, Field(description="Всего назначений")]
    completed: Annotated[int, Field(description="Сколько из них выполнено")]
    skipped: Annotated[int, Field(description="Сколько пропущено")]

class TemplateStatsItem(BaseModel):
    template_id:   UUID
    template_name: str
    tasks_created: int
    total_assignments: int
    completed:     int
    skipped:       int

class TemplateStats(BaseModel):
    templates: list[TemplateStatsItem]
