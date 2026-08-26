"""PostgreSQL connection and query utilities."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings


def get_async_database_url(database_url: str | None = None) -> str:
    """Convert a sync Postgres URL to the asyncpg driver form."""
    url = database_url or settings.database_url
    if url.startswith("postgresql+asyncpg://"):
        return url
    return url.replace("postgresql://", "postgresql+asyncpg://")


engine = create_async_engine(get_async_database_url())
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session for dependency injection."""
    async with SessionLocal() as session:
        yield session
