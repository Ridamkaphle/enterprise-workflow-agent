"""LangGraph checkpoint persistence."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.config import settings


def get_checkpoint_conn_string() -> str:
    """Return a psycopg-compatible connection string for the checkpointer.

    `settings.database_url` is written for SQLAlchemy's asyncpg driver
    (`postgresql+asyncpg://...`); the LangGraph Postgres saver uses psycopg
    directly and expects the plain `postgresql://` scheme.
    """
    return settings.database_url.replace("postgresql+asyncpg://", "postgresql://")


@asynccontextmanager
async def get_checkpointer() -> AsyncIterator[AsyncPostgresSaver]:
    """Yield a LangGraph Postgres checkpointer, ensuring its tables exist."""
    async with AsyncPostgresSaver.from_conn_string(get_checkpoint_conn_string()) as checkpointer:
        await checkpointer.setup()
        yield checkpointer
