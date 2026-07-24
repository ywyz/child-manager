from datetime import UTC, datetime, timedelta
from typing import Any, cast
from uuid import uuid4

import pytest

from packages.backend.identity.service import IdentityError, IdentityService, SessionUser


def _session(
    *,
    authentication_method: str,
    webauthn_verified_at: datetime | None = None,
    backup_reauthenticated_at: datetime | None = None,
) -> SessionUser:
    return SessionUser(
        user=cast(Any, object()),
        role_codes=["admin"],
        token_family_id=uuid4(),
        session_id=uuid4(),
        last_reauthenticated_at=webauthn_verified_at,
        authentication_method=authentication_method,
        webauthn_verified_at=webauthn_verified_at,
        backup_verified_at=None,
        backup_reauthenticated_at=backup_reauthenticated_at,
        backup_auth_version=1 if authentication_method != "webauthn" else None,
    )


def test_restricted_enrollment_session_cannot_enter_business_routes() -> None:
    session = _session(
        authentication_method="restricted_enrollment",
        webauthn_verified_at=datetime.now(UTC),
    )

    with pytest.raises(IdentityError) as raised:
        IdentityService.require_business_access(session)

    assert raised.value.code == "auth.backup_enrollment_required"
    assert session.capabilities == ["backup:enroll"]


def test_recent_webauthn_proof_satisfies_high_risk_identity_boundary() -> None:
    session = _session(
        authentication_method="webauthn",
        webauthn_verified_at=datetime.now(UTC) - timedelta(minutes=4),
    )

    IdentityService.require_recent_webauthn(session)
    IdentityService.require_add_passkey_authorization(session)


def test_backup_reauthentication_only_authorizes_add_passkey_for_five_minutes() -> None:
    session = _session(
        authentication_method="password_totp",
        backup_reauthenticated_at=datetime.now(UTC) - timedelta(minutes=4),
    )

    IdentityService.require_recent_backup_reauthentication(
        session,
        purpose="add_passkey",
    )
    IdentityService.require_add_passkey_authorization(session)

    with pytest.raises(IdentityError):
        IdentityService.require_recent_backup_reauthentication(
            session,
            purpose="manage_credentials",
        )
    with pytest.raises(IdentityError):
        IdentityService.require_recent_webauthn(session)


def test_expired_backup_reauthentication_cannot_add_passkey() -> None:
    session = _session(
        authentication_method="password_totp",
        backup_reauthenticated_at=datetime.now(UTC) - timedelta(minutes=6),
    )

    with pytest.raises(IdentityError) as raised:
        IdentityService.require_add_passkey_authorization(session)

    assert raised.value.code == "auth.backup_reauthentication_required"
