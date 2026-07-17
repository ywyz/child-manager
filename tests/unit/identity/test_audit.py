from typing import cast
from uuid import uuid4

import psycopg
import pytest

from packages.backend.audit.repository import AuditRepository
from packages.contracts.audit import IdentityAuditEventCode


def test_identity_audit_rejects_sensitive_metadata_keys() -> None:
    connection = cast(psycopg.Connection[tuple[object, ...]], object())
    repository = AuditRepository(connection, uuid4())
    with pytest.raises(ValueError, match="白名单"):
        repository.append(
            event_code=IdentityAuditEventCode.LOGIN_FAILED,
            actor_user_id=None,
            actor_role_codes=[],
            resource_type="user",
            resource_id=None,
            outcome="failure",
            metadata={"password": "不得保存"},
        )
