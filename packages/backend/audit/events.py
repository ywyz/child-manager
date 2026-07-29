"""AI 任务审计的脱敏写入入口。"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from packages.backend.audit.repository import AuditRepository
from packages.contracts.audit import IdentityAuditEventCode

_AI_EVENTS = {
    IdentityAuditEventCode.AI_GENERATION_CREATED,
    IdentityAuditEventCode.AI_AUTOMATIC_RETRY_SCHEDULED,
    IdentityAuditEventCode.AI_GENERATION_RETRIED,
    IdentityAuditEventCode.AI_GENERATION_SUCCEEDED,
    IdentityAuditEventCode.AI_GENERATION_FAILED,
    IdentityAuditEventCode.AI_PREVIEW_REJECTED,
    IdentityAuditEventCode.AI_PREVIEW_ADOPTED,
}


def append_ai_event(
    connection: Any,
    kindergarten_id: UUID,
    *,
    event_code: IdentityAuditEventCode,
    job_id: UUID,
    actor_user_id: UUID | None,
    actor_role_codes: list[str],
    outcome: str,
    request_id: UUID | None = None,
    trace_id: UUID | None = None,
    retry_of_job_id: UUID | None = None,
    attempt_count: int | None = None,
    error_code: str | None = None,
    target_section: str | None = None,
) -> None:
    if event_code not in _AI_EVENTS:
        raise ValueError("事件代码不属于 AI 审计白名单")
    AuditRepository(connection, kindergarten_id).append(
        event_code=event_code,
        actor_user_id=actor_user_id,
        actor_role_codes=actor_role_codes,
        resource_type="background_job",
        resource_id=job_id,
        request_id=request_id,
        trace_id=trace_id,
        job_id=job_id,
        outcome=outcome,
        metadata={
            "job_id": job_id,
            "retry_of_job_id": retry_of_job_id,
            "attempt_count": attempt_count,
            "error_code": error_code,
            "target_section": target_section,
        },
    )


__all__ = ["append_ai_event"]
