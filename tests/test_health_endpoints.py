import pytest
from fastapi.testclient import TestClient

from apps.api.main import HealthDependencies, create_app


@pytest.fixture
def mock_health_dependencies():
    async def always_ready() -> bool:
        return True

    return HealthDependencies(
        database=always_ready,
        redis=always_ready,
        ai=always_ready,
        calendar=always_ready,
        template=always_ready,
        export_storage=always_ready,
        security_ready=True,
    )


@pytest.fixture
def client(mock_health_dependencies):
    app = create_app(dependencies=mock_health_dependencies)
    return TestClient(app)


def test_health_live(client):
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["component"] == "api"
    assert "request_id" in data
    assert "timestamp" in data


def test_health_ready(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["component"] == "api"
    assert "request_id" in data
    assert "timestamp" in data


def test_request_id_header(client):
    response = client.get("/health/live")
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0


def test_custom_request_id(client):
    custom_id = "test-request-123"
    response = client.get("/health/live", headers={"X-Request-ID": custom_id})
    assert response.headers["X-Request-ID"] == custom_id
