"""健康检查端点权威行为覆盖。

验证运行时 /health/live 和 /health/ready 响应符合静态 OpenAPI 契约，
而非仅验证 YAML 自洽。覆盖存活、就绪、数据库不可用、安全配置缺失和
非关键组件 degraded 等矩阵。
"""

from pathlib import Path

import pytest
import yaml
from fastapi.testclient import TestClient
from jsonschema import validate

from apps.api.main import HealthDependencies, create_app

OPENAPI_PATH = (
    Path(__file__).resolve().parents[2] / "specs/001-daily-activity-plan/contracts/openapi.yaml"
)


def _health_schema() -> dict[str, object]:
    with OPENAPI_PATH.open() as f:
        spec = yaml.safe_load(f)
    return spec["components"]["schemas"]["Health"]


def _error_schema() -> dict[str, object]:
    with OPENAPI_PATH.open() as f:
        spec = yaml.safe_load(f)
    return spec["components"]["schemas"]["Error"]


async def _always_true() -> bool:
    return True


async def _always_false() -> bool:
    return False


def _make_dependencies(**overrides: object) -> HealthDependencies:
    defaults: dict[str, object] = {
        "database": _always_true,
        "redis": _always_true,
        "ai": _always_true,
        "calendar": _always_true,
        "template": _always_true,
        "export_storage": _always_true,
        "security_ready": True,
    }
    defaults.update(overrides)
    return HealthDependencies(**defaults)  # type: ignore[arg-type]


@pytest.fixture
def client_factory():
    def _create(dependencies: HealthDependencies) -> TestClient:
        return TestClient(create_app(dependencies=dependencies))

    return _create


def test_live_returns_ok_with_empty_checks(client_factory) -> None:
    client = client_factory(_make_dependencies())
    response = client.get("/health/live")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["checks"] == {}
    validate(instance=data, schema=_health_schema())


def test_ready_returns_ok_when_all_pass(client_factory) -> None:
    client = client_factory(_make_dependencies())
    response = client.get("/health/ready")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["checks"]["database"] == "ok"
    assert data["checks"]["security"] == "ok"
    validate(instance=data, schema=_health_schema())


def test_ready_returns_503_when_database_unavailable(client_factory) -> None:
    deps = _make_dependencies(database=_always_false)
    client = client_factory(deps)
    response = client.get("/health/ready")

    assert response.status_code == 503
    data = response.json()
    assert data["code"] == "database.unavailable"
    assert "request_id" in data
    validate(instance=data, schema=_error_schema())


def test_ready_returns_503_when_security_not_ready(client_factory) -> None:
    deps = _make_dependencies(security_ready=False)
    client = client_factory(deps)
    response = client.get("/health/ready")

    assert response.status_code == 503
    data = response.json()
    assert data["code"] == "configuration.unavailable"


def test_ready_returns_degraded_when_non_critical_fails(client_factory) -> None:
    deps = _make_dependencies(redis=_always_false, ai=_always_false)
    client = client_factory(deps)
    response = client.get("/health/ready")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "degraded"
    assert data["checks"]["redis"] == "degraded"
    assert data["checks"]["ai"] == "degraded"
    assert data["checks"]["database"] == "ok"
    validate(instance=data, schema=_health_schema())


def test_live_response_has_no_extra_fields(client_factory) -> None:
    client = client_factory(_make_dependencies())
    response = client.get("/health/live")

    data = response.json()
    assert set(data.keys()) == {"status", "checks"}


def test_ready_response_has_no_extra_fields(client_factory) -> None:
    client = client_factory(_make_dependencies())
    response = client.get("/health/ready")

    data = response.json()
    assert set(data.keys()) == {"status", "checks"}


def test_live_response_has_request_id(client_factory) -> None:
    client = client_factory(_make_dependencies())
    response = client.get("/health/live")

    assert "X-Request-ID" in response.headers
    from uuid import UUID

    UUID(response.headers["X-Request-ID"])


def test_ready_response_has_request_id(client_factory) -> None:
    client = client_factory(_make_dependencies())
    response = client.get("/health/ready")

    assert "X-Request-ID" in response.headers
    from uuid import UUID

    UUID(response.headers["X-Request-ID"])
