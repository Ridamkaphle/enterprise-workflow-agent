"""LangGraph checkpoint persistence."""

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.config import settings


async def get_checkpointer() -> AsyncPostgresSaver:
    """Create a LangGraph Postgres checkpointer."""
    return AsyncPostgresSaver.from_conn_string(settings.database_url)
