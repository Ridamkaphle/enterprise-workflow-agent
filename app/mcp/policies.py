"""Tool access-control policy (security-sensitive).

Flagged per this repo's own CLAUDE.md/AGENTS.md guardrail: any change here
is a security-relevant change to who may invoke which tools, called out
explicitly rather than folded into an unrelated change.

Policy model: default-deny, explicit allow rules keyed by (actor, tool).
Two actor roles are recognized:

- "automation" — the agent acting on its own, before any human has signed
  off. May only call read-only tools (none are registered yet, but the
  allowlist below is where they'd go).
- "approved-action" — the agent acting *after* a human has approved the
  specific mutating action via the approval service
  (`app/services/approval.py`). This is the only role allowed to invoke
  tools that send messages, create tickets, or otherwise mutate an
  external system.
"""

from typing import Any

# Tools that mutate external systems. Every entry here requires the
# "approved-action" actor — i.e. it must have gone through
# app/services/approval.py first.
_MUTATING_TOOLS = {
    "slack_send_message",
    "gmail_send_email",
    "github_create_issue",
    "jira_create_ticket",
    "calendar_create_event",
}

# Read-only tools any automated actor may call directly, without approval.
_READ_ONLY_TOOLS: set[str] = set()

_ALLOWED_BY_ACTOR: dict[str, set[str]] = {
    "automation": _READ_ONLY_TOOLS,
    "approved-action": _READ_ONLY_TOOLS | _MUTATING_TOOLS,
}


def is_tool_allowed(tool_name: str, actor: str, context: dict[str, Any] | None = None) -> bool:
    """Determine whether an actor may invoke the given tool."""
    _ = context
    return tool_name in _ALLOWED_BY_ACTOR.get(actor, set())


def requires_approval(tool_name: str) -> bool:
    """Whether invoking this tool requires a human approval first."""
    return tool_name in _MUTATING_TOOLS
