"""Tool access-control policy (security-sensitive)."""

from typing import Any


def is_tool_allowed(tool_name: str, actor: str, context: dict[str, Any] | None = None) -> bool:
    """Determine whether an actor may invoke the given tool."""
    _ = context
    # Default deny; extend with role-based rules per integration.
    return False
