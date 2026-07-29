"""Workflow execution service."""

from typing import Any
from uuid import UUID


async def execute_workflow_step(workflow_id: UUID, step: dict[str, Any]) -> dict[str, Any]:
    """Execute an approved workflow step via MCP tools."""
    raise NotImplementedError
