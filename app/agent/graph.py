"""LangGraph workflow graph definition."""

from langgraph.graph import END, START, StateGraph

from app.agent.nodes import execute_node, plan_node
from app.agent.state import WorkflowState


def build_workflow_graph() -> StateGraph:
    """Build and compile the enterprise workflow graph."""
    graph = StateGraph(WorkflowState)
    graph.add_node("plan", plan_node)
    graph.add_node("execute", execute_node)
    graph.add_edge(START, "plan")
    graph.add_edge("plan", "execute")
    graph.add_edge("execute", END)
    return graph
