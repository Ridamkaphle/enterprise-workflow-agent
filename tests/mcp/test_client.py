"""Tests for the local MCP client."""

import pytest

from app.mcp.client import MCPClient
from app.mcp.tools import register_mock_tools


@pytest.fixture(autouse=True)
def _register_tools() -> None:
    register_mock_tools()


async def test_call_tool_denied_for_disallowed_actor() -> None:
    client = MCPClient("http://localhost:8080")
    with pytest.raises(PermissionError):
        await client.call_tool(
            "slack_send_message", {"channel": "#x", "text": "hi"}, actor="automation"
        )


async def test_call_tool_succeeds_for_approved_action() -> None:
    client = MCPClient("http://localhost:8080")
    result = await client.call_tool(
        "slack_send_message", {"channel": "#x", "text": "hi"}, actor="approved-action"
    )
    assert result["status"] == "simulated"


async def test_call_tool_unknown_tool_raises() -> None:
    client = MCPClient("http://localhost:8080")
    with pytest.raises(KeyError):
        await client.call_tool("does_not_exist", {}, actor="approved-action")
