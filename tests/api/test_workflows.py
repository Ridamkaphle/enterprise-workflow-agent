"""Tests for workflow HTTP endpoints."""

from fastapi.testclient import TestClient


def test_workflow_health(client: TestClient) -> None:
    response = client.get("/workflows/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
