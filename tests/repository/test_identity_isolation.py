from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import psycopg
import pytest
from alembic import command
from alembic.config import Config
from psycopg.errors import ForeignKeyViolation, UniqueViolation

from packages.backend.identity.repository import IdentityRepository


@pytest.fixture
def identity_database(
    isolated_database_url: str, monkeypatch: pytest.MonkeyPatch
) -> Iterator[psycopg.Connection[tuple[object, ...]]]:
    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    command.upgrade(Config("alembic.ini"), "head")
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        yield connection


def _insert_kindergarten(connection: psycopg.Connection[tuple[object, ...]], name: str) -> UUID:
    kindergarten_id = uuid4()
    connection.execute(
        "INSERT INTO kindergartens (id, name) VALUES (%s, %s)", (kindergarten_id, name)
    )
    return kindergarten_id


def _insert_user(
    connection: psycopg.Connection[tuple[object, ...]],
    kindergarten_id: UUID,
    username: str,
    phone: str | None = None,
) -> UUID:
    user_id = uuid4()
    connection.execute(
        """INSERT INTO users
        (id, kindergarten_id, username, username_normalized, phone_e164, display_name,
         password_hash, password_changed_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
        (
            user_id,
            kindergarten_id,
            username,
            username,
            phone,
            username,
            "$argon2id$test",
            datetime.now(UTC),
        ),
    )
    return user_id


def test_username_and_non_null_phone_are_unique_only_within_kindergarten(
    identity_database: psycopg.Connection[tuple[object, ...]],
) -> None:
    first = _insert_kindergarten(identity_database, "一园")
    second = _insert_kindergarten(identity_database, "二园")
    _insert_user(identity_database, first, "teacher", "+8613800138000")
    _insert_user(identity_database, second, "teacher", "+8613800138000")
    with pytest.raises(UniqueViolation), identity_database.transaction():
        _insert_user(identity_database, first, "teacher", None)
    with pytest.raises(UniqueViolation), identity_database.transaction():
        _insert_user(identity_database, first, "different-teacher", "+8613800138000")


def test_cross_kindergarten_role_assignment_is_rejected_by_composite_foreign_key(
    identity_database: psycopg.Connection[tuple[object, ...]],
) -> None:
    first = _insert_kindergarten(identity_database, "一园")
    second = _insert_kindergarten(identity_database, "二园")
    user = _insert_user(identity_database, first, "admin")
    assigner = _insert_user(identity_database, second, "other-admin")
    role_row = identity_database.execute("SELECT id FROM roles WHERE code = 'admin'").fetchone()
    assert role_row is not None
    role_id = role_row[0]
    with pytest.raises(ForeignKeyViolation), identity_database.transaction():
        identity_database.execute(
            """INSERT INTO user_roles
            (kindergarten_id, user_id, role_id, assigned_by, assigned_at)
            VALUES (%s,%s,%s,%s,%s)""",
            (first, user, role_id, assigner, datetime.now(UTC)),
        )


def test_refresh_replacement_cannot_cross_kindergarten(
    identity_database: psycopg.Connection[tuple[object, ...]],
) -> None:
    first = _insert_kindergarten(identity_database, "一园")
    second = _insert_kindergarten(identity_database, "二园")
    first_user = _insert_user(identity_database, first, "first")
    second_user = _insert_user(identity_database, second, "second")
    now = datetime.now(UTC)
    replacement = uuid4()
    identity_database.execute(
        """INSERT INTO refresh_tokens
        (id, kindergarten_id, user_id, token_family_id, token_hash, issued_at, expires_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        (replacement, second, second_user, uuid4(), "replacement", now, now + timedelta(days=7)),
    )
    with pytest.raises(ForeignKeyViolation), identity_database.transaction():
        identity_database.execute(
            """INSERT INTO refresh_tokens
            (id, kindergarten_id, user_id, token_family_id, token_hash, issued_at,
             expires_at, revoked_at, replaced_by_id)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (
                uuid4(),
                first,
                first_user,
                uuid4(),
                "old",
                now,
                now + timedelta(days=7),
                now,
                replacement,
            ),
        )


def test_repository_refuses_to_deactivate_last_active_admin(
    identity_database: psycopg.Connection[tuple[object, ...]],
) -> None:
    kindergarten_id = _insert_kindergarten(identity_database, "一园")
    user_id = _insert_user(identity_database, kindergarten_id, "admin")
    role_row = identity_database.execute("SELECT id FROM roles WHERE code = 'admin'").fetchone()
    assert role_row is not None
    role_id = role_row[0]
    identity_database.execute(
        """INSERT INTO user_roles
        (kindergarten_id, user_id, role_id, assigned_by, assigned_at)
        VALUES (%s,%s,%s,%s,%s)""",
        (kindergarten_id, user_id, role_id, user_id, datetime.now(UTC)),
    )
    repository = IdentityRepository(identity_database, kindergarten_id)
    assert repository.active_admin_count() == 1
    assert repository.can_deactivate(user_id) is False
