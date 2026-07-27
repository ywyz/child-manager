"""提示词测试 Worker 的 PostgreSQL 权威状态适配器。"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Any, cast
from uuid import UUID

import psycopg

from packages.backend.audit.repository import AuditRepository
from packages.backend.integrations.crypto.ai_keys import AiKeyEnvelope
from packages.backend.jobs.repository import JobRepository
from packages.backend.jobs.retry_policy import MAX_RETRY_AFTER_SECONDS, retry_delay_seconds
from packages.backend.jobs.service import (
    CurrentModelCallProfile,
    PromptTestExecutionContext,
)
from packages.contracts.audit import IdentityAuditEventCode

LEASE_SECONDS = 120


def _native_url(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


class PostgresPromptTestStore:
    def __init__(self, database_url: str) -> None:
        self.database_url = database_url

    def _connect(self) -> psycopg.Connection[tuple[object, ...]]:
        return psycopg.connect(_native_url(self.database_url))

    def kindergarten_id_for_job(self, job_id: UUID) -> UUID | None:
        with self._connect() as connection:
            row: Any = connection.execute(
                """SELECT kindergarten_id FROM background_jobs
                WHERE id=%s AND job_type='prompt.test'""",
                (job_id,),
            ).fetchone()
        return UUID(str(row[0])) if row is not None else None

    def claim_prompt_test(self, kindergarten_id: UUID, job_id: UUID, worker_id: str) -> bool:
        with self._connect() as connection, connection.transaction():
            limits: Any = connection.execute(
                """SELECT p.id,p.max_concurrency,p.rate_limit_per_minute
                FROM background_jobs j
                JOIN prompt_test_runs r
                  ON r.kindergarten_id=j.kindergarten_id AND r.job_id=j.id
                JOIN ai_model_profiles p
                  ON p.kindergarten_id=r.kindergarten_id AND p.id=r.model_profile_id
                WHERE j.kindergarten_id=%s AND j.id=%s AND j.job_type='prompt.test'
                FOR UPDATE OF p""",
                (kindergarten_id, job_id),
            ).fetchone()
            if limits is None:
                return False
            running: Any = connection.execute(
                """SELECT count(*) FROM background_jobs j
                JOIN prompt_test_runs r
                  ON r.kindergarten_id=j.kindergarten_id AND r.job_id=j.id
                WHERE r.kindergarten_id=%s AND r.model_profile_id=%s
                  AND j.execution_status='running' AND j.id<>%s""",
                (kindergarten_id, limits[0], job_id),
            ).fetchone()
            if running is not None and int(cast(Any, running[0])) >= int(cast(Any, limits[1])):
                return False
            if limits[2] is not None:
                recent_attempts: Any = connection.execute(
                    """SELECT COALESCE(sum(j.attempt_count),0)
                    FROM background_jobs j
                    JOIN prompt_test_runs r
                      ON r.kindergarten_id=j.kindergarten_id AND r.job_id=j.id
                    WHERE r.kindergarten_id=%s AND r.model_profile_id=%s
                      AND j.updated_at>=now()-interval '1 minute'""",
                    (kindergarten_id, limits[0]),
                ).fetchone()
                if recent_attempts is not None and int(cast(Any, recent_attempts[0])) >= int(
                    cast(Any, limits[2])
                ):
                    return False
            return JobRepository(connection).claim(
                kindergarten_id,
                job_id,
                worker_id=worker_id,
                lease_expires_at=datetime.now(UTC) + timedelta(seconds=LEASE_SECONDS),
            )

    def load_prompt_test_context(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
    ) -> PromptTestExecutionContext:
        with self._connect() as connection:
            row: Any = connection.execute(
                """SELECT r.id,j.requested_by,r.model_profile_id,r.input_context,
                r.prompt_content,r.result_schema_code,r.result_schema_version,
                r.model_call_snapshot
                FROM prompt_test_runs r JOIN background_jobs j
                  ON j.kindergarten_id=r.kindergarten_id AND j.id=r.job_id
                WHERE r.kindergarten_id=%s AND r.job_id=%s""",
                (kindergarten_id, job_id),
            ).fetchone()
        if row is None:
            raise LookupError("提示词测试上下文不存在")
        return PromptTestExecutionContext(
            kindergarten_id=kindergarten_id,
            job_id=job_id,
            run_id=UUID(str(row[0])),
            requested_by=UUID(str(row[1])),
            model_profile_id=UUID(str(row[2])),
            input_context=cast(dict[str, object], row[3]),
            prompt_content=str(row[4]),
            result_schema_code=str(row[5]),
            result_schema_version=int(cast(Any, row[6])),
            model_call_snapshot=cast(dict[str, object], row[7]),
        )

    def get_current_profile(
        self,
        kindergarten_id: UUID,
        profile_id: UUID,
    ) -> CurrentModelCallProfile:
        with self._connect() as connection:
            row: Any = connection.execute(
                """SELECT p.api_base_url,p.model_name,p.call_config_revision,
                p.max_concurrency,p.rate_limit_per_minute,p.is_active,
                p.api_key_ciphertext,p.api_key_nonce,p.api_key_key_id,
                p.api_key_encryption_version,p.api_key_last_four,
                COALESCE(array_agg(c.capability_code ORDER BY c.capability_code)
                  FILTER (WHERE c.capability_code IS NOT NULL),ARRAY[]::varchar[])
                FROM ai_model_profiles p LEFT JOIN ai_model_profile_capabilities c
                  ON c.kindergarten_id=p.kindergarten_id AND c.model_profile_id=p.id
                WHERE p.kindergarten_id=%s AND p.id=%s GROUP BY p.id""",
                (kindergarten_id, profile_id),
            ).fetchone()
        if row is None:
            raise LookupError("模型档案不存在")
        envelope = (
            AiKeyEnvelope(
                ciphertext=bytes(cast(Any, row[6])),
                nonce=bytes(cast(Any, row[7])),
                key_id=str(row[8]),
                envelope_version=int(cast(Any, row[9])),
                last_four=str(row[10] or ""),
            )
            if all(row[index] is not None for index in (6, 7, 8, 9))
            else None
        )
        return CurrentModelCallProfile(
            kindergarten_id=kindergarten_id,
            profile_id=profile_id,
            api_base_url=str(row[0]),
            model_name=str(row[1]),
            capability_codes=frozenset(str(value) for value in cast(list[object], row[11])),
            call_config_revision=int(cast(Any, row[2])),
            max_concurrency=int(cast(Any, row[3])),
            rate_limit_per_minute=(int(cast(Any, row[4])) if row[4] is not None else None),
            is_active=bool(row[5]),
            key_envelope=envelope,
        )

    def can_run_prompt_test(self, kindergarten_id: UUID, requested_by: UUID) -> bool:
        with self._connect() as connection:
            row: Any = connection.execute(
                """SELECT EXISTS(
                    SELECT 1 FROM users u
                    JOIN user_roles ur
                      ON ur.kindergarten_id=u.kindergarten_id AND ur.user_id=u.id
                    JOIN roles r ON r.id=ur.role_id
                    WHERE u.kindergarten_id=%s AND u.id=%s
                      AND u.status='active' AND r.code='admin'
                )""",
                (kindergarten_id, requested_by),
            ).fetchone()
        return bool(row and row[0])

    def finish_prompt_test_failure(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
        code: str,
        summary: str,
        elapsed_ms: int,
    ) -> None:
        with self._connect() as connection, connection.transaction():
            row: Any = connection.execute(
                """SELECT j.requested_by,j.request_id,r.id
                FROM background_jobs j JOIN prompt_test_runs r
                  ON r.kindergarten_id=j.kindergarten_id AND r.job_id=j.id
                WHERE j.kindergarten_id=%s AND j.id=%s AND j.job_type='prompt.test'
                  AND j.execution_status='running' AND j.lease_owner=%s
                FOR UPDATE OF j""",
                (kindergarten_id, job_id, worker_id),
            ).fetchone()
            if row is None:
                return
            finished = self._finish_failure(
                connection,
                kindergarten_id,
                job_id,
                worker_id=worker_id,
                code=code,
                summary=summary,
            )
            if finished:
                self._append_attempt_audit(
                    connection,
                    kindergarten_id,
                    requested_by=UUID(str(row[0])),
                    request_id=UUID(str(row[1])) if row[1] is not None else None,
                    run_id=UUID(str(row[2])),
                    outcome="failure",
                    reason=code,
                    source="final",
                    elapsed_ms=elapsed_ms,
                    error_summary=summary,
                )

    @staticmethod
    def _finish_failure(
        connection: Any,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
        code: str,
        summary: str,
    ) -> bool:
        updated = connection.execute(
            """UPDATE background_jobs SET execution_status='failed',finished_at=now(),
            error_code=%s,error_summary=%s,lease_owner=NULL,lease_expires_at=NULL,
            last_heartbeat_at=NULL,updated_at=now()
            WHERE kindergarten_id=%s AND id=%s AND job_type='prompt.test'
              AND execution_status='running' AND lease_owner=%s""",
            (code, summary, kindergarten_id, job_id, worker_id),
        )
        if not getattr(updated, "rowcount", 0):
            return False
        connection.execute(
            """UPDATE prompt_test_runs SET status='failed',error_code=%s,error_summary=%s,
            updated_at=now() WHERE kindergarten_id=%s AND job_id=%s AND status='pending'""",
            (code, summary, kindergarten_id, job_id),
        )
        return True

    @staticmethod
    def _append_attempt_audit(
        connection: psycopg.Connection[tuple[object, ...]],
        kindergarten_id: UUID,
        *,
        requested_by: UUID,
        request_id: UUID | None,
        run_id: UUID,
        outcome: str,
        reason: str | None = None,
        source: str | None = None,
        elapsed_ms: int | None = None,
        error_summary: str | None = None,
    ) -> None:
        AuditRepository(connection, kindergarten_id).append(
            event_code=IdentityAuditEventCode.PROMPT_TEST_ATTEMPTED,
            actor_user_id=requested_by,
            actor_role_codes=["admin"],
            resource_type="prompt_test_run",
            resource_id=run_id,
            outcome=outcome,
            request_id=request_id,
            metadata={
                key: value
                for key, value in {
                    "reason": reason,
                    "source": source,
                    "elapsed_ms": elapsed_ms,
                    "error_summary": error_summary,
                }.items()
                if value is not None
            },
        )

    def finish_prompt_test_success(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
        output: dict[str, object],
        elapsed_ms: int,
    ) -> None:
        with self._connect() as connection, connection.transaction():
            job_row: Any = connection.execute(
                """UPDATE background_jobs SET execution_status='succeeded',finished_at=now(),
                error_code=NULL,error_summary=NULL,lease_owner=NULL,lease_expires_at=NULL,
                last_heartbeat_at=NULL,updated_at=now()
                WHERE kindergarten_id=%s AND id=%s AND job_type='prompt.test'
                  AND execution_status='running' AND lease_owner=%s
                RETURNING requested_by,request_id""",
                (kindergarten_id, job_id, worker_id),
            ).fetchone()
            if job_row is None:
                return
            run_row: Any = connection.execute(
                """UPDATE prompt_test_runs SET status='succeeded',output_content=%s::jsonb,
                elapsed_ms=%s,error_code=NULL,error_summary=NULL,updated_at=now()
                WHERE kindergarten_id=%s AND job_id=%s AND status='pending'
                RETURNING id""",
                (
                    json.dumps(output, ensure_ascii=False),
                    elapsed_ms,
                    kindergarten_id,
                    job_id,
                ),
            ).fetchone()
            if run_row is not None:
                self._append_attempt_audit(
                    connection,
                    kindergarten_id,
                    requested_by=UUID(str(job_row[0])),
                    request_id=UUID(str(job_row[1])) if job_row[1] is not None else None,
                    run_id=UUID(str(run_row[0])),
                    outcome="success",
                    source="completed",
                    elapsed_ms=elapsed_ms,
                )

    def handle_prompt_test_error(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
        code: str,
        summary: str,
        retryable: bool,
        retry_after_seconds: int | None,
        elapsed_ms: int | None,
    ) -> int | None:
        with self._connect() as connection, connection.transaction():
            row: Any = connection.execute(
                """SELECT j.attempt_count,j.max_attempts,j.requested_by,j.request_id,r.id
                FROM background_jobs j JOIN prompt_test_runs r
                  ON r.kindergarten_id=j.kindergarten_id AND r.job_id=j.id
                WHERE j.kindergarten_id=%s AND j.id=%s AND j.job_type='prompt.test'
                  AND j.execution_status='running' AND j.lease_owner=%s
                FOR UPDATE OF j""",
                (kindergarten_id, job_id, worker_id),
            ).fetchone()
            if row is None:
                return None
            if retryable and int(cast(Any, row[0])) < int(cast(Any, row[1])):
                policy_delay = retry_delay_seconds(
                    job_id,
                    attempt_count=int(cast(Any, row[0])),
                )
                if retry_after_seconds is not None:
                    policy_delay = max(
                        policy_delay,
                        min(MAX_RETRY_AFTER_SECONDS, retry_after_seconds),
                    )
                updated = connection.execute(
                    """UPDATE background_jobs SET execution_status='retrying',
                    lease_owner=NULL,lease_expires_at=NULL,last_heartbeat_at=NULL,
                    error_code=NULL,error_summary=NULL,
                    queued_at=now()+(%s * interval '1 second'),updated_at=now()
                    WHERE kindergarten_id=%s AND id=%s
                      AND execution_status='running' AND lease_owner=%s""",
                    (policy_delay, kindergarten_id, job_id, worker_id),
                )
                if not getattr(updated, "rowcount", 0):
                    return None
                self._append_attempt_audit(
                    connection,
                    kindergarten_id,
                    requested_by=UUID(str(row[2])),
                    request_id=UUID(str(row[3])) if row[3] is not None else None,
                    run_id=UUID(str(row[4])),
                    outcome="failure",
                    reason=code,
                    source="retrying",
                    elapsed_ms=elapsed_ms,
                    error_summary=summary,
                )
                return policy_delay
            finished = self._finish_failure(
                connection,
                kindergarten_id,
                job_id,
                worker_id=worker_id,
                code=code,
                summary=summary,
            )
            if finished:
                self._append_attempt_audit(
                    connection,
                    kindergarten_id,
                    requested_by=UUID(str(row[2])),
                    request_id=UUID(str(row[3])) if row[3] is not None else None,
                    run_id=UUID(str(row[4])),
                    outcome="failure",
                    reason=code,
                    source="final",
                    elapsed_ms=elapsed_ms,
                    error_summary=summary,
                )
            return None

    def heartbeat_prompt_test(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
    ) -> bool:
        with self._connect() as connection, connection.transaction():
            result = connection.execute(
                """UPDATE background_jobs SET last_heartbeat_at=now(),
                lease_expires_at=now()+(%s * interval '1 second'),updated_at=now()
                WHERE kindergarten_id=%s AND id=%s AND job_type='prompt.test'
                  AND execution_status='running' AND lease_owner=%s""",
                (LEASE_SECONDS, kindergarten_id, job_id, worker_id),
            )
            return bool(getattr(result, "rowcount", 0))

    def mark_prompt_test_dispatched(self, kindergarten_id: UUID, job_id: UUID) -> None:
        with self._connect() as connection, connection.transaction():
            connection.execute(
                """UPDATE background_jobs SET execution_status='queued',
                queued_at=now(),updated_at=now()
                WHERE kindergarten_id=%s AND id=%s AND job_type='prompt.test'
                  AND execution_status='pending_dispatch'""",
                (kindergarten_id, job_id),
            )

    def recoverable_job_ids(
        self,
        *,
        now: datetime,
        limit: int,
        include_expired: bool,
    ) -> list[UUID]:
        with self._connect() as connection, connection.transaction():
            lock: Any = connection.execute(
                "SELECT pg_try_advisory_xact_lock(hashtextextended(%s,0))",
                ("prompt-test-recovery",),
            ).fetchone()
            if lock is None or not bool(lock[0]):
                return []
            if include_expired:
                exhausted = connection.execute(
                    """SELECT j.kindergarten_id,j.id,j.requested_by,j.request_id,
                    j.last_heartbeat_at,r.id
                    FROM background_jobs j JOIN prompt_test_runs r
                      ON r.kindergarten_id=j.kindergarten_id AND r.job_id=j.id
                    WHERE j.job_type='prompt.test' AND j.execution_status='running'
                      AND j.lease_expires_at<%s AND j.attempt_count>=j.max_attempts
                    ORDER BY j.created_at,j.id LIMIT %s FOR UPDATE OF j SKIP LOCKED""",
                    (now, limit),
                ).fetchall()
                for row in exhausted:
                    kindergarten_id = UUID(str(row[0]))
                    job_id = UUID(str(row[1]))
                    summary = "提示词测试已达到最大尝试次数。"
                    connection.execute(
                        """UPDATE background_jobs SET execution_status='failed',
                        finished_at=%s,error_code='job.attempts_exhausted',
                        error_summary=%s,lease_owner=NULL,lease_expires_at=NULL,
                        last_heartbeat_at=NULL,updated_at=now()
                        WHERE kindergarten_id=%s AND id=%s
                          AND execution_status='running'""",
                        (now, summary, kindergarten_id, job_id),
                    )
                    connection.execute(
                        """UPDATE prompt_test_runs SET status='failed',
                        error_code='job.attempts_exhausted',error_summary=%s,updated_at=now()
                        WHERE kindergarten_id=%s AND job_id=%s AND status='pending'""",
                        (summary, kindergarten_id, job_id),
                    )
                    heartbeat_at = row[4] if isinstance(row[4], datetime) else now
                    elapsed_ms = max(
                        0,
                        int((now - heartbeat_at).total_seconds() * 1000),
                    )
                    self._append_attempt_audit(
                        connection,
                        kindergarten_id,
                        requested_by=UUID(str(row[2])),
                        request_id=UUID(str(row[3])) if row[3] is not None else None,
                        run_id=UUID(str(row[5])),
                        outcome="failure",
                        reason="job.attempts_exhausted",
                        source="lease_expired",
                        elapsed_ms=elapsed_ms,
                        error_summary=summary,
                    )
            rows = connection.execute(
                """SELECT kindergarten_id,id FROM background_jobs
                WHERE job_type='prompt.test' AND attempt_count<max_attempts
                  AND (
                    (
                        execution_status='pending_dispatch'
                        AND updated_at < %s - interval '15 seconds'
                    )
                    OR (execution_status='retrying' AND queued_at<=%s)
                    OR (
                        %s
                        AND execution_status='running'
                        AND lease_expires_at<%s
                    )
                    OR (
                        execution_status='queued'
                        AND queued_at < %s - interval '15 seconds'
                    )
                  )
                ORDER BY created_at,id LIMIT %s FOR UPDATE SKIP LOCKED""",
                (now, now, include_expired, now, now, limit),
            ).fetchall()
            reservations = [(UUID(str(row[0])), UUID(str(row[1]))) for row in rows]
            if reservations:
                with connection.cursor() as cursor:
                    cursor.executemany(
                        """UPDATE background_jobs SET execution_status='pending_dispatch',
                        lease_owner=NULL,lease_expires_at=NULL,
                        last_heartbeat_at=NULL,updated_at=now()
                        WHERE kindergarten_id=%s AND id=%s""",
                        reservations,
                    )
        return [job_id for _kindergarten_id, job_id in reservations]
