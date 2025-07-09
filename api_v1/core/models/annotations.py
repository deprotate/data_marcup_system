from datetime import datetime
from sqlalchemy import ForeignKey, DateTime, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api_v1.core.models.Base import Base
from api_v1.core.models.assignments import Assignment


class Annotation(Base):
    """
    Результат размеченного задания:
      - assignment_id
      - option_index: int (номер выбранного варианта)
      - custom_answer: текст, если вариант type="custom"
      - comment
    """
    assignment_id: Mapped[int] = mapped_column(
        ForeignKey("assignments.id", ondelete="CASCADE"),
        nullable=False
    )
    option_index: Mapped[int] = mapped_column(nullable=False)
    custom_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    assignment: Mapped[Assignment] = relationship(back_populates="annotations")
