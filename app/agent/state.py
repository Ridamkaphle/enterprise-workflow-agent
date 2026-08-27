"""Shared LangGraph state schema."""

from typing import Annotated, Any, TypedDict

from langgraph.graph.message import add_messages


class WorkflowState(TypedDict):
    """State passed between LangGraph nodes."""

    messages: Annotated[list[Any], add_messages]
    workflow_id: str
    action: str
    payload: dict[str, Any]
    requires_approval: bool
    approval_id: str | None
    result: dict[str, Any] | None
