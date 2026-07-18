"""审计 Repository。"""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from packages.backend.audit.models import AuditEvent


class AuditRepository:
    def __init__(self, session: Any) -> None:
        self._session = session

    def record(
        self,
        *,
        kindergarten_id: str,
        event_code: str,
        actor_user_id: str | None,
        actor_role_codes: list[str] | None = None,
        resource_type: str,
        resource_id: str | None,
        outcome: str,
        metadata: dict[str, Any] | None = None,
        request_id: str | None = None,
        trace_id: str | None = None,
        job_id: str | None = None,
    ) -> AuditEvent:
        now = datetime.now(UTC)
        event = AuditEvent(
            id=str(uuid4()),
            kindergarten_id=kindergarten_id,
            event_code=event_code,
            actor_user_id=actor_user_id,
            actor_role_codes=actor_role_codes or [],
            resource_type=resource_type,
            resource_id=resource_id,
            outcome=outcome,
            event_metadata=metadata or {},
            request_id=request_id,
            trace_id=trace_id,
            job_id=job_id,
            occurred_at=now,
            created_at=now,
            updated_at=now,
        )
        self._session.add(event)
        self._session.flush()
        return event
