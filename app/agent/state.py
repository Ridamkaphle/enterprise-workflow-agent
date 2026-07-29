"""Shared LangGraph state schema."""

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class WorkflowState(TypedDict):
    """State passed between LangGraph nodes."""

    messages: Annotated[list, add_messages]
    workflow_id: str
    pending_approval: bool
