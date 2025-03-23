from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import settings


DATABASE_URL = f"postgresql+asyncpg://{settings.db.user}:{settings.db.password}@"
DATABASE_URL += f"{settings.db.host}:{settings.db.port}/{settings.db.name}"

async_engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)

DATABASE_URL = f"postgresql+psycopg2://{settings.db.user}:{settings.db.password}@{settings.db.host}:{settings.db.port}/{settings.db.name}"
sync_engine = create_engine(DATABASE_URL)
session_maker = sessionmaker(sync_engine)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
