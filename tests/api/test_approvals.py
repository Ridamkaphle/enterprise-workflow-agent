"""End-to-end tests for the human-in-the-loop approval flow.

These exercise the full path: create a workflow whose action is mutating
(so it pauses on approval), confirm it's `awaiting_approval`, resolve the
approval, and confirm the workflow resumes from its Postgres checkpoint
and completes rather than restarting.
"""

from fastapi.testclient import TestClient


def test_mutating_action_pauses_for_approval(app_client: TestClient) -> None:
    response = app_client.post(
        "/workflows",
        json={
            "action": "slack_send_message",
            "payload": {"channel": "#general", "text": "hello"},
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "awaiting_approval"
    assert body["result"] is None

    pending = app_client.get("/approvals").json()
    match = next(a for a in pending if a["workflow_id"] == body["workflow_id"])
    assert match["action"] == "slack_send_message"


def test_approving_resumes_workflow_to_completion(app_client: TestClient) -> None:
    created = app_client.post(
        "/workflows",
        json={
            "action": "jira_create_ticket",
            "payload": {"project": "ENG", "summary": "Ship the feature"},
        },
    ).json()

    pending = app_client.get("/approvals").json()
    approval = next(a for a in pending if a["workflow_id"] == created["workflow_id"])

    resolved = app_client.post(
        f"/approvals/{approval['id']}/resolve",
        json={"approved": True, "reviewer": "kaphleridam@gmail.com"},
    )
    assert resolved.status_code == 200
    body = resolved.json()
    assert body["status"] == "completed"
    assert body["result"]["ticket_key"] == "ENG-1"

    workflow = app_client.get(f"/workflows/{created['workflow_id']}").json()
    assert workflow["status"] == "completed"


def test_rejecting_cancels_workflow(app_client: TestClient) -> None:
    created = app_client.post(
        "/workflows",
        json={
            "action": "github_create_issue",
            "payload": {"repo": "org/repo", "title": "Bug"},
        },
    ).json()

    pending = app_client.get("/approvals").json()
    approval = next(a for a in pending if a["workflow_id"] == created["workflow_id"])

    resolved = app_client.post(
        f"/approvals/{approval['id']}/resolve",
        json={"approved": False, "reviewer": "kaphleridam@gmail.com"},
    )
    assert resolved.status_code == 200
    assert resolved.json()["status"] == "cancelled"

    workflow = app_client.get(f"/workflows/{created['workflow_id']}").json()
    assert workflow["status"] == "cancelled"
