import uuid
from typing import Optional

from loguru import logger
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, models
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users.db import SQLAlchemyUserDatabase

from models import User, get_user_db
from config import settings

logger.add("logs/auth.log", rotation="10 MB", compression="zip")


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = settings.access_token.reset_password_token_secret
    verification_token_secret = settings.access_token.verification_token_secret

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        logger.info("User %s has registered." % user.id)


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy[models.UP, models.ID]:
    return JWTStrategy(
        secret=settings.access_token.verification_token_secret,
        lifetime_seconds=3600,
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users_router = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

current_active_user_optional = fastapi_users_router.current_user(
    active=True, optional=True
)
current_active_user = fastapi_users_router.current_user(active=True)
