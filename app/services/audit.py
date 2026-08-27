"""Audit trail service for workflow actions."""

from typing import Any
from uuid import UUID

from app.db.models import AuditEvent
from app.db.postgres import SessionLocal


async def record_event(
    workflow_id: UUID | None,
    event_type: str,
    actor: str,
    details: dict[str, Any],
) -> None:
    """Persist an auditable workflow event."""
    async with SessionLocal() as session:
        session.add(
            AuditEvent(
                workflow_id=workflow_id,
                event_type=event_type,
                actor=actor,
                details=details,
            )
        )
        await session.commit()
