from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi_cache import FastAPICache
from redis import asyncio as aioredis
from fastapi_cache.backends.redis import RedisBackend

from auth.user_manager import (
    auth_backend,
    current_active_user,
    fastapi_users_router,
)
from auth.schemas import UserCreate, UserRead
from models import User
from shorten_links.router import router
from config import settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    redis_app = aioredis.Redis(
        host=settings.redis.cache_host,
        port=6379,
        encoding="utf-8",
        decode_responses=True,
        db=0,
    )
    FastAPICache.init(RedisBackend(redis_app), prefix="fastapi-cache")

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
