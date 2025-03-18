from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends, Response
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import ShortenLink
from src.database import get_async_session
from src.shorten_links.schemas import ShortenLinkCreate
from src.auth.user_manager import current_active_user
from src.models import User
from src.shorten_links.crud import add_shorten_link, get_shorten_link
from src.shorten_links.utils import generate_alias

router = APIRouter()

@router.post("/shorten")
async def shorten_link(
    shorten_link: ShortenLinkCreate,
    response: Response,
    current_user: Optional[User] = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    
    if shorten_link.alias is None:
        alias = generate_alias(shorten_link.url)
        while await is_alias_exists(session, shorten_link.alias):
            alias = generate_alias
        shorten_link.alias = alias
    
    else:
        if await is_alias_exists(session, shorten_link.alias):
            raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f'Alias: `{shorten_link.alias}` already exists',
                )
        
    if not shorten_link.url.startswith('http'):
        shorten_link.url = "https://" + shorten_link.url
    expires_at = (
        datetime.now(timezone.utc) + 
        timedelta(minutes=shorten_link.lifetime_minutes)
    )
    expires_at = expires_at.replace(tzinfo=None)
    user_id = current_user if current_user is None else current_user.id
    new_shorten_link = ShortenLink(
        url=shorten_link.url,
        alias=shorten_link.alias,
        expires_at=expires_at,
        user_id=user_id
    )
    session.add(new_shorten_link)
    await session.commit()
    await session.refresh(new_shorten_link)
    response.status_code = status.HTTP_201_CREATED
    return {
        "status": "Shorten_link created",
        "saved_link": new_shorten_link,
    }


@router.get("/{short_code}")
async def redirect_to_original_url(short_code: str):
    return await get_shorten_link(short_code)

async def is_alias_exists(session: AsyncSession, alias: str) -> bool:
    # Выполняем запрос для проверки существования alias
    query = select(ShortenLink).where(ShortenLink.alias == alias)
    result = await session.execute(query)
    return result.scalar() is not None  # Если запись найдена, возвращаем True
    
