"""Shared pytest fixtures."""

from collections.abc import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.init_db import create_tables
from app.db.postgres import SessionLocal, engine
from app.main import app
from app.mcp import registry


@pytest.fixture(autouse=True)
def _clean_mcp_registry() -> Generator[None, None, None]:
    """Tools are registered into a shared module-level dict; keep tests isolated."""
    registry._REGISTRY.clear()
    yield
    registry._REGISTRY.clear()


@pytest.fixture
def client() -> TestClient:
    """FastAPI test client, without the lifespan (no DB/checkpointer) started."""
    return TestClient(app)


async def _require_postgres() -> None:
    try:
        async with engine.connect() as connection:
            await connection.close()
        await create_tables()
    except Exception as exc:
        pytest.skip(f"Postgres not available. Start it with: docker compose up -d postgres ({exc})")


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session. Skips test if Postgres is not running."""
    await _require_postgres()

    async with SessionLocal() as session:
        yield session


@pytest.fixture
async def app_client() -> AsyncGenerator[TestClient, None]:
    """Full app client with the lifespan running (compiled graph + Postgres checkpointer).

    Skips the test if Postgres is not running, same as `db_session`.
    """
    await _require_postgres()

    with TestClient(app) as test_client:
        yield test_client
