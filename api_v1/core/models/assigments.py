from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, Enum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api_v1.core.models.Base import Base


class Assignment(Base):
    """
    Назначение задачи пользователю:
      - task_id, user_id (внешний)
      - status: new/in_progress/done/skipped
      - ai_suggestion: подсказываем моделью
    """
    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False
    )
    user_id: Mapped[int] = mapped_column(nullable=False)  # внешний user.id
    status: Mapped[str] = mapped_column(
        Enum("new", "in_progress", "done", "skipped", name="assign_status"),
        nullable=False, server_default="new"
    )
    ai_suggestion: Mapped[str | None] = mapped_column(nullable=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)

    task: Mapped["Task"] = relationship(back_populates="assignments")
    annotations: Mapped[list["Annotation"]] = relationship(back_populates="assignment")
