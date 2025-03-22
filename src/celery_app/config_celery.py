import asyncio
from datetime import datetime, timedelta, timezone
from sqlalchemy import insert
from celery import Celery
from loguru import logger

from models import OldShortenLink
from database import async_session_maker
from shorten_links.utils import get_link_by_short_code
from config import settings

app = Celery(
    "tasks",  # Имя приложения
    broker=f"redis://{settings.redis.tasks_host}:6379/0", 
    backend=f"redis://{settings.redis.tasks_host}:6379/0",
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@app.task(
    name="delete_link_if_expired",
    soft_time_limit=30,
    time_limit=300,
)
def delete_link_if_expired(short_code: str):
    """
    Удаляет ссылку и добавляет её в таблицу OldShortenLink.
    """

    async def _delete_link():
        async with async_session_maker() as session:
            # Получаем ссылку
            logger.info("Получаем ссылку")
            link = await get_link_by_short_code(session, short_code)
            if link is None:
                logger.info("Ссылка не найдена")
                return  # Ссылка уже удалена

            now = datetime.now(timezone.utc).replace(tzinfo=None)
            logger.info(f"текущее время: {now}")
            if link.expires_at <= now or (
                link.last_clicked_at
                and (now - link.last_clicked_at)
                > timedelta(seconds=settings.life_time_links.without_clicks)
            ):
                logger.info(f"ссылка просрочена: {link.expires_at}")
                # Копируем ссылку в OldShortenLink
                await session.execute(
                    insert(OldShortenLink).values(
                        url=link.url,
                        created_at=link.created_at,
                        alias=link.alias,
                        user_id=link.user_id,
                        deleted_at=now,
                    )
                )
                logger.info("Ссылка удалена")
                # Удаляем ссылку из основной таблицы
                await session.delete(link)
                await session.commit()

    asyncio.run(_delete_link())
