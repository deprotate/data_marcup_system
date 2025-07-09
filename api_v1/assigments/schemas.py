from typing import Annotated, Any, Literal
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class NextAssignmentResponse(BaseModel):
    assignment_id:  Annotated[UUID, Field() ]
    task_id:        Annotated[UUID, Field() ]
    template_name:  Annotated[str, Field() ]
    content:        Annotated[dict[str, Any], Field() ]
    options:        Annotated[list[dict[str, Any]], Field() ]  # можно заменить на List[Option] из TaskTemplate
    ai_suggestion:  Annotated[str | None, Field(default=None) ]

    model_config = {"from_attributes": True}

class AssignmentStatus(BaseModel):
    status:         Annotated[Literal["new","in_progress","done","skipped"], Field() ]
    ai_suggestion:  Annotated[str | None, Field(default=None) ]
    answer:         Annotated[int | None, Field(default=None, description="Индекс варианта ответа") ]
    custom_answer:  Annotated[str | None, Field(default=None) ]
    comment:        Annotated[str | None, Field(default=None) ]

    model_config = {"from_attributes": True}
