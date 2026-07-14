"""敏感配置与开发回环保护。"""

import pytest

from apps.api import __main__ as api_main
from packages.backend.config import AppSettings, global_security_ready


def settings(**overrides: object) -> AppSettings:
    values: dict[str, object] = {
        "environment": "development",
        "bind_host": "127.0.0.1",
        "cookie_secure": False,
        "database_url": "postgresql+psycopg://user:database-password@127.0.0.1/db",
        "redis_url": "redis://127.0.0.1:6379/0",
        "jwt_signing_key": "jwt-secret-value",
        "csrf_signing_key": "csrf-secret-value",
    }
    values.update(overrides)
    return AppSettings.model_validate(values)


def test_development_insecure_cookie_requires_loopback_binding() -> None:
    allowed = settings()
    allowed.validate_security()

    with pytest.raises(ValueError, match="回环"):
        settings(bind_host="0.0.0.0").validate_security()


def test_production_never_allows_insecure_cookie() -> None:
    with pytest.raises(ValueError, match="Secure"):
        settings(environment="production", cookie_secure=False).validate_security()


def test_settings_repr_masks_all_secret_values() -> None:
    rendered = repr(settings())

    assert "database-password" not in rendered
    assert "jwt-secret-value" not in rendered
    assert "csrf-secret-value" not in rendered


def test_global_security_requires_jwt_and_csrf_keys() -> None:
    assert global_security_ready(settings()) is True
    assert global_security_ready(settings(jwt_signing_key=None)) is False
    assert global_security_ready(settings(csrf_signing_key=None)) is False


def test_api_entrypoint_rejects_insecure_cookie_on_non_loopback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    called = False

    def run_server(*args: object, **kwargs: object) -> None:
        nonlocal called
        called = True

    monkeypatch.setenv("CHILD_MANAGER_ENV", "development")
    monkeypatch.setenv("CHILD_MANAGER_COOKIE_SECURE", "false")
    monkeypatch.setattr(api_main.uvicorn, "run", run_server)
    monkeypatch.setattr("sys.argv", ["python -m apps.api", "--host", "0.0.0.0"])

    with pytest.raises(ValueError, match="回环"):
        api_main.main()

    assert called is False
