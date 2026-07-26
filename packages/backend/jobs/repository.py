"""PostgreSQL 权威后台任务 Repository。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
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


_SELECT = """SELECT id,job_type,execution_status,requested_by,request_fingerprint_sha256,
attempt_count,max_attempts,trace_id,created_at,queued_at,started_at,finished_at,
error_code,error_summary FROM background_jobs"""


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
              AND (execution_status IN ('pending_dispatch','queued','retrying')
                   OR (execution_status='running' AND lease_expires_at<now()))""",
            (worker_id, lease_expires_at, kindergarten_id, job_id),
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
              AND (execution_status='pending_dispatch'
                   OR (execution_status='running' AND lease_expires_at<%s))
            ORDER BY created_at,id LIMIT %s""",
            (kindergarten_id, now, limit),
        )
        return [UUID(str(row[0])) for row in result.fetchall()]
