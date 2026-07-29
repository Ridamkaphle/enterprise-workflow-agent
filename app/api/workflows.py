"""Workflow HTTP endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Health check for the workflow service."""
    return {"status": "ok"}
