from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, relationship, mapped_column
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from api_v1.core.models.Base import AuthBase


class User(SQLAlchemyBaseUserTableUUID, AuthBase):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    # email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    # hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    templates: Mapped[list["TaskTemplate"]] = relationship(
        "TaskTemplate",
        back_populates="owner",
        primaryjoin="User.id == TaskTemplate.owner_id",
        lazy="joined",
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="created_by_user",
        primaryjoin="User.id == Task.created_by_id",
        lazy="joined",
    )