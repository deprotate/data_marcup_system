from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api_v1.core.models.Base import Base


class TaskTemplate(Base):
    """
    Один шаблон:
      - title: заголовок
      - description: текстовое условие
      - content_schema: JSON‑схема для основного блока (текст, запрос + выдача или картинки)
      - options: список вариантов ответа [{ "label": str, "type": "fixed"|"custom" }]
    """
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    content_schema: Mapped[dict] = mapped_column(JSONB, nullable=False)
    options: Mapped[list] = mapped_column(JSONB, nullable=False)

    # связь к задачам
    tasks: Mapped[list["Task"]] = relationship(back_populates="template")
