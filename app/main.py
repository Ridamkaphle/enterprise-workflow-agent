"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api import approvals, workflows

app = FastAPI(
    title="Enterprise Workflow Agent",
    description="Distributed agentic platform for enterprise workflow orchestration.",
    version="0.1.0",
)

app.include_router(workflows.router)
app.include_router(approvals.router)
