# api_v1/users/auth.py

from uuid import UUID
from fastapi import Depends
from fastapi_users import FastAPIUsers, BaseUserManager, schemas, exceptions
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.DBHelper import db_helper
from ..core.models.users import User  # ваш SQLAlchemy-модель
from .schemas import UserCreate, UserRead, UserUpdate

# 1. Transport — будем отдавать/принимать токены по Bearer
bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")

# 2. Strategy — как генерировать/валидация JWT
def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET, lifetime_seconds=3600)
    # lifetime_seconds — время жизни токена в секундах

# 3. Backend — «сочетание» transport + strategy :contentReference[oaicite:0]{index=0}
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# 4. User DB — адаптер SQLAlchemy → fastapi-users :contentReference[oaicite:1]{index=1}
async def get_user_db(session: AsyncSession = Depends(db_helper.session_dependency)):
    yield SQLAlchemyUserDatabase(session, User)

# 5. Менеджер пользователей — можно добавить валидацию пароля etc.
class UserManager(BaseUserManager[User, UUID]):
    reset_password_token_secret = settings.SECRET
    verification_token_secret   = settings.SECRET

    async def validate_password(self, password: str, user: User) -> None:
        if len(password) < 6:
            raise exceptions.InvalidPasswordException(
                "Пароль должен быть не менее 6 символов"
            )

get_user_manager = UserManager(get_user_db)

# 6. Инициализация FastAPIUsers
fastapi_users = FastAPIUsers[User, UUID](
    get_user_manager,
    [auth_backend],
    UserCreate,
    UserRead,
    UserUpdate,
)

# 7. Роутеры для подключения в main.py
auth_router = auth_backend.get_router(fastapi_users)            # /auth/jwt/login, /logout
register_router = fastapi_users.get_register_router()          # /auth/register
reset_pw_router = fastapi_users.get_reset_password_router()    # /auth/reset-password
verify_router   = fastapi_users.get_verify_router()            # /auth/verify
users_router    = fastapi_users.get_users_router()             # /users (CRUD для админов)
