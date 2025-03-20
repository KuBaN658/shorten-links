from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from fastapi import FastAPI, Depends
from fastapi_cache import FastAPICache
from redis import asyncio as aioredis
from fastapi_cache.backends.redis import RedisBackend

from src.auth.user_manager import (
    auth_backend,
    current_active_user,
    fastapi_users_router,
)
from src.auth.schemas import UserCreate, UserRead
from src.auth.models import User
from src.shorten_links.router import router


@asynccontextmanager
async def lifespan(_: FastAPI):
    redis = aioredis.from_url(
        url="redis://localhost", encoding="utf-8", decode_responses=True
    )
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(
    fastapi_users_router.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users_router.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    router,
    prefix="/links",
    tags=["links"],
)


@app.get("/protected-route")
def protected_route(user: User = Depends(current_active_user)):
    return f"Hello, {user.email}"


@app.get("/unprotected-route")
def unprotected_route():
    return f"Hello, anonym"
