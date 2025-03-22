from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from fastapi import FastAPI, Depends
from fastapi_cache import FastAPICache
from redis import asyncio as aioredis
from fastapi_cache.backends.redis import RedisBackend
import uvicorn

from auth.user_manager import (
    auth_backend,
    current_active_user,
    fastapi_users_router,
)
from auth.schemas import UserCreate, UserRead
from models import User
from shorten_links.router import router


@asynccontextmanager
async def lifespan(_: FastAPI):
    redis_app = aioredis.Redis(
        host="localhost", 
        port=6379,
        encoding="utf-8", 
        decode_responses=True,
        db=0
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


@app.get("/protected-route")
def protected_route(user: User = Depends(current_active_user)):
    return f"Hello, {user.email}"


@app.get("/unprotected-route")
def unprotected_route():
    return f"Hello, anonym"

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        log_level="info",
        reload=True,
    )
