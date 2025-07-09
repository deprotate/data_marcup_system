from typing import Annotated, Literal, Any
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class Option(BaseModel):
    label: Annotated[str, Field()]
    type: Annotated[Literal["fixed", "custom"], Field()]


class TaskTemplateCreate(BaseModel):
    name: Annotated[str, Field(description="Уникальный код шаблона")]
    title: Annotated[str, Field(description="Заголовок задания")]
    description: Annotated[str | None, Field(default=None, description="Текст условия")]
    content_schema: Annotated[dict[str, Any], Field(description="JSON‑схема для content")]
    options: Annotated[list[Option], Field(description="Список вариантов ответа")]


class TaskTemplateRead(TaskTemplateCreate):
    id: Annotated[UUID, Field()]
    owner_id: Annotated[UUID, Field(description="Кто создал шаблон")]
    created_at: Annotated[datetime, Field()]

    model_config = {"from_attributes": True}
