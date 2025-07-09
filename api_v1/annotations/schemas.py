from typing import Annotated
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime


class AnnotationCreate(BaseModel):
    option_index: Annotated[int, Field(ge=0, description="Индекс выбранного варианта")]
    custom_answer: Annotated[str | None, Field(default=None, description="Текст, если вариант custom")]
    comment: Annotated[str | None, Field(default=None, description="Комментарий аннотатора")]


class AnnotationRead(AnnotationCreate):
    id: Annotated[UUID, Field()]
    assignment_id: Annotated[UUID, Field()]
    created_at: Annotated[datetime, Field()]

    model_config = {"from_attributes": True}
