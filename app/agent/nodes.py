"""LangGraph node functions."""

from app.agent.state import WorkflowState


async def plan_node(state: WorkflowState) -> WorkflowState:
    """Plan the next workflow steps."""
    return state


async def execute_node(state: WorkflowState) -> WorkflowState:
    """Execute approved workflow actions via services layer."""
    return state
