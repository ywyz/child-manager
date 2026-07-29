"""PostgreSQL 权威后台任务 Repository。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from typing import Any
from uuid import UUID


@dataclass(frozen=True, slots=True)
class JobRecord:
    id: UUID
    job_type: str
    status: str
    requested_by: UUID
    request_fingerprint_sha256: str | None
    attempt_count: int
    max_attempts: int
    trace_id: UUID
    created_at: datetime
    queued_at: datetime | None
    started_at: datetime | None
    finished_at: datetime | None
    error_code: str | None
    error_summary: str | None


@dataclass(frozen=True, slots=True)
class AiJobRecord:
    id: UUID
    parent_job_id: UUID | None
    retry_of_job_id: UUID | None
    job_type: str
    status: str | None
    plan_id: UUID
    target_section: str | None
    requested_resource_version: int
    idempotency_scope: str | None
    idempotency_key: str | None
    request_fingerprint_sha256: str | None
    attempt_count: int | None
    max_attempts: int | None
    requested_by: UUID
    request_id: UUID | None
    trace_id: UUID
    created_at: datetime
    queued_at: datetime | None
    started_at: datetime | None
    finished_at: datetime | None
    error_code: str | None
    error_summary: str | None


def _row(result: Any) -> tuple[Any, ...] | None:
    return result.fetchone() if result is not None else None


def _job(row: tuple[Any, ...] | None) -> JobRecord | None:
    if row is None:
        return None
    return JobRecord(
        id=UUID(str(row[0])),
        job_type=str(row[1]),
        status=str(row[2]),
        requested_by=UUID(str(row[3])),
        request_fingerprint_sha256=str(row[4]) if row[4] is not None else None,
        attempt_count=int(row[5] or 0),
        max_attempts=int(row[6] or 0),
        trace_id=UUID(str(row[7])),
        created_at=row[8],  # type: ignore[arg-type]
        queued_at=row[9] if isinstance(row[9], datetime) else None,
        started_at=row[10] if isinstance(row[10], datetime) else None,
        finished_at=row[11] if isinstance(row[11], datetime) else None,
        error_code=str(row[12]) if row[12] is not None else None,
        error_summary=str(row[13]) if row[13] is not None else None,
    )


def _uuid(value: object | None) -> UUID | None:
    return UUID(str(value)) if value is not None else None


def _ai_job(row: tuple[Any, ...] | None) -> AiJobRecord | None:
    if row is None:
        return None
    plan_id = _uuid(row[5])
    requested_resource_version = row[7]
    assert plan_id is not None
    assert requested_resource_version is not None
    return AiJobRecord(
        id=UUID(str(row[0])),
        parent_job_id=_uuid(row[1]),
        retry_of_job_id=_uuid(row[2]),
        job_type=str(row[3]),
        status=str(row[4]) if row[4] is not None else None,
        plan_id=plan_id,
        target_section=str(row[6]) if row[6] is not None else None,
        requested_resource_version=int(requested_resource_version),
        idempotency_scope=str(row[8]) if row[8] is not None else None,
        idempotency_key=str(row[9]) if row[9] is not None else None,
        request_fingerprint_sha256=str(row[10]) if row[10] is not None else None,
        attempt_count=int(row[11]) if row[11] is not None else None,
        max_attempts=int(row[12]) if row[12] is not None else None,
        requested_by=UUID(str(row[13])),
        request_id=_uuid(row[14]),
        trace_id=UUID(str(row[15])),
        created_at=row[16],  # type: ignore[arg-type]
        queued_at=row[17] if isinstance(row[17], datetime) else None,
        started_at=row[18] if isinstance(row[18], datetime) else None,
        finished_at=row[19] if isinstance(row[19], datetime) else None,
        error_code=str(row[20]) if row[20] is not None else None,
        error_summary=str(row[21]) if row[21] is not None else None,
    )


_SELECT = """SELECT id,job_type,execution_status,requested_by,request_fingerprint_sha256,
attempt_count,max_attempts,trace_id,created_at,queued_at,started_at,finished_at,
error_code,error_summary FROM background_jobs"""

_AI_SELECT = """SELECT id,parent_job_id,retry_of_job_id,job_type,execution_status,
plan_id,target_section,requested_resource_version,idempotency_scope,idempotency_key,
request_fingerprint_sha256,attempt_count,max_attempts,requested_by,request_id,trace_id,
created_at,queued_at,started_at,finished_at,error_code,error_summary FROM background_jobs"""


class JobRepository:
    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def get(self, kindergarten_id: UUID, job_id: UUID) -> JobRecord | None:
        return _job(
            _row(
                self.connection.execute(
                    _SELECT + " WHERE kindergarten_id=%s AND id=%s",
                    (kindergarten_id, job_id),
                )
            )
        )

    def find_idempotent(
        self,
        kindergarten_id: UUID,
        *,
        requested_by: UUID,
        scope: str,
        key: str,
    ) -> JobRecord | None:
        return _job(
            _row(
                self.connection.execute(
                    _SELECT
                    + """ WHERE kindergarten_id=%s AND requested_by=%s
                    AND idempotency_scope=%s AND idempotency_key=%s""",
                    (kindergarten_id, requested_by, scope, key),
                )
            )
        )

    def get_ai(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        for_update: bool = False,
    ) -> AiJobRecord | None:
        suffix = " FOR UPDATE" if for_update else ""
        return _ai_job(
            _row(
                self.connection.execute(
                    _AI_SELECT
                    + """ WHERE kindergarten_id=%s AND id=%s
                    AND job_type LIKE 'ai.%%'"""
                    + suffix,
                    (kindergarten_id, job_id),
                )
            )
        )

    def find_idempotent_ai(
        self,
        kindergarten_id: UUID,
        *,
        requested_by: UUID,
        scope: str,
        key: str,
    ) -> AiJobRecord | None:
        return _ai_job(
            _row(
                self.connection.execute(
                    _AI_SELECT
                    + """ WHERE kindergarten_id=%s AND requested_by=%s
                    AND idempotency_scope=%s AND idempotency_key=%s
                    AND job_type LIKE 'ai.%%'""",
                    (kindergarten_id, requested_by, scope, key),
                )
            )
        )

    def list_ai_children(
        self,
        kindergarten_id: UUID,
        parent_job_id: UUID,
    ) -> list[AiJobRecord]:
        result = self.connection.execute(
            _AI_SELECT
            + """ WHERE kindergarten_id=%s AND parent_job_id=%s
            ORDER BY CASE target_section
                WHEN 'morning_activity' THEN 1
                WHEN 'morning_talk' THEN 2
                WHEN 'indoor_area_game' THEN 3
                WHEN 'afternoon_outdoor_game' THEN 4
                ELSE 5 END,id""",
            (kindergarten_id, parent_job_id),
        )
        return [record for row in result.fetchall() if (record := _ai_job(row)) is not None]

    def lock_idempotency(
        self,
        kindergarten_id: UUID,
        *,
        requested_by: UUID,
        scope: str,
        key: str,
    ) -> None:
        digest = sha256(f"{kindergarten_id}:{requested_by}:{scope}:{key}".encode()).digest()
        lock_id = int.from_bytes(digest[:8], signed=True)
        self.connection.execute("SELECT pg_advisory_xact_lock(%s)", (lock_id,))

    def create_prompt_test(
        self,
        kindergarten_id: UUID,
        *,
        job_id: UUID,
        requested_by: UUID,
        request_id: UUID | None,
        trace_id: UUID,
        scope: str,
        key: str,
        fingerprint: str,
    ) -> JobRecord:
        result = self.connection.execute(
            """INSERT INTO background_jobs
            (id,kindergarten_id,job_type,execution_status,idempotency_scope,idempotency_key,
             request_fingerprint_sha256,attempt_count,max_attempts,requested_by,request_id,trace_id)
            VALUES (%s,%s,'prompt.test','pending_dispatch',%s,%s,%s,0,3,%s,%s,%s)
            RETURNING id,job_type,execution_status,requested_by,request_fingerprint_sha256,
                      attempt_count,max_attempts,trace_id,created_at,queued_at,started_at,
                      finished_at,error_code,error_summary""",
            (
                job_id,
                kindergarten_id,
                scope,
                key,
                fingerprint,
                requested_by,
                request_id,
                trace_id,
            ),
        )
        record = _job(_row(result))
        assert record is not None
        return record

    def create_ai_batch(
        self,
        kindergarten_id: UUID,
        *,
        job_id: UUID,
        plan_id: UUID,
        requested_resource_version: int,
        requested_by: UUID,
        request_id: UUID | None,
        trace_id: UUID,
        scope: str,
        key: str,
        fingerprint: str,
    ) -> AiJobRecord:
        result = self.connection.execute(
            """INSERT INTO background_jobs
            (id,kindergarten_id,job_type,plan_id,requested_resource_version,
             idempotency_scope,idempotency_key,request_fingerprint_sha256,
             requested_by,request_id,trace_id)
            VALUES (%s,%s,'ai.batch',%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id,parent_job_id,retry_of_job_id,job_type,execution_status,
                      plan_id,target_section,requested_resource_version,idempotency_scope,
                      idempotency_key,request_fingerprint_sha256,attempt_count,max_attempts,
                      requested_by,request_id,trace_id,created_at,queued_at,started_at,
                      finished_at,error_code,error_summary""",
            (
                job_id,
                kindergarten_id,
                plan_id,
                requested_resource_version,
                scope,
                key,
                fingerprint,
                requested_by,
                request_id,
                trace_id,
            ),
        )
        record = _ai_job(_row(result))
        assert record is not None
        return record

    def create_ai_executable(
        self,
        kindergarten_id: UUID,
        *,
        job_id: UUID,
        parent_job_id: UUID | None,
        job_type: str,
        plan_id: UUID,
        target_section: str,
        requested_resource_version: int,
        requested_by: UUID,
        request_id: UUID | None,
        trace_id: UUID,
        scope: str | None,
        key: str | None,
        fingerprint: str | None,
        status: str = "pending_dispatch",
        finished_at: datetime | None = None,
        error_code: str | None = None,
        error_summary: str | None = None,
    ) -> AiJobRecord:
        result = self.connection.execute(
            """INSERT INTO background_jobs
            (id,kindergarten_id,parent_job_id,job_type,execution_status,plan_id,
             target_section,requested_resource_version,idempotency_scope,idempotency_key,
             request_fingerprint_sha256,attempt_count,max_attempts,requested_by,request_id,
             trace_id,finished_at,error_code,error_summary)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0,3,%s,%s,%s,%s,%s,%s)
            RETURNING id,parent_job_id,retry_of_job_id,job_type,execution_status,
                      plan_id,target_section,requested_resource_version,idempotency_scope,
                      idempotency_key,request_fingerprint_sha256,attempt_count,max_attempts,
                      requested_by,request_id,trace_id,created_at,queued_at,started_at,
                      finished_at,error_code,error_summary""",
            (
                job_id,
                kindergarten_id,
                parent_job_id,
                job_type,
                status,
                plan_id,
                target_section,
                requested_resource_version,
                scope,
                key,
                fingerprint,
                requested_by,
                request_id,
                trace_id,
                finished_at,
                error_code,
                error_summary,
            ),
        )
        record = _ai_job(_row(result))
        assert record is not None
        return record

    def claim(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
        lease_expires_at: datetime,
    ) -> bool:
        result = self.connection.execute(
            """UPDATE background_jobs SET execution_status='running',attempt_count=attempt_count+1,
            lease_owner=%s,lease_expires_at=%s,last_heartbeat_at=now(),
            started_at=COALESCE(started_at,now()),updated_at=now()
            WHERE kindergarten_id=%s AND id=%s AND job_type='prompt.test'
              AND attempt_count < max_attempts
              AND (execution_status IN ('pending_dispatch','queued')
                   OR (execution_status='retrying' AND queued_at<=now())
                   OR (execution_status='running' AND lease_expires_at<now()))""",
            (worker_id, lease_expires_at, kindergarten_id, job_id),
        )
        return bool(getattr(result, "rowcount", 0))

    def mark_queued(self, kindergarten_id: UUID, job_id: UUID) -> None:
        self.connection.execute(
            """UPDATE background_jobs SET execution_status='queued',
            queued_at=COALESCE(queued_at,now()),updated_at=now()
            WHERE kindergarten_id=%s AND id=%s AND execution_status='pending_dispatch'""",
            (kindergarten_id, job_id),
        )

    def mark_ai_preview_decided(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        status: str,
        decided_at: datetime,
    ) -> bool:
        if status not in {"adopted", "rejected"}:
            raise ValueError("AI 预览决策状态无效")
        result = self.connection.execute(
            """UPDATE background_jobs
            SET execution_status=%s,finished_at=%s,updated_at=now()
            WHERE kindergarten_id=%s AND id=%s
              AND job_type LIKE 'ai.%%' AND job_type<>'ai.batch'
              AND execution_status='awaiting_confirmation'""",
            (status, decided_at, kindergarten_id, job_id),
        )
        return bool(getattr(result, "rowcount", 0))

    def recoverable_job_ids(
        self,
        kindergarten_id: UUID,
        *,
        now: datetime,
        limit: int,
    ) -> list[UUID]:
        result = self.connection.execute(
            """SELECT id FROM background_jobs
            WHERE kindergarten_id=%s AND job_type='prompt.test'
              AND attempt_count < max_attempts
              AND (execution_status='pending_dispatch'
                   OR (execution_status='running' AND lease_expires_at<%s))
            ORDER BY created_at,id LIMIT %s""",
            (kindergarten_id, now, limit),
        )
        return [UUID(str(row[0])) for row in result.fetchall()]
