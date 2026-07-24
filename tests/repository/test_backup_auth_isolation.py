from collections.abc import Sequence
from typing import Any, cast
from uuid import UUID, uuid4

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
