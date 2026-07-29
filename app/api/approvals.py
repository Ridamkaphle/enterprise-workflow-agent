"""Human-in-the-loop approval HTTP endpoints."""

from fastapi import APIRouter

router = APIRouter(prefix="/approvals", tags=["approvals"])
