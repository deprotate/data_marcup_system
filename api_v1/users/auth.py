from uuid import UUID
from fastapi import Depends
from fastapi_users import FastAPIUsers, BaseUserManager, exceptions
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.DBHelper import db_helper
from ..core.models.users import User
from .schemas import UserCreate, UserRead, UserUpdate

# 1) Transport — Bearer-токен
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

# 2) JWT-стратегия
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET, lifetime_seconds=3600)

# 3) АутenticationBackend
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# 4) БД‑адаптер
async def get_user_db(session: AsyncSession = Depends(db_helper.session_dependency)):
    yield SQLAlchemyUserDatabase(session, User)

# 5) Менеджер — **функция**, а не сразу объект!
class UserManager(BaseUserManager[User, UUID]):
    reset_password_token_secret = settings.SECRET
    verification_token_secret   = settings.SECRET

    async def validate_password(self, password: str, user: User) -> None:
        if len(password) < 6:
            raise exceptions.InvalidPasswordException(
                "Пароль должен быть не менее 6 символов"
            )

# **Вот здесь** возвращаем сам класс UserManager как зависимость
async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)

app_users = FastAPIUsers[User, UUID](
    get_user_manager,
    [auth_backend],
)


auth_router     = app_users.get_auth_router(auth_backend)
register_router = app_users.get_register_router(UserRead, UserCreate)
reset_pw_router = app_users.get_reset_password_router()
verify_router   = app_users.get_verify_router(UserRead)
users_router    = app_users.get_users_router(UserRead, UserUpdate)