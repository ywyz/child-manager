from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from threading import Barrier
from typing import Any, cast
from uuid import UUID, uuid4

import psycopg
import pytest
from alembic import command
from alembic.config import Config

from packages.backend.identity.repository import IdentityRepository


class RecordingResult:
    def fetchone(self) -> None:
        return None

    def fetchall(self) -> list[tuple[object, ...]]:
        return []


class RecordingConnection:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[object, ...]]] = []

    def execute(
        self,
        statement: object,
        params: Sequence[object] = (),
    ) -> RecordingResult:
        self.calls.append((str(statement), tuple(params)))
        return RecordingResult()


def test_identity_repository_exposes_atomic_backup_auth_operations() -> None:
    required_operations = {
        "get_backup_credential",
        "start_backup_enrollment",
        "consume_backup_enrollment",
        "accept_totp_counter",
        "revoke_backup_auth",
        "list_backup_security_events",
    }

    assert required_operations <= set(dir(IdentityRepository))


def test_backup_credential_reads_are_scoped_to_kindergarten_and_user() -> None:
    connection = RecordingConnection()
    kindergarten_id = uuid4()
    user_id = uuid4()
    repository = cast(Any, IdentityRepository(connection, kindergarten_id))  # type: ignore[arg-type]

    repository.get_backup_credential(user_id)

    assert connection.calls
    for statement, params in connection.calls:
        assert "kindergarten_id" in statement.lower()
        assert kindergarten_id in params
        assert user_id in params


def test_totp_counter_consumption_is_one_atomic_tenant_scoped_update() -> None:
    connection = RecordingConnection()
    kindergarten_id = uuid4()
    credential_id = uuid4()
    repository = cast(Any, IdentityRepository(connection, kindergarten_id))  # type: ignore[arg-type]

    repository.accept_totp_counter(credential_id, 42)

    assert len(connection.calls) == 1
    statement, params = connection.calls[0]
    normalized = " ".join(statement.lower().split())
    assert normalized.startswith("update backup_auth_credentials")
    assert "last_accepted_counter <" in normalized
    assert "returning" in normalized
    assert kindergarten_id in params
    assert credential_id in params
    assert 42 in params


def test_repository_cannot_read_backup_material_from_another_kindergarten() -> None:
    connection = RecordingConnection()
    first_kindergarten = uuid4()
    second_kindergarten = uuid4()
    user_id = UUID("00000000-0000-7000-8000-000000000001")

    repository = cast(Any, IdentityRepository(connection, first_kindergarten))  # type: ignore[arg-type]
    repository.get_backup_credential(user_id)

    assert connection.calls
    assert all(first_kindergarten in params for _statement, params in connection.calls)
    assert all(second_kindergarten not in params for _statement, params in connection.calls)


def _seed_backup_repository(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[str, UUID, UUID, UUID, UUID]:
    monkeypatch.setenv("CHILD_MANAGER_DATABASE_URL", isolated_database_url)
    command.upgrade(Config("alembic.ini"), "0005_password_totp_backup_login")
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    kindergarten_id = uuid4()
    user_id = uuid4()
    webauthn_session_id = uuid4()
    backup_session_id = uuid4()
    now = datetime.now(UTC)
    with psycopg.connect(native_url) as connection:
        connection.execute(
            "INSERT INTO kindergartens (id, name) VALUES (%s, %s)",
            (kindergarten_id, "备用认证 Repository 测试园"),
        )
        connection.execute(
            """INSERT INTO users
            (id, kindergarten_id, username, username_normalized, display_name,
             webauthn_user_handle, status, activated_at)
            VALUES (%s,%s,%s,%s,%s,%s,'active',%s)""",
            (
                user_id,
                kindergarten_id,
                "backup-repository-user",
                "backup-repository-user",
                "备用认证测试用户",
                bytes(range(32)),
                now,
            ),
        )
        connection.execute(
            """INSERT INTO refresh_tokens
            (id, kindergarten_id, user_id, token_family_id, token_hash, issued_at, expires_at,
             authentication_method, webauthn_verified_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,'webauthn',%s)""",
            (
                webauthn_session_id,
                kindergarten_id,
                user_id,
                webauthn_session_id,
                f"webauthn-{webauthn_session_id}",
                now,
                now + timedelta(days=7),
                now,
            ),
        )
        connection.execute(
            """INSERT INTO refresh_tokens
            (id, kindergarten_id, user_id, token_family_id, token_hash, issued_at, expires_at,
             authentication_method, backup_verified_at, backup_auth_version)
            VALUES (%s,%s,%s,%s,%s,%s,%s,'password_totp',%s,1)""",
            (
                backup_session_id,
                kindergarten_id,
                user_id,
                backup_session_id,
                f"backup-{backup_session_id}",
                now,
                now + timedelta(days=7),
                now,
            ),
        )
    return native_url, kindergarten_id, user_id, webauthn_session_id, backup_session_id


def test_new_backup_enrollment_atomically_supersedes_the_previous_one(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    native_url, kindergarten_id, user_id, webauthn_session_id, _backup_session_id = (
        _seed_backup_repository(isolated_database_url, monkeypatch)
    )
    now = datetime.now(UTC)
    with psycopg.connect(native_url) as connection:
        repository = IdentityRepository(connection, kindergarten_id)
        first = repository.start_backup_enrollment(
            user_id=user_id,
            session_token_id=webauthn_session_id,
            totp_ciphertext=b"first-encrypted-secret",
            totp_nonce=bytes(range(12)),
            totp_key_id="test-key",
            totp_envelope_version=1,
            expires_at=now + timedelta(minutes=10),
        )
        second = repository.start_backup_enrollment(
            user_id=user_id,
            session_token_id=webauthn_session_id,
            totp_ciphertext=b"second-encrypted-secret",
            totp_nonce=bytes(reversed(range(12))),
            totp_key_id="test-key",
            totp_envelope_version=1,
            expires_at=now + timedelta(minutes=10),
        )
        rows = connection.execute(
            """SELECT id, invalidation_reason FROM backup_auth_enrollments
            WHERE kindergarten_id=%s AND user_id=%s ORDER BY created_at, id""",
            (kindergarten_id, user_id),
        ).fetchall()

    assert first.id != second.id
    assert rows == [(first.id, "superseded"), (second.id, None)]


def test_concurrent_totp_counter_consumption_succeeds_only_once(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    native_url, kindergarten_id, user_id, _webauthn_session_id, _backup_session_id = (
        _seed_backup_repository(isolated_database_url, monkeypatch)
    )
    credential_id = uuid4()
    now = datetime.now(UTC)
    with psycopg.connect(native_url) as connection:
        connection.execute(
            """INSERT INTO backup_auth_credentials
            (id, kindergarten_id, user_id, status, password_hash, password_changed_at,
             totp_ciphertext, totp_nonce, totp_key_id, totp_envelope_version, enabled_at)
            VALUES (%s,%s,%s,'enabled',%s,%s,%s,%s,%s,1,%s)""",
            (
                credential_id,
                kindergarten_id,
                user_id,
                "$argon2id$test-only",
                now,
                b"encrypted-test-secret",
                bytes(range(12)),
                "test-key",
                now,
            ),
        )

    barrier = Barrier(2)

    def consume() -> bool:
        with psycopg.connect(native_url) as connection:
            repository = IdentityRepository(connection, kindergarten_id)
            barrier.wait()
            return repository.accept_totp_counter(credential_id, 42)

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _index: consume(), range(2)))

    assert sorted(results) == [False, True]


def test_backup_version_change_revokes_only_related_sessions(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    native_url, kindergarten_id, user_id, webauthn_session_id, backup_session_id = (
        _seed_backup_repository(isolated_database_url, monkeypatch)
    )
    now = datetime.now(UTC)
    with psycopg.connect(native_url) as connection:
        repository = IdentityRepository(connection, kindergarten_id)
        repository.save_backup_credential(
            credential_id=uuid4(),
            user_id=user_id,
            password_hash="$argon2id$test-only",
            password_changed_at=now,
            totp_ciphertext=b"encrypted-test-secret",
            totp_nonce=bytes(range(12)),
            totp_key_id="test-key",
            totp_envelope_version=1,
            enabled_at=now,
            last_accepted_counter=41,
        )
        result = repository.revoke_backup_auth(user_id, reason="backup_factor_changed")
        sessions = dict(
            connection.execute(
                """SELECT id, revoked_at FROM refresh_tokens
                WHERE kindergarten_id=%s AND user_id=%s""",
                (kindergarten_id, user_id),
            ).fetchall()
        )
        credential = repository.get_backup_credential(user_id)

    assert result.backup_auth_version == 2
    assert result.sessions_revoked == 1
    assert sessions[webauthn_session_id] is None
    assert sessions[backup_session_id] is not None
    assert credential is not None
    assert credential.status == "revoked"
    assert credential.password_hash is None
    assert credential.totp_ciphertext is None


def test_admin_role_gate_restricts_and_then_releases_webauthn_sessions(
    isolated_database_url: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    native_url, kindergarten_id, user_id, webauthn_session_id, _backup_session_id = (
        _seed_backup_repository(isolated_database_url, monkeypatch)
    )
    now = datetime.now(UTC)
    with psycopg.connect(native_url) as connection:
        connection.execute(
            """INSERT INTO user_roles
            (kindergarten_id, user_id, role_id, assigned_by, assigned_at)
            SELECT %s,%s,id,%s,%s FROM roles WHERE code='admin'""",
            (kindergarten_id, user_id, user_id, now),
        )
        repository = IdentityRepository(connection, kindergarten_id)

        assert repository.recalculate_backup_enrollment_gate(user_id) is True
        restricted = connection.execute(
            """SELECT authentication_method, backup_auth_version
            FROM refresh_tokens WHERE kindergarten_id=%s AND id=%s""",
            (kindergarten_id, webauthn_session_id),
        ).fetchone()

        repository.save_backup_credential(
            credential_id=uuid4(),
            user_id=user_id,
            password_hash="$argon2id$test-only",
            password_changed_at=now,
            totp_ciphertext=b"encrypted-test-secret",
            totp_nonce=bytes(range(12)),
            totp_key_id="test-key",
            totp_envelope_version=1,
            enabled_at=now,
            last_accepted_counter=41,
        )
        assert repository.recalculate_backup_enrollment_gate(user_id) is False
        released = connection.execute(
            """SELECT authentication_method, backup_auth_version
            FROM refresh_tokens WHERE kindergarten_id=%s AND id=%s""",
            (kindergarten_id, webauthn_session_id),
        ).fetchone()

    assert restricted == ("restricted_enrollment", 1)
    assert released == ("webauthn", None)
