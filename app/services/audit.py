"""Audit trail service for workflow actions."""

from typing import Any
from uuid import UUID


async def record_event(
    workflow_id: UUID,
    event_type: str,
    actor: str,
    details: dict[str, Any],
) -> None:
    """Persist an auditable workflow event."""
    raise NotImplementedError
