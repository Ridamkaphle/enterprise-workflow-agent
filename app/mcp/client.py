"""MCP server client for tool invocation."""

from typing import Any


class MCPClient:
    """Client for communicating with MCP servers."""

    def __init__(self, server_url: str) -> None:
        self.server_url = server_url

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        """Invoke a registered MCP tool."""
        raise NotImplementedError
