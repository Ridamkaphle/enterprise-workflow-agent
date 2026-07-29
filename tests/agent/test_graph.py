"""Tests for LangGraph workflow graph."""

from app.agent.graph import build_workflow_graph


def test_build_workflow_graph() -> None:
    graph = build_workflow_graph()
    assert graph is not None
