from packages.backend.bootstrap.config import settings


def test_settings_defaults():
    assert settings.environment == "development"
    assert settings.api_host == "127.0.0.1"
    assert settings.api_port == 28000
    assert settings.web_host == "127.0.0.1"
    assert settings.web_port == 28080


def test_database_url():
    assert "postgresql+psycopg" in settings.resolved_database_url
    assert "localhost:25432" in settings.resolved_database_url
    assert "child_manager_trae" in settings.resolved_database_url


def test_redis_url():
    assert "redis://localhost:26379" in settings.resolved_redis_url


def test_jwt_settings():
    assert settings.jwt_algorithm == "HS256"
    assert settings.jwt_expire_minutes == 60


def test_allowed_hosts():
    assert "localhost" in settings.allowed_hosts
    assert "127.0.0.1" in settings.allowed_hosts


def test_database_url_override():
    from packages.backend.bootstrap.config import Settings

    overridden = Settings(
        database_url="postgresql+psycopg://user:pass@localhost:5432/test_db",
    )
    assert (
        overridden.resolved_database_url == "postgresql+psycopg://user:pass@localhost:5432/test_db"
    )


def test_redis_url_override():
    from packages.backend.bootstrap.config import Settings

    overridden = Settings(redis_url="redis://localhost:6379/1")
    assert overridden.resolved_redis_url == "redis://localhost:6379/1"
