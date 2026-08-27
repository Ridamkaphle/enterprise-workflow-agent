"""PostgreSQL connection and query utilities."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import settings


def get_async_database_url(database_url: str | None = None) -> str:
    """Convert a sync Postgres URL to the asyncpg driver form."""
    url = database_url or settings.database_url
    if url.startswith("postgresql+asyncpg://"):
        return url
    return url.replace("postgresql://", "postgresql+asyncpg://")


# NullPool: asyncpg connections are bound to the event loop that created
# them, and a pooled connection reused from a different loop than the one
# it was opened on raises "attached to a different loop". That happens in
# practice as soon as more than one asyncio loop touches this process (the
# LangGraph checkpointer's own loop, or — in tests — pytest-asyncio's loop
# vs. the separate loop TestClient's portal thread runs the app on). Every
# call opens a fresh connection instead of reusing a pooled one.
engine = create_async_engine(get_async_database_url(), poolclass=NullPool)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session for dependency injection."""
    async with SessionLocal() as session:
        yield session
