"""Tests for MCP tool access-control policy."""

from app.mcp.policies import is_tool_allowed, requires_approval


def test_mutating_tool_requires_approval() -> None:
    assert requires_approval("slack_send_message") is True


def test_unknown_tool_does_not_require_approval() -> None:
    assert requires_approval("not_a_real_tool") is False


def test_automation_actor_cannot_call_mutating_tool() -> None:
    assert is_tool_allowed("slack_send_message", actor="automation") is False


def test_approved_action_actor_can_call_mutating_tool() -> None:
    assert is_tool_allowed("slack_send_message", actor="approved-action") is True


def test_unknown_actor_is_denied_by_default() -> None:
    assert is_tool_allowed("slack_send_message", actor="anonymous") is False
