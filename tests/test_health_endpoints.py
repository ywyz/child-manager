import pytest
from fastapi.testclient import TestClient

from apps.api.main import HealthDependencies, create_app


@pytest.fixture
def mock_health_dependencies() -> HealthDependencies:
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
def client(mock_health_dependencies: HealthDependencies) -> TestClient:
    app_instance = create_app(dependencies=mock_health_dependencies)
    return TestClient(app_instance)


def test_health_live(client: TestClient) -> None:
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["checks"] == {}


def test_health_ready(client: TestClient) -> None:
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "database" in data["checks"]
    assert data["checks"]["database"] == "ok"


def test_request_id_header(client: TestClient) -> None:
    response = client.get("/health/live")
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0


def test_custom_request_id(client: TestClient) -> None:
    custom_id = "test-request-123"
    response = client.get("/health/live", headers={"X-Request-ID": custom_id})
    assert response.headers["X-Request-ID"] == custom_id
