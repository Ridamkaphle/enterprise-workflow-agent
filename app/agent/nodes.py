"""LangGraph node functions."""

from uuid import UUID

from langgraph.types import interrupt

from app.agent.state import WorkflowState
from app.mcp.policies import requires_approval as tool_requires_approval
from app.services import approval as approval_service
from app.services import execution as execution_service


async def plan_node(state: WorkflowState) -> WorkflowState:
    """Plan the next workflow step: decide if the requested action needs approval."""
    state["requires_approval"] = tool_requires_approval(state["action"])
    return state


async def approval_node(state: WorkflowState) -> WorkflowState:
    """Gate mutating actions behind a human approval, pausing the graph.

    On first entry this creates a pending ApprovalRequest and calls
    `interrupt()`, which LangGraph checkpoints to Postgres and pauses the
    run. Resuming with `Command(resume={"approved": bool})` re-enters this
    node; the approval_id guard below skips re-creating the approval
    request and `interrupt()` returns the resume value instead of pausing
    again.
    """
    if not state["requires_approval"]:
        return state

    if not state.get("approval_id"):
        approval_id = await approval_service.request_approval(
            workflow_id=UUID(state["workflow_id"]),
            action=state["action"],
            payload=state["payload"],
        )
        state["approval_id"] = str(approval_id)

    decision = interrupt(
        {
            "approval_id": state["approval_id"],
            "action": state["action"],
            "payload": state["payload"],
        }
    )
    if not decision.get("approved", False):
        state["result"] = {"status": "rejected"}
    return state


async def execute_node(state: WorkflowState) -> WorkflowState:
    """Execute the workflow action via the services layer, unless it was rejected."""
    if (state.get("result") or {}).get("status") == "rejected":
        return state

    result = await execution_service.execute_workflow_step(
        workflow_id=UUID(state["workflow_id"]),
        step={"action": state["action"], "payload": state["payload"]},
    )
    state["result"] = result
    return state
