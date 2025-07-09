from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api_v1.core.models.Base import Base
from api_v1.core.models.assignments import Assignment
from api_v1.core.models.task_templates import TaskTemplate
from api_v1.core.models.users import User


class Task(Base):
    """
    Конкретное задание:
      - шаблон (template_id)
      - content: готовый JSON по content_schema шаблона
      - created_by_id: внешний user_id
    """
    template_id:    Mapped[int]  = mapped_column(
        ForeignKey("tasktemplates.id", ondelete="CASCADE"),
        nullable=False
    )
    content:        Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_by:     Mapped[int]  = mapped_column(nullable=True)  # привязка к внешнему user.id
    created_at:     Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    template:       Mapped[TaskTemplate] = relationship(back_populates="tasks", lazy="joined")
    assignments:    Mapped[list[Assignment]] = relationship(back_populates="task")

    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_by: Mapped[User] = relationship(back_populates="tasks")