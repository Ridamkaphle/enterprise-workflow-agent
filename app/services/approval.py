"""Human-in-the-loop approval workflow service."""

from typing import Any
from uuid import UUID


async def request_approval(
    workflow_id: UUID,
    action: str,
    payload: dict[str, Any],
) -> UUID:
    """Create an approval request for a mutating workflow action."""
    raise NotImplementedError


async def resolve_approval(approval_id: UUID, approved: bool, reviewer: str) -> None:
    """Approve or reject a pending action."""
    raise NotImplementedError
