"""Workflow HTTP endpoints."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.db.models import WorkflowStatus
from app.services import workflow as workflow_service

router = APIRouter(prefix="/workflows", tags=["workflows"])


class CreateWorkflowRequest(BaseModel):
    """A workflow run is a single action dispatched through governed MCP tools."""

    action: str
    payload: dict[str, Any] = {}


class WorkflowResponse(BaseModel):
    workflow_id: str
    status: str
    result: dict[str, Any] | None = None


@router.get("/health")
async def health() -> dict[str, str]:
    """Health check for the workflow service."""
    return {"status": "ok"}


@router.post("", response_model=WorkflowResponse)
async def create_workflow(request: Request, body: CreateWorkflowRequest) -> WorkflowResponse:
    """Create a workflow and run it until completion or a pending approval.

    Mutating actions (see `app/mcp/policies.py`) pause the run at the
    approval node; the workflow's status will come back
    `awaiting_approval` and it resumes from its Postgres checkpoint once
    resolved via `POST /approvals/{id}/resolve`.
    """
    workflow_id = await workflow_service.create_workflow()
    graph = request.app.state.graph
    config = {"configurable": {"thread_id": str(workflow_id)}}

    try:
        final_state = await graph.ainvoke(
            {
                "messages": [],
                "workflow_id": str(workflow_id),
                "action": body.action,
                "payload": body.payload,
                "requires_approval": False,
                "approval_id": None,
                "result": None,
            },
            config=config,
        )
    except Exception:
        await workflow_service.set_workflow_status(workflow_id, WorkflowStatus.FAILED)
        raise

    snapshot = await graph.aget_state(config)
    if not snapshot.next:
        # Ran to completion without pausing on an approval.
        await workflow_service.set_workflow_status(workflow_id, WorkflowStatus.COMPLETED)

    workflow = await workflow_service.get_workflow(workflow_id)
    assert workflow is not None
    return WorkflowResponse(
        workflow_id=str(workflow_id),
        status=workflow.status.value,
        result=final_state.get("result"),
    )


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow(workflow_id: UUID) -> WorkflowResponse:
    """Fetch a workflow's current status."""
    workflow = await workflow_service.get_workflow(workflow_id)
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return WorkflowResponse(workflow_id=str(workflow_id), status=workflow.status.value)
