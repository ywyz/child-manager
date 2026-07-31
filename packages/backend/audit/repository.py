"""只接受身份白名单字段的审计写入。"""

import json
from datetime import UTC, datetime
from uuid import UUID, uuid7

import psycopg
from pydantic import ValidationError

from packages.contracts.audit import (
    AiGenerationAuditMetadata,
    IdentityAuditEventCode,
    IdentityAuditMetadata,
)


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
        trace_id: UUID | None = None,
        job_id: UUID | None = None,
        metadata: dict[str, object] | None = None,
    ) -> None:
        try:
            metadata_model = (
                AiGenerationAuditMetadata
                if event_code.value.startswith("ai.")
                else IdentityAuditMetadata
            )
            safe_metadata = metadata_model.model_validate(metadata or {}).model_dump(
                mode="json",
                exclude_none=True,
            )
        except ValidationError as exc:
            raise ValueError("审计 metadata 包含非白名单字段或值") from exc
        self.connection.execute(
            """INSERT INTO audit_events
            (id, kindergarten_id, event_code, actor_user_id, actor_role_codes, resource_type,
             resource_id, request_id, trace_id, job_id, outcome, metadata, occurred_at)
            VALUES (%s,%s,%s,%s,%s::jsonb,%s,%s,%s,%s,%s,%s,%s::jsonb,%s)""",
            (
                uuid7(),
                self.kindergarten_id,
                event_code.value,
                actor_user_id,
                json.dumps(actor_role_codes),
                resource_type,
                resource_id,
                request_id,
                trace_id,
                job_id,
                outcome,
                json.dumps(safe_metadata),
                datetime.now(UTC),
            ),
        )
