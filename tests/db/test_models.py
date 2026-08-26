"""Database layer integration tests."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ApprovalRequest, ApprovalStatus, AuditEvent, Workflow, WorkflowStatus


@pytest.mark.asyncio
async def test_create_workflow(db_session: AsyncSession) -> None:
    """A workflow row can be saved and read back from Postgres."""
    workflow = Workflow(status=WorkflowStatus.PENDING)
    db_session.add(workflow)
    await db_session.commit()

    result = await db_session.execute(select(Workflow).where(Workflow.id == workflow.id))
    saved = result.scalar_one()

    assert saved.id == workflow.id
    assert saved.status == WorkflowStatus.PENDING


@pytest.mark.asyncio
async def test_workflow_with_approval_and_audit(db_session: AsyncSession) -> None:
    """Workflows can be linked to approval requests and audit events."""
    workflow = Workflow(status=WorkflowStatus.AWAITING_APPROVAL)
    approval = ApprovalRequest(
        workflow=workflow,
        action="send_slack_message",
        payload={"channel": "#general", "text": "Hello"},
        status=ApprovalStatus.PENDING,
    )
    audit = AuditEvent(
        workflow=workflow,
        event_type="approval.requested",
        actor="system",
        details={"action": "send_slack_message"},
    )
    db_session.add_all([workflow, approval, audit])
    await db_session.commit()

    result = await db_session.execute(
        select(Workflow).where(Workflow.id == workflow.id)
    )
    saved = result.scalar_one()

    assert len(saved.approval_requests) == 1
    assert saved.approval_requests[0].action == "send_slack_message"
    assert len(saved.audit_events) == 1
    assert saved.audit_events[0].event_type == "approval.requested"


@pytest.mark.asyncio
async def test_audit_event_without_workflow(db_session: AsyncSession) -> None:
    """System-level audit events may exist without a workflow id."""
    audit = AuditEvent(
        workflow_id=None,
        event_type="system.startup",
        actor="system",
        details={"version": "0.1.0"},
    )
    db_session.add(audit)
    await db_session.commit()

    result = await db_session.execute(select(AuditEvent).where(AuditEvent.id == audit.id))
    saved = result.scalar_one()

    assert saved.workflow_id is None
    assert saved.event_type == "system.startup"
