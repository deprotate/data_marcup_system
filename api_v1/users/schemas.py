from uuid import UUID

from fastapi_users import schemas

class UserRead(schemas.BaseUser[UUID]):
    username: str | None

class UserCreate(schemas.BaseUserCreate):
    username: str  # требуем username при регистрации

class UserUpdate(schemas.BaseUserUpdate):
    username: str | None
