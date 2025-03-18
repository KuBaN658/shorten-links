from fastapi import FastAPI, Depends

from src.auth.user_manager import (
    auth_backend,
    current_active_user,
    fastapi_users_router,
)
from src.auth.schemas import UserCreate, UserRead
from src.auth.models import User
from src.shorten_links.router import router


app = FastAPI()

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
