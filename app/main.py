"""FastAPI application entry point."""

import asyncio
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

if sys.platform == "win32":
    # psycopg's async driver (used by the LangGraph Postgres checkpointer,
    # see app/db/checkpoint.py) cannot run on the default Windows
    # ProactorEventLoop. This must run before *any* event loop is created.
    # It's early enough for pytest, which imports this module (via
    # tests/conftest.py) well before pytest-asyncio creates a loop per
    # test. It is NOT early enough for `uvicorn app.main:app` from the
    # CLI — uvicorn creates its loop via asyncio.run() before it lazily
    # imports the app string — so local dev on Windows must run this
    # module directly (`python -m app.main`, see the `__main__` block
    # below) rather than the `uvicorn` CLI. Irrelevant in Docker (Linux).
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.agent.graph import build_workflow_graph
from app.api import approvals, workflows
from app.db.checkpoint import get_checkpointer
from app.mcp.tools import register_mock_tools
from app.observability.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Wire up logging, mock tool registration, and the compiled workflow graph."""
    setup_logging()
    register_mock_tools()

    async with get_checkpointer() as checkpointer:
        app.state.graph = build_workflow_graph(checkpointer=checkpointer)
        yield


app = FastAPI(
    title="Enterprise Workflow Agent",
    description="Distributed agentic platform for enterprise workflow orchestration.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(workflows.router)
app.include_router(approvals.router)


if __name__ == "__main__":
    # `python -m app.main` — see the Windows event-loop note above. Setting
    # the process-wide policy isn't enough on its own: uvicorn's "auto"/
    # "asyncio" loop options hardcode `asyncio.ProactorEventLoop` as an
    # explicit loop_factory on win32 (uvicorn/loops/asyncio.py), which
    # bypasses the event loop policy entirely. Pointing `loop` at
    # `asyncio.SelectorEventLoop` directly (not one of uvicorn's reserved
    # loop names) sidesteps that.
    import uvicorn

    loop = "asyncio:SelectorEventLoop" if sys.platform == "win32" else "auto"
    uvicorn.run(app, host="127.0.0.1", port=8000, loop=loop)
