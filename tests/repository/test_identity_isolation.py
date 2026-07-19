from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from threading import Event, Thread
from time import monotonic
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


@pytest.mark.parametrize("revocation_scope", ["family", "user"])
def test_refresh_revocation_serializes_with_rotation_and_revokes_the_new_token(
    identity_database: psycopg.Connection[tuple[object, ...]],
    isolated_database_url: str,
    revocation_scope: str,
) -> None:
    kindergarten_id = _insert_kindergarten(identity_database, "并发测试园")
    user_id = _insert_user(identity_database, kindergarten_id, "concurrent-user")
    family_id = uuid4()
    current_id = uuid4()
    now = datetime.now(UTC)
    expires_at = now + timedelta(days=7)
    identity_database.execute(
        """INSERT INTO refresh_tokens
        (id, kindergarten_id, user_id, token_family_id, token_hash, issued_at, expires_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        (current_id, kindergarten_id, user_id, family_id, "current", now, expires_at),
    )
    identity_database.execute(
        """INSERT INTO refresh_tokens
        (id, kindergarten_id, user_id, token_family_id, token_hash, issued_at, expires_at,
         revoked_at, revoke_reason, replaced_by_id)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (
            uuid4(),
            kindergarten_id,
            user_id,
            family_id,
            "replayed",
            now - timedelta(minutes=1),
            expires_at,
            now,
            "rotated",
            current_id,
        ),
    )
    identity_database.commit()

    rotation_inserted = Event()
    revocation_attempted = Event()
    allow_rotation_commit = Event()
    replay_backend_ready = Event()
    replay_backend_pid: list[int] = []
    errors: list[BaseException] = []
    dsn = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)

    def rotate() -> None:
        try:
            with psycopg.connect(dsn) as connection, connection.transaction():
                repository = IdentityRepository(connection, kindergarten_id)
                current = repository.get_refresh("current", lock=True)
                assert current is not None
                repository.rotate_refresh(
                    current,
                    new_hash="new",
                    now=now + timedelta(seconds=1),
                )
                rotation_inserted.set()
                assert allow_rotation_commit.wait(timeout=5)
        except Exception as exc:  # pragma: no cover - surfaced by the main thread
            errors.append(exc)
            rotation_inserted.set()
            allow_rotation_commit.set()

    def replay() -> None:
        try:
            assert rotation_inserted.wait(timeout=5)
            with psycopg.connect(dsn) as connection, connection.transaction():
                repository = IdentityRepository(connection, kindergarten_id)
                replay_backend_pid.append(
                    int(connection.execute("SELECT pg_backend_pid()").fetchone()[0])  # type: ignore[index]
                )
                replay_backend_ready.set()
                revocation_attempted.set()
                if revocation_scope == "family":
                    replayed = repository.get_refresh("replayed", lock=True)
                    assert replayed is not None
                    repository.revoke_family(replayed.token_family_id, reason="replay")
                else:
                    repository.revoke_user_sessions(user_id, reason="password_reset")
        except Exception as exc:  # pragma: no cover - surfaced by the main thread
            errors.append(exc)
            replay_backend_ready.set()
            revocation_attempted.set()

    rotation_thread = Thread(target=rotate)
    replay_thread = Thread(target=replay)
    rotation_thread.start()
    replay_thread.start()
    assert replay_backend_ready.wait(timeout=5)
    assert revocation_attempted.wait(timeout=5)
    assert replay_backend_pid
    deadline = monotonic() + 5
    while monotonic() < deadline:
        wait_state = identity_database.execute(
            "SELECT wait_event_type FROM pg_stat_activity WHERE pid=%s",
            (replay_backend_pid[0],),
        ).fetchone()
        if wait_state == ("Lock",):
            break
        Event().wait(0.01)
    else:
        pytest.fail("重放事务未进入预期的数据库锁等待")
    allow_rotation_commit.set()
    rotation_thread.join(timeout=10)
    replay_thread.join(timeout=10)

    assert not rotation_thread.is_alive()
    assert not replay_thread.is_alive()
    assert errors == []
    expected_reason = "replay" if revocation_scope == "family" else "password_reset"
    assert identity_database.execute(
        """SELECT count(DISTINCT expires_at), count(*), count(revoked_at),
        array_agg(DISTINCT revoke_reason ORDER BY revoke_reason)
        FROM refresh_tokens WHERE kindergarten_id=%s AND token_family_id=%s""",
        (kindergarten_id, family_id),
    ).fetchone() == (1, 3, 3, [expected_reason])
