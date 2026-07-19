"""审计 Repository。"""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid7

from packages.backend.audit.models import AuditEvent

# 冻结 Schema §6.2 要求 metadata 只允许事件专用白名单字段。
# 当前身份审计只记录来源 IP；未来新事件需要新增字段时必须在此扩展并补回归测试。
_ALLOWED_METADATA_KEYS = frozenset({"source_ip"})


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
        normalized_metadata = metadata or {}
        unexpected = set(normalized_metadata) - _ALLOWED_METADATA_KEYS
        if unexpected:
            # 拒绝密钥、令牌、完整教案或 AI 正文等非白名单字段进入审计记录。
            msg = f"审计 metadata 含未授权字段: {sorted(unexpected)}"
            raise ValueError(msg)
        now = datetime.now(UTC)
        event = AuditEvent(
            # 冻结 Schema §3.2 要求主键使用 UUIDv7。
            id=str(uuid7()),
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
