from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.config import settings

DATABASE_URL = f"postgresql+asyncpg://{settings.db.user}:{settings.db.password}@"
DATABASE_URL += f"{settings.db.host}:{settings.db.port}/{settings.db.name}"

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
