from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, relationship, mapped_column
from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from api_v1.core.models.Base import AuthBase


class User(SQLAlchemyBaseUserTableUUID, AuthBase):
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    # email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    # hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    templates: Mapped[list['TaskTemplate']] = relationship(back_populates="owner")
    tasks: Mapped[list['Task']] = relationship(back_populates="created_by_user")
