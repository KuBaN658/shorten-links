from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Depends, Response
from fastapi.responses import RedirectResponse
from sqlalchemy import select, and_, insert
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_cache.decorator import cache
from celery.result import AsyncResult

from models import ShortenLink, OldShortenLink
from database import get_async_session
from shorten_links.schemas import ShortenLinkCreate, UrlUpdate
from auth.user_manager import current_active_user, current_active_user_optional
from models import User
from shorten_links.utils import generate_alias
from shorten_links.schemas import Stats
from shorten_links.utils import get_link_by_short_code
from celery_app.config_celery import delete_link_if_expired
from config import settings

router = APIRouter()


@router.post(
    "/shorten",
    description="""Создает короткую ссылку, для зарегистрированного 
            пользователя и для не зарегистрированного.
            Есть возможность указать кастомный alias. Параметр: alias.
            Есть возможность указать время жизни ссылки. Параметр: lifetime_hours.
            По умолчанию время жизни ссылки 24 часа. По истечении времени ссылка удаляется.
            Есть возможность указать проекта, которому принадлежит ссылка. Параметр: project.
            """,
)
async def create_shorten_link(
    shorten_link: ShortenLinkCreate,
    response: Response,
    current_user: Optional[User] = Depends(current_active_user_optional),
    session: AsyncSession = Depends(get_async_session),
):
    if shorten_link.alias == "search":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Alias `search` is not allowed",
        )
    if shorten_link.alias is None:
        alias = generate_alias(shorten_link.url)
        while await get_link_by_short_code(session, shorten_link.alias):
            alias = generate_alias
        shorten_link.alias = alias

    else:
        if await get_link_by_short_code(session, shorten_link.alias):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Alias: `{shorten_link.alias}` already exists",
            )

    if not shorten_link.url.startswith("http"):
        shorten_link.url = "https://" + shorten_link.url
    expires_at = datetime.now(timezone.utc) + timedelta(
        seconds=shorten_link.lifetime_seconds
    )
    expires_at = expires_at.replace(tzinfo=None)
    user_id = current_user if current_user is None else current_user.id

    delete_time = min(
        datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(seconds=settings.life_time_links.without_clicks),
        expires_at,
    )

    task = delete_link_if_expired.apply_async(
        args=[shorten_link.alias], eta=delete_time
    )

    new_shorten_link = ShortenLink(
        url=shorten_link.url,
        alias=shorten_link.alias,
        expires_at=expires_at,
        user_id=user_id,
        project=shorten_link.project,
        task_id=task.id,
    )

    session.add(new_shorten_link)
    await session.commit()
    await session.refresh(new_shorten_link)

    response.status_code = status.HTTP_201_CREATED
    return {
        "status": "Shorten_link created",
        "saved_link": new_shorten_link,
    }


@router.get("/search", description="Поиск всех коротких ссылок по оригинальному URL, результат кэшируется")
@cache(expire=60)
async def search_shorten_links(
    original_url: str,
    session: AsyncSession = Depends(get_async_session),
):
    if not original_url.startswith("http"):
        original_url = "https://" + original_url
    query = select(ShortenLink).where(ShortenLink.url == original_url)
    result = await session.execute(query)
    return result.scalars().all()


@router.get(
    "/{short_code}", description="Перенаправляет пользователя на оригинальный URL, результат кэшируется"
)
@cache(expire=60)
async def redirect_to_original_url(
    short_code: str,
    session: AsyncSession = Depends(get_async_session),
):
    link = await get_link_by_short_code(session, short_code)
    if link is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Link not found",
        )

    link.clicks += 1
    last_clicked_at = datetime.now(timezone.utc)
    last_clicked_at = last_clicked_at.replace(tzinfo=None)
    link.last_clicked_at = last_clicked_at

    delete_time = min(
        datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(seconds=settings.life_time_links.without_clicks),
        link.expires_at,
    )

    AsyncResult(link.task_id).revoke(terminate=True)

    task = delete_link_if_expired.apply_async(
        args=[link.alias], eta=delete_time
    )

    link.task_id = task.id
    await session.commit()
    await session.refresh(link)

    return RedirectResponse(link.url, status_code=307)


@router.put("/{short_code}", description="Обновляет URL")
async def update_shorten_link(
    short_code: str,
    update_link: UrlUpdate,
    current_user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    link = await get_link_by_short_code(session, short_code)
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
        if not update_link.url.startswith("http"):
            update_link.url = "https://" + update_link.url
        link.url = update_link.url
        await session.commit()
        await session.refresh(link)
        return {
            "detail": f"Link {short_code} updated",
            "updated_link": link,
        }


@router.delete("/delete/{short_code}", description="Удаляет короткую ссылку")
async def delete_shorten_link(
    short_code: str,
    current_user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    link = await get_link_by_short_code(session, short_code)
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
        await session.execute(
            insert(OldShortenLink).values(
                    url=link.url,
                    created_at=link.created_at,
                    alias=link.alias,
                    user_id=link.user_id,
                    deleted_at=datetime.now(timezone.utc).replace(tzinfo=None),
                )
            )
        AsyncResult(link.task_id).revoke(terminate=True)
        await session.delete(link)
        await session.commit()
        return Response(
            status_code=status.HTTP_204_NO_CONTENT,
        )


@router.get(
    "/{short_code}/stats",
    description="Получить статистику по короткой ссылке",
)
async def get_shorten_link_stats(
    short_code: str,
    current_user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):  
    link = await get_link_by_short_code(session, short_code)
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
            last_clicked_at=link.last_clicked_at,
        )


@router.get("/my/{project}", description="Получить все ссылки своего проекта")
async def get_links_by_project(
    project: str,
    current_user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    query = select(ShortenLink).where(
        and_(ShortenLink.project == project, ShortenLink.user_id == current_user.id)
    )
    result = await session.execute(query)
    links = result.scalars().all()
    if not links:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project not found",
        )
    return links


@router.get("/history/old_links", description="Получить все устаревшие ссылки")
async def get_old_links(
    current_user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session),
):
    query = select(OldShortenLink).where(
        and_(OldShortenLink.user_id == current_user.id, 
             OldShortenLink.user_id == current_user.id)
    )
    result = await session.execute(query)
    return result.scalars().all()
