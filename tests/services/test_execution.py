"""Integration tests for the workflow execution service."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AuditEvent
from app.mcp.tools import register_mock_tools
from app.services.execution import execute_workflow_step
from app.services.workflow import create_workflow


@pytest.fixture(autouse=True)
def _register_tools() -> None:
    register_mock_tools()


async def test_execute_workflow_step_records_audit_event(db_session: AsyncSession) -> None:
    workflow_id = await create_workflow()

    result = await execute_workflow_step(
        workflow_id=workflow_id,
        step={"action": "jira_create_ticket", "payload": {"project": "ENG", "summary": "Test"}},
    )
    assert result["status"] == "simulated"

    events = (
        (await db_session.execute(select(AuditEvent).where(AuditEvent.workflow_id == workflow_id)))
        .scalars()
        .all()
    )
    assert any(e.event_type == "execution.succeeded" for e in events)
