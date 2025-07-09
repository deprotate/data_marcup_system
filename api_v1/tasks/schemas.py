from typing import Annotated, Any
from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime

class TaskCreate(BaseModel):
    template_name:  Annotated[str, Field( description="Код шаблона, из которого берём content_schema") ]
    content:        Annotated[dict[str, Any], Field(description="Заполненный JSON по content_schema") ]

class TaskRead(BaseModel):
    id:             Annotated[UUID, Field() ]
    template_name:  Annotated[str, Field() ]
    content:        Annotated[dict[str, Any], Field() ]
    created_by_id:  Annotated[UUID | None, Field(default=None) ]
    created_at:     Annotated[datetime, Field() ]

    model_config = {"from_attributes": True}
