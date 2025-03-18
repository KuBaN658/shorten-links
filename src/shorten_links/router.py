from datetime import datetime, timedelta, timezone
from typing import Optional, List

from fastapi import APIRouter, HTTPException, status, Depends, Response
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import ShortenLink
from src.database import get_async_session
from src.shorten_links.schemas import ShortenLinkCreate
from src.auth.user_manager import current_active_user, current_active_user_optional
from src.models import User
from src.shorten_links.utils import generate_alias
from src.shorten_links.schemas import Stats

router = APIRouter()

@router.post("/shorten")
async def create_shorten_link(
    shorten_link: ShortenLinkCreate,
    response: Response,
    current_user: Optional[User] = Depends(current_active_user_optional),
    session: AsyncSession = Depends(get_async_session),
):
    if shorten_link.alias == 'search':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Alias `search` is not allowed',
            )
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


@router.get("/search")
async def search_shorten_links(
    original_url: str,
    session: AsyncSession = Depends(get_async_session),
):
    if not original_url.startswith('http'):
        original_url = "https://" + original_url
    print(original_url)
    query = select(ShortenLink).where(ShortenLink.url == original_url)
    result = await session.execute(query)
    return result.scalars().all()


@router.get("/{short_code}")
async def redirect_to_original_url(
    short_code: str,
    session: AsyncSession = Depends(get_async_session),
):  
    query = select(ShortenLink).where(ShortenLink.alias == short_code)
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


@router.delete("/delete/{short_code}")
async def delete_shorten_link(
    short_code: str,
    response: Response,
    current_user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    query = select(ShortenLink).where(
        ShortenLink.alias == short_code
    )
    result = await session.execute(query)
    link = result.scalar_one_or_none()
    if link is None:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Link not found",
            )
    elif link.user_id != current_user.id:
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied",
            )
    else:
        await session.delete(link)
        await session.commit()
        return Response(
            status_code=status.HTTP_204_NO_CONTENT,
        )
    
@router.get("/{short_code}/stats")
async def get_shorten_link_stats(
    short_code: str,
    current_user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    query = select(ShortenLink).where(
        ShortenLink.alias == short_code
    )
    result = await session.execute(query)
    link = result.scalar_one_or_none()
    if link is None:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Link not found",
            )
    elif link.user_id != current_user.id:
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied",
            )
    else:
        return Stats(
            original_url=link.url,
            created_at=link.created_at,
            clicks=link.clicks,
            last_clicked_at=link.last_clicked_at
        )
    

async def is_alias_exists(session: AsyncSession, alias: str) -> bool:
    # Выполняем запрос для проверки существования alias
    query = select(ShortenLink).where(ShortenLink.alias == alias)
    result = await session.execute(query)
    return result.scalar() is not None  # Если запись найдена, возвращаем True
