"""API 存活、就绪与分项降级契约。"""

from collections.abc import Awaitable, Callable
from dataclasses import replace
from pathlib import Path
from uuid import UUID

import pytest
import structlog
from fastapi.testclient import TestClient

from apps.api.app import create_app
from apps.api.dependencies import HealthDependencies, build_health_dependencies
from tests.conftest import BASE_DATABASE_URL


def check(value: bool) -> Callable[[], Awaitable[bool]]:
    async def run() -> bool:
        return value

    return run


def dependencies(
    *,
    database: bool = True,
    security_ready: bool = True,
    redis: bool = True,
    ai: bool = True,
    calendar: bool = True,
    template: bool = True,
    export_storage: bool = True,
) -> HealthDependencies:
    return HealthDependencies(
        database=check(database),
        redis=check(redis),
        ai=check(ai),
        calendar=check(calendar),
        template=check(template),
        export_storage=check(export_storage),
        security_ready=security_ready,
    )


def test_live_reports_process_liveness() -> None:
    response = TestClient(create_app(dependencies())).get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": {}}


def test_database_failure_returns_stable_503_code() -> None:
    response = TestClient(create_app(dependencies(database=False))).get("/health/ready")

    assert response.status_code == 503
    assert response.json()["code"] == "database.unavailable"
    assert response.headers["X-Request-ID"] == response.json()["request_id"]
    UUID(response.json()["request_id"])


def test_invalid_supplied_request_id_is_replaced_consistently() -> None:
    response = TestClient(create_app(dependencies(database=False))).get(
        "/health/ready", headers={"X-Request-ID": "request-123"}
    )

    assert response.headers["X-Request-ID"] == response.json()["request_id"]
    assert response.headers["X-Request-ID"] != "request-123"
    UUID(response.json()["request_id"])


def test_global_security_failure_returns_configuration_503() -> None:
    response = TestClient(create_app(dependencies(security_ready=False))).get("/health/ready")

    assert response.status_code == 503
    assert response.json()["code"] == "configuration.unavailable"


@pytest.mark.parametrize(
    "dependency_name", ["redis", "ai", "calendar", "template", "export_storage"]
)
def test_each_optional_dependency_only_degrades_ready_response(dependency_name: str) -> None:
    response = TestClient(create_app(dependencies(**{dependency_name: False}))).get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "degraded",
        "checks": {
            "database": "ok",
            "security": "ok",
            "redis": "degraded" if dependency_name == "redis" else "ok",
            "ai": "degraded" if dependency_name == "ai" else "ok",
            "calendar": "degraded" if dependency_name == "calendar" else "ok",
            "template": "degraded" if dependency_name == "template" else "ok",
            "export_storage": "degraded" if dependency_name == "export_storage" else "ok",
        },
    }


def test_health_check_exception_is_logged_without_exception_message() -> None:
    async def broken_database() -> bool:
        raise RuntimeError("database-password-must-not-leak")

    health = replace(dependencies(), database=broken_database)

    with structlog.testing.capture_logs() as captured:
        response = TestClient(create_app(health)).get("/health/ready")

    assert response.status_code == 503
    assert captured == [
        {
            "component": "database",
            "error_type": "RuntimeError",
            "event": "health_check_failed",
            "log_level": "warning",
        }
    ]
    assert "database-password-must-not-leak" not in repr(captured)


def test_default_dependencies_check_real_local_runtime(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    runtime_root = tmp_path / "runtime"
    (runtime_root / "exports").mkdir(parents=True)
    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", BASE_DATABASE_URL)
    monkeypatch.delenv("CHILD_MANAGER_REDIS_URL", raising=False)
    monkeypatch.setenv("CHILD_MANAGER_JWT_SIGNING_KEY", "test-jwt-secret")
    monkeypatch.setenv("CHILD_MANAGER_CSRF_SIGNING_KEY", "test-csrf-secret")
    monkeypatch.setenv("CHILD_MANAGER_RUNTIME_ROOT", str(runtime_root))

    response = TestClient(create_app()).get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "degraded",
        "checks": {
            "database": "ok",
            "security": "ok",
            "redis": "degraded",
            "ai": "degraded",
            "calendar": "ok",
            "template": "ok",
            "export_storage": "ok",
        },
    }


@pytest.mark.asyncio
async def test_default_dependencies_require_profile_runtime_root(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CHILD_MANAGER_RUNTIME_ROOT", raising=False)

    health = build_health_dependencies()

    assert await health.export_storage() is False


def test_default_dependencies_reject_blank_security_keys(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CHILD_MANAGER_JWT_SIGNING_KEY", "   ")
    monkeypatch.setenv("CHILD_MANAGER_CSRF_SIGNING_KEY", "\t")

    assert build_health_dependencies().security_ready is False


@pytest.mark.asyncio
async def test_default_calendar_check_degrades_when_library_is_unavailable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def unavailable(_name: str) -> object:
        raise ImportError("calendar unavailable")

    monkeypatch.setattr("apps.api.dependencies.import_module", unavailable)

    assert await build_health_dependencies().calendar() is False
