"""提示词测试 Worker 的 PostgreSQL 权威状态适配器。"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Any, cast
from uuid import UUID

import psycopg

from packages.backend.integrations.crypto.ai_keys import AiKeyEnvelope
from packages.backend.jobs.repository import JobRepository
from packages.backend.jobs.service import (
    CurrentModelCallProfile,
    PromptTestExecutionContext,
)

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
                """SELECT p.api_base_url,p.model_name,p.call_config_revision,p.is_active,
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
                ciphertext=bytes(cast(Any, row[4])),
                nonce=bytes(cast(Any, row[5])),
                key_id=str(row[6]),
                envelope_version=int(cast(Any, row[7])),
                last_four=str(row[8] or ""),
            )
            if all(row[index] is not None for index in (4, 5, 6, 7))
            else None
        )
        return CurrentModelCallProfile(
            kindergarten_id=kindergarten_id,
            profile_id=profile_id,
            api_base_url=str(row[0]),
            model_name=str(row[1]),
            capability_codes=frozenset(str(value) for value in cast(list[object], row[9])),
            call_config_revision=int(cast(Any, row[2])),
            is_active=bool(row[3]),
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
        code: str,
        summary: str,
    ) -> None:
        with self._connect() as connection, connection.transaction():
            self._finish_failure(connection, kindergarten_id, job_id, code=code, summary=summary)

    @staticmethod
    def _finish_failure(
        connection: Any,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        code: str,
        summary: str,
    ) -> None:
        connection.execute(
            """UPDATE background_jobs SET execution_status='failed',finished_at=now(),
            error_code=%s,error_summary=%s,lease_owner=NULL,lease_expires_at=NULL,
            last_heartbeat_at=NULL,updated_at=now()
            WHERE kindergarten_id=%s AND id=%s AND job_type='prompt.test'
              AND execution_status NOT IN ('succeeded','failed')""",
            (code, summary, kindergarten_id, job_id),
        )
        connection.execute(
            """UPDATE prompt_test_runs SET status='failed',error_code=%s,error_summary=%s,
            updated_at=now() WHERE kindergarten_id=%s AND job_id=%s AND status='pending'""",
            (code, summary, kindergarten_id, job_id),
        )

    def finish_prompt_test_success(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        output: dict[str, object],
        elapsed_ms: int,
    ) -> None:
        with self._connect() as connection, connection.transaction():
            updated = connection.execute(
                """UPDATE background_jobs SET execution_status='succeeded',finished_at=now(),
                error_code=NULL,error_summary=NULL,lease_owner=NULL,lease_expires_at=NULL,
                last_heartbeat_at=NULL,updated_at=now()
                WHERE kindergarten_id=%s AND id=%s AND job_type='prompt.test'
                  AND execution_status='running'""",
                (kindergarten_id, job_id),
            )
            if not getattr(updated, "rowcount", 0):
                return
            connection.execute(
                """UPDATE prompt_test_runs SET status='succeeded',output_content=%s::jsonb,
                elapsed_ms=%s,error_code=NULL,error_summary=NULL,updated_at=now()
                WHERE kindergarten_id=%s AND job_id=%s AND status='pending'""",
                (
                    json.dumps(output, ensure_ascii=False),
                    elapsed_ms,
                    kindergarten_id,
                    job_id,
                ),
            )

    def handle_prompt_test_error(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        code: str,
        summary: str,
        retryable: bool,
    ) -> bool:
        with self._connect() as connection, connection.transaction():
            row: Any = connection.execute(
                """SELECT attempt_count,max_attempts FROM background_jobs
                WHERE kindergarten_id=%s AND id=%s AND job_type='prompt.test'
                FOR UPDATE""",
                (kindergarten_id, job_id),
            ).fetchone()
            if row is None:
                return False
            if retryable and int(cast(Any, row[0])) < int(cast(Any, row[1])):
                connection.execute(
                    """UPDATE background_jobs SET execution_status='retrying',
                    lease_owner=NULL,lease_expires_at=NULL,last_heartbeat_at=NULL,
                    error_code=NULL,error_summary=NULL,updated_at=now()
                    WHERE kindergarten_id=%s AND id=%s AND execution_status='running'""",
                    (kindergarten_id, job_id),
                )
                return True
            self._finish_failure(
                connection,
                kindergarten_id,
                job_id,
                code=code,
                summary=summary,
            )
            return False

    def recoverable_job_ids(
        self,
        *,
        now: datetime,
        limit: int,
    ) -> list[UUID]:
        with self._connect() as connection, connection.transaction():
            connection.execute(
                """UPDATE background_jobs j SET execution_status='failed',finished_at=now(),
                error_code='job.attempts_exhausted',
                error_summary='提示词测试已达到最大尝试次数。',
                lease_owner=NULL,lease_expires_at=NULL,last_heartbeat_at=NULL,updated_at=now()
                WHERE j.job_type='prompt.test' AND j.execution_status='running'
                  AND j.lease_expires_at<%s AND j.attempt_count>=j.max_attempts""",
                (now,),
            )
            connection.execute(
                """UPDATE prompt_test_runs r SET status='failed',
                error_code='job.attempts_exhausted',
                error_summary='提示词测试已达到最大尝试次数。',updated_at=now()
                FROM background_jobs j
                WHERE j.kindergarten_id=r.kindergarten_id AND j.id=r.job_id
                  AND j.job_type='prompt.test' AND j.execution_status='failed'
                  AND j.error_code='job.attempts_exhausted' AND r.status='pending'"""
            )
            rows = connection.execute(
                """SELECT id FROM background_jobs
                WHERE job_type='prompt.test' AND attempt_count<max_attempts
                  AND (
                    execution_status IN ('pending_dispatch','retrying')
                    OR (execution_status='running' AND lease_expires_at<%s)
                  )
                ORDER BY created_at,id LIMIT %s""",
                (now, limit),
            ).fetchall()
        return [UUID(str(row[0])) for row in rows]
