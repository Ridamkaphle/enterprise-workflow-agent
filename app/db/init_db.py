"""Create or drop database tables."""

import asyncio

from app.db.base import Base
from app.db.postgres import engine

# Import models so SQLAlchemy registers them with Base.metadata.
from app.db import models  # noqa: F401


async def create_tables() -> None:
    """Create all tables defined in models if they do not exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables() -> None:
    """Drop all tables. Intended for tests only."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def main() -> None:
    """CLI entry point: python -m app.db.init_db"""
    asyncio.run(create_tables())
    print("Database tables created.")


if __name__ == "__main__":
    main()
