"""Workflow execution service."""

from typing import Any
from uuid import UUID

from app.config import settings
from app.mcp.client import MCPClient
from app.services import audit

_client = MCPClient(settings.mcp_server_url)


async def execute_workflow_step(workflow_id: UUID, step: dict[str, Any]) -> dict[str, Any]:
    """Execute an approved workflow step via MCP tools.

    `step` must contain `action` (the registered tool name) and `payload`
    (the tool's arguments). Execution runs as the "approved-action" actor —
    callers are expected to have already gone through the approval flow in
    `app/services/approval.py` for any mutating action.
    """
    action = step["action"]
    payload = step.get("payload", {})

    try:
        result = await _client.call_tool(action, payload, actor="approved-action")
        await audit.record_event(
            workflow_id=workflow_id,
            event_type="execution.succeeded",
            actor="approved-action",
            details={"action": action, "payload": payload, "result": result},
        )
        return result
    except Exception as exc:
        await audit.record_event(
            workflow_id=workflow_id,
            event_type="execution.failed",
            actor="approved-action",
            details={"action": action, "payload": payload, "error": str(exc)},
        )
        raise
