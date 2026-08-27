"""Mock enterprise tool integrations.

These are LOCAL SIMULATIONS, not real integrations. None of these
functions make an outbound network call or use any OAuth token / API key
from `app/config.py` — they just validate the payload shape and return a
deterministic "simulated" result so the rest of the platform (approval
gating, audit trail, checkpointed execution) can be exercised end-to-end
without talking to Slack, Gmail, GitHub, Jira, or a real calendar service.

Swapping one of these for a real integration means replacing the body of
the handler with an actual API call — the registration, policy, approval,
and audit plumbing around it does not change.
"""

from typing import Any

from app.mcp.registry import register_tool


def _require(payload: dict[str, Any], *fields: str) -> None:
    missing = [f for f in fields if f not in payload]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")


async def slack_send_message(payload: dict[str, Any]) -> dict[str, Any]:
    """Simulate posting a Slack message. Real integration would call chat.postMessage."""
    _require(payload, "channel", "text")
    return {
        "status": "simulated",
        "tool": "slack_send_message",
        "channel": payload["channel"],
        "text": payload["text"],
    }


async def gmail_send_email(payload: dict[str, Any]) -> dict[str, Any]:
    """Simulate sending an email. Real integration would call the Gmail API."""
    _require(payload, "to", "subject", "body")
    return {
        "status": "simulated",
        "tool": "gmail_send_email",
        "to": payload["to"],
        "subject": payload["subject"],
    }


async def github_create_issue(payload: dict[str, Any]) -> dict[str, Any]:
    """Simulate opening a GitHub issue. Real integration would call the Issues API."""
    _require(payload, "repo", "title")
    return {
        "status": "simulated",
        "tool": "github_create_issue",
        "repo": payload["repo"],
        "title": payload["title"],
        "issue_number": 1,
    }


async def jira_create_ticket(payload: dict[str, Any]) -> dict[str, Any]:
    """Simulate creating a Jira ticket. Real integration would call the Jira REST API."""
    _require(payload, "project", "summary")
    return {
        "status": "simulated",
        "tool": "jira_create_ticket",
        "project": payload["project"],
        "summary": payload["summary"],
        "ticket_key": f"{payload['project']}-1",
    }


async def calendar_create_event(payload: dict[str, Any]) -> dict[str, Any]:
    """Simulate scheduling a calendar event. Real integration would call the Calendar API."""
    _require(payload, "title", "start_time")
    return {
        "status": "simulated",
        "tool": "calendar_create_event",
        "title": payload["title"],
        "start_time": payload["start_time"],
    }


def register_mock_tools() -> None:
    """Register all mock enterprise tools with the MCP registry."""
    register_tool("slack_send_message", slack_send_message)
    register_tool("gmail_send_email", gmail_send_email)
    register_tool("github_create_issue", github_create_issue)
    register_tool("jira_create_ticket", jira_create_ticket)
    register_tool("calendar_create_event", calendar_create_event)
