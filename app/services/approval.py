"""Human-in-the-loop approval workflow service."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.db.models import ApprovalRequest, ApprovalStatus, Workflow, WorkflowStatus
from app.db.postgres import SessionLocal
from app.services import audit


async def request_approval(
    workflow_id: UUID,
    action: str,
    payload: dict[str, Any],
) -> UUID:
    """Create an approval request for a mutating workflow action."""
    async with SessionLocal() as session:
        approval = ApprovalRequest(
            workflow_id=workflow_id,
            action=action,
            payload=payload,
            status=ApprovalStatus.PENDING,
        )
        session.add(approval)
        workflow = await session.get(Workflow, workflow_id)
        if workflow is not None:
            workflow.status = WorkflowStatus.AWAITING_APPROVAL
        await session.commit()
        approval_id = approval.id

    await audit.record_event(
        workflow_id=workflow_id,
        event_type="approval.requested",
        actor="system",
        details={"action": action, "payload": payload},
    )
    return approval_id


async def resolve_approval(approval_id: UUID, approved: bool, reviewer: str) -> ApprovalRequest:
    """Approve or reject a pending action, returning the resolved request."""
    async with SessionLocal() as session:
        approval = await session.get(ApprovalRequest, approval_id)
        if approval is None:
            raise ValueError(f"Approval request {approval_id} not found")
        if approval.status != ApprovalStatus.PENDING:
            raise ValueError(f"Approval request {approval_id} is already resolved")

        approval.status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
        approval.reviewer = reviewer
        approval.resolved_at = datetime.now(UTC)
        await session.commit()
        await session.refresh(approval)
        workflow_id = approval.workflow_id
        action = approval.action
        payload = approval.payload
        resolved = approval

    await audit.record_event(
        workflow_id=workflow_id,
        event_type="approval.approved" if approved else "approval.rejected",
        actor=reviewer,
        details={"action": action, "payload": payload},
    )
    return resolved
