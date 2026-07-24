from datetime import UTC, datetime, timedelta
from uuid import uuid4

import psycopg
import pytest
from alembic import command
from alembic.config import Config
from alembic.script import Script, ScriptDirectory

REVISION = "0005_password_totp_backup_login"
DOWN_REVISION = "0004_settings"


def _backup_revision() -> Script:
    revisions = {
        revision.revision: revision
        for revision in ScriptDirectory.from_config(Config("alembic.ini")).walk_revisions()
    }
    revision = revisions.get(REVISION)
    assert revision is not None, "T010 尚未创建 0005 迁移"
    return revision


def test_backup_auth_migration_creates_isolated_credentials_and_enrollments(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _backup_revision()
    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    command.upgrade(Config("alembic.ini"), REVISION)
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        expected_tables = {"backup_auth_credentials", "backup_auth_enrollments"}
        tables = {
            str(row[0])
            for row in connection.execute(
                "SELECT tablename FROM pg_tables WHERE schemaname=current_schema()"
            ).fetchall()
        }
        credential_columns = {
            str(row[0])
            for row in connection.execute(
                """SELECT column_name FROM information_schema.columns
                WHERE table_schema=current_schema()
                  AND table_name='backup_auth_credentials'"""
            ).fetchall()
        }
        enrollment_columns = {
            str(row[0])
            for row in connection.execute(
                """SELECT column_name FROM information_schema.columns
                WHERE table_schema=current_schema()
                  AND table_name='backup_auth_enrollments'"""
            ).fetchall()
        }
        user_columns = {
            str(row[0])
            for row in connection.execute(
                """SELECT column_name FROM information_schema.columns
                WHERE table_schema=current_schema() AND table_name='users'"""
            ).fetchall()
        }
        refresh_columns = {
            str(row[0])
            for row in connection.execute(
                """SELECT column_name FROM information_schema.columns
                WHERE table_schema=current_schema() AND table_name='refresh_tokens'"""
            ).fetchall()
        }

    assert expected_tables <= tables
    assert {
        "kindergarten_id",
        "user_id",
        "password_hash",
        "totp_ciphertext",
        "totp_nonce",
        "last_accepted_counter",
    } <= credential_columns
    assert {
        "kindergarten_id",
        "user_id",
        "session_token_id",
        "expires_at",
        "consumed_at",
        "invalidated_at",
    } <= enrollment_columns
    assert "backup_auth_version" in user_columns
    assert {
        "authentication_method",
        "webauthn_verified_at",
        "backup_verified_at",
        "backup_reauthenticated_at",
        "backup_auth_version",
    } <= refresh_columns
    assert {"password_hash", "totp_ciphertext"}.isdisjoint(user_columns)


def test_backup_auth_revision_is_the_only_child_of_settings() -> None:
    revision = _backup_revision()
    script = ScriptDirectory.from_config(Config("alembic.ini"))

    assert revision.down_revision == DOWN_REVISION
    assert script.get_heads() == [REVISION]


def test_backup_auth_migration_downgrades_to_settings_without_restoring_legacy_passwords(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _backup_revision()
    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    config = Config("alembic.ini")
    command.upgrade(config, REVISION)
    command.downgrade(config, DOWN_REVISION)
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)

    with psycopg.connect(native_url) as connection:
        version = connection.execute("SELECT version_num FROM alembic_version").fetchone()
        tables = {
            str(row[0])
            for row in connection.execute(
                "SELECT tablename FROM pg_tables WHERE schemaname=current_schema()"
            ).fetchall()
        }
        user_columns = {
            str(row[0])
            for row in connection.execute(
                """SELECT column_name FROM information_schema.columns
                WHERE table_schema=current_schema() AND table_name='users'"""
            ).fetchall()
        }

    assert version == (DOWN_REVISION,)
    assert {"backup_auth_credentials", "backup_auth_enrollments"}.isdisjoint(tables)
    assert {"password_hash", "password_changed_at"}.isdisjoint(user_columns)


def test_existing_sessions_are_marked_webauthn_or_revoked_during_upgrade(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _backup_revision()
    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    config = Config("alembic.ini")
    command.upgrade(config, DOWN_REVISION)
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    kindergarten_id = uuid4()
    user_id = uuid4()
    refresh_id = uuid4()
    now = datetime.now(UTC)
    with psycopg.connect(native_url) as connection:
        connection.execute(
            "INSERT INTO kindergartens (id, name) VALUES (%s, %s)",
            (kindergarten_id, "迁移会话测试园"),
        )
        connection.execute(
            """INSERT INTO users
            (id, kindergarten_id, username, username_normalized, display_name,
             webauthn_user_handle, status, activated_at)
            VALUES (%s,%s,%s,%s,%s,%s,'active',%s)""",
            (
                user_id,
                kindergarten_id,
                "migration-user",
                "migration-user",
                "迁移用户",
                bytes(range(32)),
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
                "migration-refresh-hash",
                now,
                now + timedelta(days=7),
            ),
        )
    command.upgrade(config, REVISION)

    with psycopg.connect(native_url) as connection:
        row = connection.execute(
            """SELECT authentication_method, revoked_at
            FROM refresh_tokens WHERE id=%s""",
            (refresh_id,),
        ).fetchone()

    assert row is not None
    assert row[0] == "webauthn" or row[1] is not None
