"""审计 Repository。"""

from typing import Any

from packages.backend.audit.models import AuditEvent


class AuditRepository:
    def __init__(self, session: Any) -> None:
        self._session = session

    def record(
        self,
        *,
        kindergarten_id: str,
        event_type: str,
        actor_user_id: str | None,
        resource_type: str,
        resource_id: str,
        action: str,
        result: str,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEvent:
        event = AuditEvent(
            kindergarten_id=kindergarten_id,
            event_type=event_type,
            actor_user_id=actor_user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            result=result,
            event_metadata=metadata or {},
        )
        self._session.add(event)
        self._session.flush()
        return event
