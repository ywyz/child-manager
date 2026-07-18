from packages.backend.config import Settings


def test_settings_defaults(monkeypatch):
    monkeypatch.delenv("CHILD_MANAGER_ENVIRONMENT", raising=False)
    settings = Settings()
    assert settings.environment == "production"
    assert settings.api_host == "127.0.0.1"
    assert settings.api_port == 28000
    assert settings.web_host == "127.0.0.1"
    assert settings.web_port == 28080


def test_jwt_settings():
    settings = Settings()
    assert settings.jwt_algorithm == "HS256"
    assert settings.jwt_expire_minutes == 15


def test_allowed_hosts():
    settings = Settings()
    assert "localhost" in settings.allowed_hosts
    assert "127.0.0.1" in settings.allowed_hosts


def test_database_url():
    settings = Settings(database_url="postgresql+psycopg://user:pass@localhost:5432/test_db")
    assert settings.database_url == "postgresql+psycopg://user:pass@localhost:5432/test_db"


def test_redis_url():
    settings = Settings(redis_url="redis://localhost:6379/1")
    assert settings.redis_url == "redis://localhost:6379/1"


def test_cookie_security_validation():
    settings = Settings(environment="development")
    settings.validate_cookie_security(bind_host="127.0.0.1", cookie_secure=False)


def test_cookie_security_production():
    settings = Settings(environment="production")
    try:
        settings.validate_cookie_security(bind_host="127.0.0.1", cookie_secure=False)
        raise AssertionError("应该抛出 ValueError")
    except ValueError:
        pass


def test_cookie_security_non_loopback():
    settings = Settings(environment="development")
    try:
        settings.validate_cookie_security(bind_host="0.0.0.0", cookie_secure=False)
        raise AssertionError("应该抛出 ValueError")
    except ValueError:
        pass


def test_environment_rejects_unknown_values():
    """environment 必须拒绝非 production/development/test 的值。"""
    from pydantic import ValidationError

    try:
        Settings(environment="staging")  # type: ignore[arg-type]
        raise AssertionError("应该抛出 ValidationError")
    except ValidationError:
        pass
