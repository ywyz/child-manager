import pytest
from fastapi.testclient import TestClient

from apps.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health_live(client):
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "component": "api"}


def test_health_ready(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "component": "api"}


def test_request_id_header(client):
    response = client.get("/health/live")
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0


def test_custom_request_id(client):
    custom_id = "test-request-123"
    response = client.get("/health/live", headers={"X-Request-ID": custom_id})
    assert response.headers["X-Request-ID"] == custom_id
