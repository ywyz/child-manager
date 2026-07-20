import pytest

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


# --- Trusted BFF Peer 配置化（Issue #6 M2 Final Fix Area 2）---


def test_trusted_bff_peers_development_default_supports_local() -> None:
    """development 默认包含回环地址，支持本地 BFF 转发。"""
    settings = Settings(environment="development")
    peers = {p.strip().lower() for p in settings.trusted_bff_peers}
    assert "127.0.0.1" in peers


def test_trusted_bff_peers_test_default_supports_local() -> None:
    """test 默认包含回环地址，支持本地测试 BFF 转发。"""
    settings = Settings(environment="test")
    peers = {p.strip().lower() for p in settings.trusted_bff_peers}
    assert "127.0.0.1" in peers


def test_trusted_bff_peers_production_default_empty() -> None:
    """production 默认为空，必须显式配置才能信任 BFF peer。

    硬编码回环地址会让生产部署在非回环拓扑下静默信任错误的内部转发头。
    """
    settings = Settings(environment="production")
    assert settings.trusted_bff_peers == []


def test_trusted_bff_peers_can_be_overridden() -> None:
    """trusted_bff_peers 可通过配置显式覆盖。"""
    settings = Settings(environment="production", trusted_bff_peers=["10.0.0.5"])
    assert settings.trusted_bff_peers == ["10.0.0.5"]


# --- Cookie Secure Policy（Issue #6 M2 Final Fix Area 3）---


def test_cookie_secure_production_defaults_true() -> None:
    """production 默认 Secure=true。"""
    settings = Settings(environment="production")
    assert settings.cookie_secure is True


def test_cookie_secure_development_defaults_false() -> None:
    """development 允许默认 Secure=false。"""
    settings = Settings(environment="development")
    assert settings.cookie_secure is False


def test_cookie_secure_test_defaults_true() -> None:
    """test 禁止默认关闭 Secure；默认必须为 true。

    旧版 secure=environment=='production' 让 test 默认 Secure=false，
    无法发现 Secure 相关回归。test 默认必须与 production 一致为 true；
    如测试确实需要关闭，必须显式配置。
    """
    settings = Settings(environment="test")
    assert settings.cookie_secure is True


def test_cookie_secure_test_env_forces_secure_true() -> None:
    """test 环境强制 Secure=true，显式 cookie_secure=False 必须被拒绝。

    Codex M2 Final Contract Freeze M2-F03：test 默认并强制 Secure=true。
    production/test 均不接受 cookie_secure=False；仅 development 在回环绑定下
    允许关闭 Secure。
    """
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        Settings(environment="test", cookie_secure=False)


def test_cookie_security_test_env_rejects_false() -> None:
    """validate_cookie_security 在 test 环境必须拒绝 cookie_secure=False。

    Codex M2-F03：test 强制 Secure=true；仅 development 显式回环本地调试
    允许 false。test 环境即使绑定回环地址也不得关闭 Secure。
    """
    settings = Settings(environment="test")
    with pytest.raises(ValueError, match="非开发环境必须启用 Cookie Secure"):
        settings.validate_cookie_security(bind_host="127.0.0.1", cookie_secure=False)
