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


def test_request_id_header_is_uuid(client: TestClient) -> None:
    response = client.get("/health/live")
    assert "X-Request-ID" in response.headers
    request_id = response.headers["X-Request-ID"]
    from uuid import UUID

    UUID(request_id)  # 验证是合法 UUID


def test_valid_uuid_request_id_preserved(client: TestClient) -> None:
    custom_id = "0198a7b0-1234-7890-abcd-ef0123456789"
    response = client.get("/health/live", headers={"X-Request-ID": custom_id})
    assert response.headers["X-Request-ID"] == custom_id


def test_non_uuid_request_id_replaced(client: TestClient) -> None:
    response = client.get("/health/live", headers={"X-Request-ID": "not-a-uuid"})
    request_id = response.headers["X-Request-ID"]
    assert request_id != "not-a-uuid"
    from uuid import UUID

    UUID(request_id)  # 替换后必须是合法 UUID
