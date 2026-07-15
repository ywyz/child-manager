import os
from unittest.mock import patch

import pytest

from packages.backend.bootstrap.config import Settings


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


def test_database_url_construction():
    settings = Settings(
        database_user="test_user",
        database_password="test_pass",
        postgres_host="localhost",
        postgres_port=5432,
        database_name="test_db",
    )

    expected = (
        "postgresql+psycopg://test_user:test_pass@localhost:5432/test_db"
    )
    assert settings.resolved_database_url == expected


def test_custom_database_url_override():
    custom_url = (
        "postgresql+psycopg://custom_user:custom_pass"
        "@custom_host:5432/custom_db"
    )
    settings = Settings(database_url=custom_url)

    assert settings.resolved_database_url == custom_url


def test_redis_url_construction():
    settings = Settings(redis_host="localhost", redis_port=6379)

    assert settings.resolved_redis_url == "redis://localhost:6379/0"


def test_custom_redis_url_override():
    custom_url = "redis://custom_host:6379/1"
    settings = Settings(redis_url=custom_url)

    assert settings.resolved_redis_url == custom_url


def test_jwt_secret_is_empty_by_default():
    settings = Settings()

    assert settings.jwt_secret_key == ""


def test_allowed_hosts_contains_localhost():
    settings = Settings()

    assert "localhost" in settings.allowed_hosts
    assert "127.0.0.1" in settings.allowed_hosts