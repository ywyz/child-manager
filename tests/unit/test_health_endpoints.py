from fastapi.testclient import TestClient

from apps.api.main import HealthDependencies, create_app


async def always_ready() -> bool:
    return True


mock_dependencies = HealthDependencies(
    database=always_ready,
    redis=always_ready,
    ai=always_ready,
    calendar=always_ready,
    template=always_ready,
    export_storage=always_ready,
    security_ready=True,
)

app = create_app(dependencies=mock_dependencies)
client = TestClient(app)


def test_health_live_returns_healthy():
    response = client.get("/health/live")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["component"] == "api"


def test_health_ready_returns_healthy():
    response = client.get("/health/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["component"] == "api"


def test_health_live_has_request_id():
    response = client.get("/health/live")

    assert "X-Request-ID" in response.headers


def test_health_ready_has_request_id():
    response = client.get("/health/ready")

    assert "X-Request-ID" in response.headers


def test_custom_request_id_propagated():
    custom_id = "my-custom-request-id-123"
    response = client.get("/health/live", headers={"X-Request-ID": custom_id})

    assert response.headers["X-Request-ID"] == custom_id
