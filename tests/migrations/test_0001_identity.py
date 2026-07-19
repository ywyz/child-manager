"""身份与审计迁移约束测试。"""

import os
from collections.abc import Iterator

import pytest
from alembic.command import upgrade
from alembic.config import Config
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.types import UUID, VARCHAR

from tests.conftest import IS_POSTGRESQL


@pytest.fixture
def upgraded_engine(isolated_database_url: str) -> Iterator[Engine]:
    os.environ["CHILD_MANAGER_DATABASE_URL"] = isolated_database_url
    config = Config("alembic.ini")
    upgrade(config, "0006_reconcile_identity_schema")

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
    assert "is_active" in columns
    assert "created_at" in columns
    assert "updated_at" in columns
    assert isinstance(columns["id"]["type"], (UUID, VARCHAR))


@pytest.mark.skipif(not IS_POSTGRESQL, reason="身份迁移需要 PostgreSQL")
def test_roles_global(upgraded_engine: Engine) -> None:
    inspector = inspect(upgraded_engine)
    columns = {c["name"]: c for c in inspector.get_columns("roles")}
    assert "code" in columns
    assert "name" in columns
    assert "is_system" in columns
    assert "kindergarten_id" not in columns
    assert "created_at" not in columns
    assert "updated_at" not in columns

    constraints = inspector.get_unique_constraints("roles")
    names = {uc["name"] for uc in constraints if uc.get("name")}
    assert "uq_roles_code" in names


@pytest.mark.skipif(not IS_POSTGRESQL, reason="身份迁移需要 PostgreSQL")
def test_user_columns_and_constraints(upgraded_engine: Engine) -> None:
    inspector = inspect(upgraded_engine)
    columns = {c["name"]: c for c in inspector.get_columns("users")}
    required = {
        "username",
        "username_normalized",
        "phone_e164",
        "display_name",
        "password_hash",
        "is_active",
        "password_changed_at",
        "last_login_at",
        "created_by",
        "updated_by",
    }
    assert required <= set(columns)
    assert isinstance(columns["id"]["type"], (UUID, VARCHAR))
    assert isinstance(columns["kindergarten_id"]["type"], (UUID, VARCHAR))

    constraints = inspector.get_unique_constraints("users")
    names = {uc["name"] for uc in constraints if uc.get("name")}
    assert "uq_users_kindergarten_username" in names


@pytest.mark.skipif(not IS_POSTGRESQL, reason="身份迁移需要 PostgreSQL")
def test_user_roles_composite_primary_key(upgraded_engine: Engine) -> None:
    inspector = inspect(upgraded_engine)
    pk = inspector.get_pk_constraint("user_roles")
    assert set(pk["constrained_columns"]) == {
        "kindergarten_id",
        "user_id",
        "role_id",
    }

    fks = inspector.get_foreign_keys("user_roles")
    assert len(fks) >= 3
    constrained_columns = {col for fk in fks for col in fk["constrained_columns"]}
    assert {"kindergarten_id", "user_id", "role_id", "assigned_by"} <= constrained_columns


@pytest.mark.skipif(not IS_POSTGRESQL, reason="身份迁移需要 PostgreSQL")
def test_refresh_token_columns(upgraded_engine: Engine) -> None:
    inspector = inspect(upgraded_engine)
    columns = {c["name"]: c for c in inspector.get_columns("refresh_tokens")}
    required = {
        "user_id",
        "token_family_id",
        "token_hash",
        "issued_at",
        "expires_at",
        "last_used_at",
        "revoked_at",
        "revoke_reason",
        "replaced_by_id",
        "client_label",
    }
    assert required <= set(columns)
    assert isinstance(columns["id"]["type"], (UUID, VARCHAR))
    # 冻结 Schema §5.5 未定义 family 级过期/撤销列；0006 收敛移除 0003/0005 引入的这两列。
    assert "family_expires_at" not in columns
    assert "family_revoked_at" not in columns


@pytest.mark.skipif(not IS_POSTGRESQL, reason="身份迁移需要 PostgreSQL")
def test_audit_events_columns(upgraded_engine: Engine) -> None:
    inspector = inspect(upgraded_engine)
    columns = {c["name"]: c for c in inspector.get_columns("audit_events")}
    required = {
        "kindergarten_id",
        "event_code",
        "actor_user_id",
        "actor_role_codes",
        "resource_type",
        "resource_id",
        "request_id",
        "trace_id",
        "job_id",
        "outcome",
        "metadata",
        "occurred_at",
        "created_at",
        "updated_at",
    }
    assert required <= set(columns)
    assert isinstance(columns["id"]["type"], (UUID, VARCHAR))
