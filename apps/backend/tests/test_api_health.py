"""Tests for health and readiness endpoints."""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.dependencies import get_db_session
from api.main import create_app


def test_healthz_returns_healthy(client: TestClient) -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert "version" in payload
    assert "timestamp" in payload


def test_api_health_readiness_connected(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["database"] == "connected"


def test_api_health_readiness_failure_returns_503() -> None:
    app = create_app()

    def broken_db_session():
        class FakeSession:
            def execute(self, stmt):
                raise ConnectionError("Database unreachable")

        yield FakeSession()

    app.dependency_overrides[get_db_session] = broken_db_session
    with TestClient(app) as test_client:
        response = test_client.get("/api/v1/health")
        assert response.status_code == 503
        payload = response.json()
        assert payload["status"] == "degraded"
        assert payload["database"] == "disconnected"


def test_root_redirects_to_docs(client: TestClient) -> None:
    response = client.get("/", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/docs"
