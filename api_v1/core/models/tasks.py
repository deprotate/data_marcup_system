from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api_v1.core.models.Base import Base


class Task(Base):
    """
    Конкретное задание:
      - шаблон (template_id)
      - content: готовый JSON по content_schema шаблона
      - created_by_id: внешний user_id
    """
    tid: Mapped[int] = mapped_column(primary_key=True, index=True)
    template_id: Mapped[int] = mapped_column(
        ForeignKey("tasktemplates.id", ondelete="CASCADE"),
        nullable=False
    )
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_by_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    template: Mapped["TaskTemplate"] = relationship(back_populates="tasks", lazy="joined")
    created_by_user: Mapped["User"] = relationship(back_populates="tasks")
    assignments: Mapped[list["Assignment"]] = relationship(back_populates="task")
