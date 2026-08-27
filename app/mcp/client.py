"""MCP server client for tool invocation.

This client resolves and invokes tools from the local `app.mcp.registry`.
It is a stand-in for a real MCP wire protocol client: no requests are sent
to `server_url` today. Standing up a real MCP server transport later means
replacing the body of `call_tool` — the governance (policy check) and
call-site contract stay the same.
"""

from typing import Any, cast

from app.mcp.policies import is_tool_allowed
from app.mcp.registry import get_tool


class MCPClient:
    """Client for communicating with MCP servers."""

    def __init__(self, server_url: str) -> None:
        self.server_url = server_url

    async def call_tool(
        self, tool_name: str, arguments: dict[str, Any], actor: str
    ) -> dict[str, Any]:
        """Invoke a registered MCP tool, subject to access-control policy."""
        handler = get_tool(tool_name)
        if handler is None:
            raise KeyError(f"No tool registered with name '{tool_name}'")

        if not is_tool_allowed(tool_name, actor):
            raise PermissionError(f"Actor '{actor}' is not allowed to call tool '{tool_name}'")

        return cast(dict[str, Any], await handler(arguments))
