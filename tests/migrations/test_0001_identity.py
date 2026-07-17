"""身份与审计迁移约束测试。"""

import os
from collections.abc import Iterator

import pytest
from alembic.command import upgrade
from alembic.config import Config
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine

from tests.conftest import IS_POSTGRESQL


@pytest.fixture
def upgraded_engine(isolated_database_url: str) -> Iterator[Engine]:
    os.environ["CHILD_MANAGER_DATABASE_URL"] = isolated_database_url
    config = Config("alembic.ini")
    upgrade(config, "0001_identity_and_audit")

    engine = create_engine(isolated_database_url)
    yield engine
    engine.dispose()


@pytest.mark.skipif(not IS_POSTGRESQL, reason="身份迁移需要 PostgreSQL")
def test_identity_tables_exist(upgraded_engine: Engine) -> None:
    inspector = inspect(upgraded_engine)
    tables = set(inspector.get_table_names())
    required = {
        "kindergartens",
        "roles",
        "users",
        "user_roles",
        "refresh_tokens",
        "audit_events",
    }
    assert required <= tables


@pytest.mark.skipif(not IS_POSTGRESQL, reason="身份迁移需要 PostgreSQL")
def test_kindergarten_columns(upgraded_engine: Engine) -> None:
    inspector = inspect(upgraded_engine)
    columns = {c["name"]: c for c in inspector.get_columns("kindergartens")}
    assert "name" in columns
    assert "timezone" in columns
    assert "created_at" in columns
    assert "updated_at" in columns


@pytest.mark.skipif(not IS_POSTGRESQL, reason="身份迁移需要 PostgreSQL")
def test_user_unique_constraints(upgraded_engine: Engine) -> None:
    inspector = inspect(upgraded_engine)
    constraints = inspector.get_unique_constraints("users")
    names = {uc["name"] for uc in constraints if uc.get("name")}
    assert any("username" in (name or "").lower() for name in names)


@pytest.mark.skipif(not IS_POSTGRESQL, reason="身份迁移需要 PostgreSQL")
def test_roles_unique_per_kindergarten(upgraded_engine: Engine) -> None:
    inspector = inspect(upgraded_engine)
    constraints = inspector.get_unique_constraints("roles")
    names = {uc["name"] for uc in constraints if uc.get("name")}
    assert any("code" in (name or "").lower() for name in names)


@pytest.mark.skipif(not IS_POSTGRESQL, reason="身份迁移需要 PostgreSQL")
def test_user_roles_composite_foreign_keys(upgraded_engine: Engine) -> None:
    inspector = inspect(upgraded_engine)
    fks = inspector.get_foreign_keys("user_roles")
    assert len(fks) >= 2
    constrained_columns = {col for fk in fks for col in fk["constrained_columns"]}
    assert {"kindergarten_id", "user_id", "role_id"} <= constrained_columns


@pytest.mark.skipif(not IS_POSTGRESQL, reason="身份迁移需要 PostgreSQL")
def test_refresh_token_columns(upgraded_engine: Engine) -> None:
    inspector = inspect(upgraded_engine)
    columns = {c["name"]: c for c in inspector.get_columns("refresh_tokens")}
    assert {"user_id", "family_id", "token_hash", "expires_at", "revoked_at"} <= set(columns)


@pytest.mark.skipif(not IS_POSTGRESQL, reason="身份迁移需要 PostgreSQL")
def test_audit_events_columns(upgraded_engine: Engine) -> None:
    inspector = inspect(upgraded_engine)
    columns = {c["name"]: c for c in inspector.get_columns("audit_events")}
    required = {
        "kindergarten_id",
        "event_type",
        "actor_user_id",
        "resource_type",
        "resource_id",
        "result",
        "event_metadata",
        "created_at",
    }
    assert required <= set(columns)
