"""Human-in-the-loop approval HTTP endpoints."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Request
from langgraph.types import Command
from pydantic import BaseModel
from sqlalchemy import select

from app.db.models import ApprovalRequest, ApprovalStatus, WorkflowStatus
from app.db.postgres import SessionLocal
from app.services import approval as approval_service
from app.services import workflow as workflow_service

router = APIRouter(prefix="/approvals", tags=["approvals"])


class ApprovalResponse(BaseModel):
    id: str
    workflow_id: str
    action: str
    payload: dict[str, Any]
    status: str


class ResolveApprovalRequest(BaseModel):
    approved: bool
    reviewer: str


@router.get("", response_model=list[ApprovalResponse])
async def list_pending_approvals() -> list[ApprovalResponse]:
    """List approval requests awaiting a decision."""
    async with SessionLocal() as session:
        result = await session.execute(
            select(ApprovalRequest).where(ApprovalRequest.status == ApprovalStatus.PENDING)
        )
        return [
            ApprovalResponse(
                id=str(a.id),
                workflow_id=str(a.workflow_id),
                action=a.action,
                payload=a.payload,
                status=a.status.value,
            )
            for a in result.scalars().all()
        ]


@router.post("/{approval_id}/resolve")
async def resolve_pending_approval(
    approval_id: UUID, request: Request, body: ResolveApprovalRequest
) -> dict[str, Any]:
    """Approve or reject a pending action, resuming its workflow from its checkpoint.

    This is the recoverability path: the workflow run isn't restarted, it
    resumes the same LangGraph run from the Postgres checkpoint captured
    when it paused at the approval node.
    """
    try:
        resolved = await approval_service.resolve_approval(
            approval_id=approval_id, approved=body.approved, reviewer=body.reviewer
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if not body.approved:
        await workflow_service.set_workflow_status(resolved.workflow_id, WorkflowStatus.CANCELLED)
        return {
            "approval_id": str(approval_id),
            "workflow_id": str(resolved.workflow_id),
            "status": WorkflowStatus.CANCELLED.value,
            "result": {"status": "rejected"},
        }

    graph = request.app.state.graph
    config = {"configurable": {"thread_id": str(resolved.workflow_id)}}

    try:
        final_state = await graph.ainvoke(
            Command(resume={"approved": True, "reviewer": body.reviewer}),
            config=config,
        )
    except Exception as exc:
        await workflow_service.set_workflow_status(resolved.workflow_id, WorkflowStatus.FAILED)
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    await workflow_service.set_workflow_status(resolved.workflow_id, WorkflowStatus.COMPLETED)
    return {
        "approval_id": str(approval_id),
        "workflow_id": str(resolved.workflow_id),
        "status": WorkflowStatus.COMPLETED.value,
        "result": final_state.get("result"),
    }
