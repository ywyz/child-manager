from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import psycopg
import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory

EXPAND_REVISION = "0002_passkey_expand"
CONTRACT_REVISION = "0003_passkey_contract"


def _native_url(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


def _user_columns(connection: psycopg.Connection[tuple[object, ...]]) -> set[str]:
    return {
        str(row[0])
        for row in connection.execute(
            """SELECT column_name FROM information_schema.columns
            WHERE table_schema=current_schema() AND table_name='users'"""
        ).fetchall()
    }


def _assert_passkey_revisions_exist() -> None:
    revisions = {
        revision.revision
        for revision in ScriptDirectory.from_config(Config("alembic.ini")).walk_revisions()
    }
    assert {EXPAND_REVISION, CONTRACT_REVISION} <= revisions


def test_passkey_migration_has_explicit_expand_and_contract_boundaries() -> None:
    _assert_passkey_revisions_exist()


def test_expand_moves_existing_accounts_to_enrollment_and_revokes_old_sessions(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _assert_passkey_revisions_exist()
    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    config = Config("alembic.ini")
    command.upgrade(config, "0001_identity_and_audit")
    kindergarten_id = uuid4()
    user_id = uuid4()
    suspended_user_id = uuid4()
    refresh_id = uuid4()
    now = datetime.now(UTC)
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        connection.execute(
            "INSERT INTO kindergartens (id, name) VALUES (%s, %s)",
            (kindergarten_id, "迁移测试园"),
        )
        connection.execute(
            """INSERT INTO users
            (id, kindergarten_id, username, username_normalized, display_name,
             password_hash, password_changed_at, is_active)
            VALUES (%s,%s,%s,%s,%s,%s,%s,false)""",
            (
                suspended_user_id,
                kindergarten_id,
                "legacy-suspended",
                "legacy-suspended",
                "旧停用账号",
                "$argon2id$legacy-suspended",
                now,
            ),
        )
        connection.execute(
            """INSERT INTO users
            (id, kindergarten_id, username, username_normalized, display_name,
             password_hash, password_changed_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (
                user_id,
                kindergarten_id,
                "legacy-admin",
                "legacy-admin",
                "旧管理员",
                "$argon2id$legacy",
                now,
            ),
        )
        connection.execute(
            """INSERT INTO refresh_tokens
            (id, kindergarten_id, user_id, token_family_id, token_hash, issued_at, expires_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (
                refresh_id,
                kindergarten_id,
                user_id,
                uuid4(),
                "legacy-refresh",
                now,
                now + timedelta(days=7),
            ),
        )

    command.upgrade(config, EXPAND_REVISION)

    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        assert connection.execute(
            "SELECT status FROM users WHERE id=%s", (user_id,)
        ).fetchone() == ("pending_registration",)
        assert connection.execute(
            "SELECT status FROM users WHERE id=%s", (suspended_user_id,)
        ).fetchone() == ("suspended",)
        refresh_row = connection.execute(
            "SELECT revoked_at, revoke_reason FROM refresh_tokens WHERE id=%s", (refresh_id,)
        ).fetchone()
        assert refresh_row is not None
        assert refresh_row[0] is not None
        assert {"password_hash", "password_changed_at"} <= _user_columns(connection)


def test_contract_removes_password_data_and_downgrade_recreates_only_empty_columns(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _assert_passkey_revisions_exist()
    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    config = Config("alembic.ini")
    command.upgrade(config, "head")
    kindergarten_id = uuid4()
    user_id = uuid4()
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        assert {"password_hash", "password_changed_at", "is_active"}.isdisjoint(
            _user_columns(connection)
        )
        connection.execute(
            "INSERT INTO kindergartens (id, name) VALUES (%s, %s)",
            (kindergarten_id, "契约降级园"),
        )
        connection.execute(
            """INSERT INTO users
            (id, kindergarten_id, username, username_normalized, display_name,
             webauthn_user_handle, status)
            VALUES (%s,%s,%s,%s,%s,%s,%s)""",
            (
                user_id,
                kindergarten_id,
                "passkey-user",
                "passkey-user",
                "通行密钥用户",
                b"u" * 32,
                "pending_registration",
            ),
        )

    command.downgrade(config, EXPAND_REVISION)

    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        columns = _user_columns(connection)
        assert {"password_hash", "password_changed_at", "is_active"} <= columns
        assert connection.execute(
            """SELECT count(*) FROM users
            WHERE password_hash IS NOT NULL OR password_changed_at IS NOT NULL
               OR is_active IS NOT NULL"""
        ).fetchone() == (0,)
