"""Tests for MCP tool registry."""

from app.mcp import registry


def test_list_tools_empty_by_default() -> None:
    assert registry.list_tools() == []
