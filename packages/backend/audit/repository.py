"""只接受身份白名单字段的审计写入。"""

import json
from datetime import UTC, datetime
from uuid import UUID, uuid7

import psycopg

from packages.contracts.audit import IdentityAuditEventCode


class AuditRepository:
    def __init__(
        self, connection: psycopg.Connection[tuple[object, ...]], kindergarten_id: UUID
    ) -> None:
        self.connection = connection
        self.kindergarten_id = kindergarten_id

    def append(
        self,
        *,
        event_code: IdentityAuditEventCode,
        actor_user_id: UUID | None,
        actor_role_codes: list[str],
        resource_type: str,
        resource_id: UUID | None,
        outcome: str,
        request_id: UUID | None = None,
        metadata: dict[str, object] | None = None,
    ) -> None:
        safe_metadata = metadata or {}
        if set(safe_metadata) - {"reason", "source", "target_role_codes"}:
            raise ValueError("审计 metadata 包含非白名单字段")
        self.connection.execute(
            """INSERT INTO audit_events
            (id, kindergarten_id, event_code, actor_user_id, actor_role_codes, resource_type,
             resource_id, request_id, outcome, metadata, occurred_at)
            VALUES (%s,%s,%s,%s,%s::jsonb,%s,%s,%s,%s,%s::jsonb,%s)""",
            (
                uuid7(),
                self.kindergarten_id,
                event_code.value,
                actor_user_id,
                json.dumps(actor_role_codes),
                resource_type,
                resource_id,
                request_id,
                outcome,
                json.dumps(safe_metadata),
                datetime.now(UTC),
            ),
        )
