"""Shared pytest fixtures."""

from collections.abc import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.init_db import create_tables
from app.db.postgres import SessionLocal, engine
from app.main import app


@pytest.fixture
def client() -> TestClient:
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session. Skips test if Postgres is not running."""
    try:
        async with engine.connect() as connection:
            await connection.close()
        await create_tables()
    except Exception as exc:
        pytest.skip(f"Postgres not available. Start it with: docker compose up -d postgres ({exc})")

    async with SessionLocal() as session:
        yield session
