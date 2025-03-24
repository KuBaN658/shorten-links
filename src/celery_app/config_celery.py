from datetime import datetime, timezone
from sqlalchemy import insert, select
from celery import Celery
from loguru import logger

from models import OldShortenLink, ShortenLink
from database import session_maker
from config import settings

app = Celery(
    "tasks",  # Имя приложения
    broker=f"redis://{settings.redis.tasks_host}:6379/0",
    backend=f"redis://{settings.redis.tasks_host}:6379/1",
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
    with session_maker() as session:
        # Получаем ссылку
        query = select(ShortenLink).where(ShortenLink.alias == short_code)
        link = session.execute(query).scalar_one_or_none()
        if link is None:
            return  # Ссылка уже удалена

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        # Копируем ссылку в OldShortenLink
        session.execute(
            insert(OldShortenLink).values(
                url=link.url,
                created_at=link.created_at,
                alias=link.alias,
                user_id=link.user_id,
                deleted_at=now,
                clicks=link.clicks,
                last_clicked_at=link.last_clicked_at,
                project=link.project,
            )
        )

        # Удаляем ссылку из основной таблицы
        session.delete(link)
        session.commit()
        logger.info("Ссылка удалена")
