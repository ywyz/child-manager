import pytest

from packages.backend.config import Settings


def test_settings_defaults_use_loopback():
    settings = Settings()

    assert settings.api_host == "127.0.0.1"
    assert settings.web_host == "127.0.0.1"


def test_settings_prohibits_non_loopback_host():
    with pytest.raises(ValueError, match="必须使用回环地址"):
        Settings(api_host="0.0.0.0")

    with pytest.raises(ValueError, match="必须使用回环地址"):
        Settings(web_host="192.168.1.1")

    with pytest.raises(ValueError, match="必须使用回环地址"):
        Settings(api_host="example.com")


def test_settings_allows_localhost():
    settings = Settings(api_host="localhost", web_host="localhost")

    assert settings.api_host == "localhost"
    assert settings.web_host == "localhost"


def test_database_url_direct():
    custom_url = "postgresql+psycopg://test_user:test_pass@localhost:5432/test_db"
    settings = Settings(database_url=custom_url)

    assert settings.database_url == custom_url


def test_redis_url_direct():
    custom_url = "redis://localhost:6379/0"
    settings = Settings(redis_url=custom_url)

    assert settings.redis_url == custom_url


def test_jwt_signing_key_is_empty_by_default(monkeypatch):
    monkeypatch.delenv("CHILD_MANAGER_JWT_SIGNING_KEY", raising=False)
    monkeypatch.delenv("CHILD_MANAGER_CSRF_SIGNING_KEY", raising=False)
    settings = Settings()

    assert settings.jwt_signing_key == ""


def test_allowed_hosts_contains_localhost():
    settings = Settings()

    assert "localhost" in settings.allowed_hosts
    assert "127.0.0.1" in settings.allowed_hosts


def test_cookie_security_development_loopback():
    settings = Settings(environment="development")
    settings.validate_cookie_security(bind_host="127.0.0.1", cookie_secure=False)


def test_cookie_security_production_requires_secure():
    settings = Settings(environment="production")
    with pytest.raises(ValueError, match="非开发环境必须启用 Cookie Secure"):
        settings.validate_cookie_security(bind_host="127.0.0.1", cookie_secure=False)


def test_cookie_security_non_loopback_rejected():
    settings = Settings(environment="development")
    with pytest.raises(ValueError, match="关闭 Cookie Secure 时只能绑定回环地址"):
        settings.validate_cookie_security(bind_host="0.0.0.0", cookie_secure=False)
