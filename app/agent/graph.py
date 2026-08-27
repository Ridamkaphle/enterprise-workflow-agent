"""LangGraph workflow graph definition."""

from typing import Any

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agent.nodes import approval_node, execute_node, plan_node
from app.agent.state import WorkflowState


def build_workflow_graph(
    checkpointer: BaseCheckpointSaver[Any] | None = None,
) -> CompiledStateGraph[WorkflowState, Any, Any, Any]:
    """Build and compile the enterprise workflow graph.

    `checkpointer` should be a `AsyncPostgresSaver` (see `app/db/checkpoint.py`)
    in production so an interrupted (awaiting-approval) run persists and can
    be resumed later without restarting execution from the start.
    """
    graph = StateGraph(WorkflowState)
    graph.add_node("plan", plan_node)
    graph.add_node("approval", approval_node)
    graph.add_node("execute", execute_node)
    graph.add_edge(START, "plan")
    graph.add_edge("plan", "approval")
    graph.add_edge("approval", "execute")
    graph.add_edge("execute", END)
    return graph.compile(checkpointer=checkpointer)
