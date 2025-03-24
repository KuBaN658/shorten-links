from typing import AsyncIterator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from redis import asyncio as aioredis
from fastapi_cache.backends.redis import RedisBackend

from auth.user_manager import (
    auth_backend,
    fastapi_users_router,
)
from auth.schemas import UserCreate, UserRead
from shorten_links.router import router
from config import settings


def custom_key_builder(func, namespace, request, response=None, args=None, kwargs=None):
    return f"short_links_cache:{request.url.path}?{request.url.query}"


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    # Инициализация кэша в redis
    redis = aioredis.from_url(f"redis://{settings.redis.cache_host}:6379")
    FastAPICache.init(
        RedisBackend(redis),
        key_builder=custom_key_builder,
    )
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


@app.get("/health")
def check_health():
    return {"status": "ok"}
