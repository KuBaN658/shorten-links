from datetime import datetime, timedelta, timezone
from sqlalchemy import insert
from celery import shared_task

from src.models import OldShortenLink
from src.database import get_async_session
from src.shorten_links.utils import get_link_by_short_code

@shared_task
def delete_link_if_expired(short_code: str):
    """
    Удаляет ссылку и добавляет её в таблицу OldShortenLink.
    """
    async def _delete_link():
        async with get_async_session() as session:
            # Получаем ссылку
            link = await get_link_by_short_code(session, short_code)
            if link is None:
                return  # Ссылка уже удалена

            now = datetime.now(timezone.utc).replace(tzinfo=None)
            if link.expires_at <= now or (link.last_clicked_at and (now - link.last_clicked_at) > timedelta(days=1)):
                # Копируем ссылку в OldShortenLink
                await session.execute(
                    insert(OldShortenLink).values(
                        id=link.id,
                        url=link.url,
                        alias=link.alias,
                        expires_at=link.expires_at,
                        user_id=link.user_id,
                        deleted_at=now,
                    )
                )

                # Удаляем ссылку из основной таблицы
                await session.delete(link)
                await session.commit()

    # Запускаем асинхронную функцию
    import asyncio
    asyncio.run(_delete_link())
