"""审计 Service。"""

from typing import Any

from packages.backend.audit.repository import AuditRepository
from packages.contracts import audit as audit_constants


class AuditService:
    """业务审计门面，隐藏 Repository 细节并约束身份审计字段。"""

    def __init__(self, session: Any) -> None:
        self._repo = AuditRepository(session)

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
    ) -> None:
        """记录一条审计事件。"""
        self._repo.record(
            kindergarten_id=kindergarten_id,
            event_type=event_type,
            actor_user_id=actor_user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            result=result,
            metadata=metadata,
        )

    def record_identity(
        self,
        *,
        kindergarten_id: str,
        event_type: str,
        actor_user_id: str | None,
        resource_id: str,
        action: str,
        result: str,
        source_ip: str | None = None,
    ) -> None:
        """记录身份审计事件，元数据仅保留来源 IP。"""
        metadata: dict[str, Any] = {}
        if source_ip:
            metadata["source_ip"] = source_ip
        self.record(
            kindergarten_id=kindergarten_id,
            event_type=event_type,
            actor_user_id=actor_user_id,
            resource_type=audit_constants.RESOURCE_TYPE_USER,
            resource_id=resource_id,
            action=action,
            result=result,
            metadata=metadata,
        )
