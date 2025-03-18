from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from fastapi.responses import RedirectResponse

from src.database import get_async_session
from src.shorten_links.utils import generate_alias
from src.shorten_links.schemas import ShortenLinkCreate
from src.models import ShortenLink
from src.database import async_session_maker


async def add_shorten_link(shorten_link: ShortenLinkCreate):
    async with async_session_maker() as session:
        if shorten_link.alias is None:
            alias = generate_alias(shorten_link.url)
            while await is_alias_exists(session, alias):
                alias = generate_alias(shorten_link.url)
            shorten_link.alias = alias
        else:
            if await is_alias_exists(session, shorten_link.alias):
                return HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f'Alias: `{shorten_link.alias}` already exists',
                )
            
        if not shorten_link.url.startswith('http'):
            shorten_link.url = 'https://' + shorten_link.url 
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=shorten_link.lifetime_minutes)
        expires_at = expires_at.replace(tzinfo=None)
        new_shorten_link = ShortenLink(
            url=shorten_link.url,
            alias=shorten_link.alias,
            expires_at=expires_at,
        )
        session.add(new_shorten_link)
        await session.commit()

        return {
            "status": "ok",
            "shorten_link": new_shorten_link.shorten_link,
        }
    
async def get_shorten_link(short_code: str):
    async with async_session_maker() as session:
        query = select(ShortenLink).where(ShortenLink.shorten_link == short_code)
        result = await session.execute(query)
        link = result.scalar_one_or_none()
        if link is None:
            raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Link not found",
                )

        link.clicks += 1
        last_clicked_at = datetime.now(timezone.utc)
        last_clicked_at = last_clicked_at.replace(tzinfo=None)
        link.last_clicked_at = last_clicked_at
        await session.commit()
        return RedirectResponse(link.url, status_code=307)     


async def is_alias_exists(session: AsyncSession, alias: str) -> bool:
    # Выполняем запрос для проверки существования alias
    query = select(ShortenLink).where(ShortenLink.shorten_link == alias)
    result = await session.execute(query)
    return result.scalar() is not None  # Если запись найдена, возвращаем True
