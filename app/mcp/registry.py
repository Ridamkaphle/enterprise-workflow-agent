"""MCP tool registration and discovery."""

from collections.abc import Callable
from typing import Any

ToolHandler = Callable[..., Any]

_REGISTRY: dict[str, ToolHandler] = {}


def register_tool(name: str, handler: ToolHandler) -> None:
    """Register an MCP tool handler."""
    _REGISTRY[name] = handler


def get_tool(name: str) -> ToolHandler | None:
    """Look up a registered tool by name."""
    return _REGISTRY.get(name)


def list_tools() -> list[str]:
    """Return all registered tool names."""
    return list(_REGISTRY.keys())
