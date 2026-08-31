"""Tests for mock enterprise tool integrations."""

import pytest

from app.mcp import registry, tools


def test_register_mock_tools() -> None:
    tools.register_mock_tools()
    registered = registry.list_tools()
    for name in (
        "slack_send_message",
        "gmail_send_email",
        "github_create_issue",
        "jira_create_ticket",
        "calendar_create_event",
    ):
        assert name in registered


async def test_slack_send_message_simulated() -> None:
    result = await tools.slack_send_message({"channel": "#general", "text": "hi"})
    assert result["status"] == "simulated"
    assert result["channel"] == "#general"


async def test_slack_send_message_missing_field() -> None:
    with pytest.raises(ValueError, match="Missing required fields"):
        await tools.slack_send_message({"channel": "#general"})


async def test_jira_create_ticket_simulated() -> None:
    result = await tools.jira_create_ticket({"project": "ENG", "summary": "Fix bug"})
    assert result["ticket_key"] == "ENG-1"
