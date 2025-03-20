import hashlib
import random

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import ShortenLink


def generate_alias(url: str) -> str:
    hash_object = hashlib.sha256(url.encode("utf-8"))
    alias = "".join(random.choices(hash_object.hexdigest(), k=8))
    return alias


async def get_link_by_short_code(session: AsyncSession, alias: str) -> bool:
    # Выполняем запрос для проверки существования alias
    query = select(ShortenLink).where(ShortenLink.alias == alias)
    result = await session.execute(query)
    return result.scalar_one_or_none()  # Если запись найдена, возвращаем True
