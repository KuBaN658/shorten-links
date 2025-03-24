import hashlib
import random
from fastapi_cache import FastAPICache
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import ShortenLink


def generate_alias(url: str) -> str:
    hash_object = hashlib.sha256(url.encode("utf-8"))
    alias = "".join(random.choices(hash_object.hexdigest(), k=8))
    return alias


async def get_link_by_short_code(session: AsyncSession, alias: str) -> bool:
    # Выполняем запрос для проверки существования alias
    query = select(ShortenLink).where(ShortenLink.alias == alias)
    result = await session.execute(query)
    return result.scalar_one_or_none()  # Если запись найдена, возвращаем True


async def delete_cache(link: ShortenLink):
    redis = FastAPICache.get_backend().redis
    key_cache = f"short_links_cache:/links/search?original_url={link.url}"
    await redis.delete(key_cache)
    key_cache = f"short_links_cache:/links/{link.alias}?"
    await redis.delete(key_cache)
