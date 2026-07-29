"""同园隔离的 AI 生成结果 Repository。"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any
from uuid import UUID

from psycopg.types.json import Jsonb


@dataclass(frozen=True, slots=True)
class AiGenerationResultRecord:
    id: UUID
    kindergarten_id: UUID
    job_id: UUID
    plan_id: UUID
    target_section: str
    requested_resource_version: int
    target_section_baseline_sha256: str
    input_context: dict[str, Any] | None
    input_sha256: str
    model_profile_id: UUID
    model_name_snapshot: str
    prompt_definition_id: UUID
    prompt_version_id: UUID
    prompt_content_sha256: str
    result_schema_code: str
    result_schema_version: int
    output_content: dict[str, Any] | None
    output_sha256: str | None
    expires_at: datetime
    adopted_at: datetime | None
    adopted_by: UUID | None
    rejected_at: datetime | None
    rejected_by: UUID | None
    content_cleared_at: datetime | None
    created_at: datetime
    updated_at: datetime


_COLUMNS = """id,kindergarten_id,job_id,plan_id,target_section,
requested_resource_version,target_section_baseline_sha256,input_context,input_sha256,
model_profile_id,model_name_snapshot,prompt_definition_id,prompt_version_id,
prompt_content_sha256,result_schema_code,result_schema_version,output_content,
output_sha256,expires_at,adopted_at,adopted_by,rejected_at,rejected_by,
content_cleared_at,created_at,updated_at"""


def _uuid(value: object) -> UUID:
    return value if isinstance(value, UUID) else UUID(str(value))


def _optional_uuid(value: object | None) -> UUID | None:
    return _uuid(value) if value is not None else None


def _json_object(value: object | None) -> dict[str, Any] | None:
    return dict(value) if isinstance(value, Mapping) else None


def _row(result: Any) -> tuple[Any, ...] | None:
    return result.fetchone() if result is not None else None


def _record(row: tuple[Any, ...] | None) -> AiGenerationResultRecord | None:
    if row is None:
        return None
    return AiGenerationResultRecord(
        id=_uuid(row[0]),
        kindergarten_id=_uuid(row[1]),
        job_id=_uuid(row[2]),
        plan_id=_uuid(row[3]),
        target_section=str(row[4]),
        requested_resource_version=int(row[5]),
        target_section_baseline_sha256=str(row[6]),
        input_context=_json_object(row[7]),
        input_sha256=str(row[8]),
        model_profile_id=_uuid(row[9]),
        model_name_snapshot=str(row[10]),
        prompt_definition_id=_uuid(row[11]),
        prompt_version_id=_uuid(row[12]),
        prompt_content_sha256=str(row[13]),
        result_schema_code=str(row[14]),
        result_schema_version=int(row[15]),
        output_content=_json_object(row[16]),
        output_sha256=str(row[17]) if row[17] is not None else None,
        expires_at=row[18],
        adopted_at=row[19] if isinstance(row[19], datetime) else None,
        adopted_by=_optional_uuid(row[20]),
        rejected_at=row[21] if isinstance(row[21], datetime) else None,
        rejected_by=_optional_uuid(row[22]),
        content_cleared_at=row[23] if isinstance(row[23], datetime) else None,
        created_at=row[24],
        updated_at=row[25],
    )


class AiGenerationResultRepository:
    """执行 SQL 但不拥有调用方事务。"""

    def __init__(self, connection: Any) -> None:
        self.connection = connection

    def create_pending(
        self,
        kindergarten_id: UUID,
        *,
        result_id: UUID,
        job_id: UUID,
        plan_id: UUID,
        target_section: str,
        requested_resource_version: int,
        target_section_baseline_sha256: str,
        input_context: Mapping[str, Any],
        input_sha256: str,
        model_profile_id: UUID,
        model_name_snapshot: str,
        prompt_definition_id: UUID,
        prompt_version_id: UUID,
        prompt_content_sha256: str,
        result_schema_code: str,
        result_schema_version: int,
        expires_at: datetime,
    ) -> AiGenerationResultRecord:
        result = self.connection.execute(
            f"""INSERT INTO ai_generation_results
            (id,kindergarten_id,job_id,plan_id,target_section,requested_resource_version,
             target_section_baseline_sha256,input_context,input_sha256,model_profile_id,
             model_name_snapshot,prompt_definition_id,prompt_version_id,
             prompt_content_sha256,result_schema_code,result_schema_version,expires_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING {_COLUMNS}""",
            (
                result_id,
                kindergarten_id,
                job_id,
                plan_id,
                target_section,
                requested_resource_version,
                target_section_baseline_sha256,
                Jsonb(dict(input_context)),
                input_sha256,
                model_profile_id,
                model_name_snapshot,
                prompt_definition_id,
                prompt_version_id,
                prompt_content_sha256,
                result_schema_code,
                result_schema_version,
                expires_at,
            ),
        )
        record = _record(_row(result))
        assert record is not None
        return record

    def get_by_job(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
    ) -> AiGenerationResultRecord | None:
        return _record(
            _row(
                self.connection.execute(
                    f"""SELECT {_COLUMNS} FROM ai_generation_results
                    WHERE kindergarten_id=%s AND job_id=%s""",
                    (kindergarten_id, job_id),
                )
            )
        )

    def complete_pending(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        output_content: Mapping[str, Any],
        output_sha256: str,
    ) -> bool:
        result = self.connection.execute(
            """UPDATE ai_generation_results
            SET output_content=%s,output_sha256=%s,updated_at=now()
            WHERE kindergarten_id=%s AND job_id=%s
              AND output_content IS NULL AND output_sha256 IS NULL
              AND content_cleared_at IS NULL
              AND adopted_at IS NULL AND rejected_at IS NULL""",
            (
                Jsonb(dict(output_content)),
                output_sha256,
                kindergarten_id,
                job_id,
            ),
        )
        return bool(getattr(result, "rowcount", 0))

    def mark_adopted(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        actor_id: UUID,
        adopted_at: datetime,
    ) -> bool:
        result = self.connection.execute(
            """UPDATE ai_generation_results
            SET adopted_at=%s,adopted_by=%s,updated_at=now()
            WHERE kindergarten_id=%s AND job_id=%s
              AND output_content IS NOT NULL AND output_sha256 IS NOT NULL
              AND content_cleared_at IS NULL
              AND adopted_at IS NULL AND rejected_at IS NULL""",
            (adopted_at, actor_id, kindergarten_id, job_id),
        )
        return bool(getattr(result, "rowcount", 0))

    def mark_rejected(
        self,
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        actor_id: UUID,
        rejected_at: datetime,
    ) -> bool:
        result = self.connection.execute(
            """UPDATE ai_generation_results
            SET rejected_at=%s,rejected_by=%s,updated_at=now()
            WHERE kindergarten_id=%s AND job_id=%s
              AND output_content IS NOT NULL AND output_sha256 IS NOT NULL
              AND content_cleared_at IS NULL
              AND adopted_at IS NULL AND rejected_at IS NULL""",
            (rejected_at, actor_id, kindergarten_id, job_id),
        )
        return bool(getattr(result, "rowcount", 0))

    def clone_failed_to_pending(
        self,
        kindergarten_id: UUID,
        *,
        source_job_id: UUID,
        target_result_id: UUID,
        target_job_id: UUID,
        expires_at: datetime,
    ) -> AiGenerationResultRecord | None:
        result = self.connection.execute(
            f"""INSERT INTO ai_generation_results
            (id,kindergarten_id,job_id,plan_id,target_section,requested_resource_version,
             target_section_baseline_sha256,input_context,input_sha256,model_profile_id,
             model_name_snapshot,prompt_definition_id,prompt_version_id,
             prompt_content_sha256,result_schema_code,result_schema_version,expires_at)
            SELECT %s,source_result.kindergarten_id,%s,source_result.plan_id,
                   source_result.target_section,source_result.requested_resource_version,
                   source_result.target_section_baseline_sha256,source_result.input_context,
                   source_result.input_sha256,source_result.model_profile_id,
                   source_result.model_name_snapshot,source_result.prompt_definition_id,
                   source_result.prompt_version_id,source_result.prompt_content_sha256,
                   source_result.result_schema_code,source_result.result_schema_version,%s
            FROM ai_generation_results AS source_result
            JOIN background_jobs AS source_job
              ON source_job.kindergarten_id=source_result.kindergarten_id
             AND source_job.id=source_result.job_id
            JOIN background_jobs AS target_job
              ON target_job.kindergarten_id=source_result.kindergarten_id
             AND target_job.id=%s
            WHERE source_result.kindergarten_id=%s
              AND source_result.job_id=%s
              AND source_job.execution_status='failed'
              AND target_job.execution_status='pending_dispatch'
              AND target_job.retry_of_job_id=source_job.id
              AND target_job.parent_job_id IS NULL
              AND target_job.plan_id=source_result.plan_id
              AND target_job.target_section=source_result.target_section
              AND target_job.job_type=source_job.job_type
            RETURNING {_COLUMNS}""",
            (
                target_result_id,
                target_job_id,
                expires_at,
                target_job_id,
                kindergarten_id,
                source_job_id,
            ),
        )
        return _record(_row(result))

    def expire_due_previews(
        self,
        kindergarten_id: UUID,
        *,
        now: datetime,
        limit: int,
    ) -> int:
        """将同园到期预览条件收敛为 expired，不修改结果正文或决策字段。"""

        result = self.connection.execute(
            """WITH due AS (
                SELECT job.id
                FROM background_jobs AS job
                JOIN ai_generation_results AS ai_result
                  ON ai_result.kindergarten_id=job.kindergarten_id
                 AND ai_result.job_id=job.id
                WHERE job.kindergarten_id=%s
                  AND job.execution_status='awaiting_confirmation'
                  AND ai_result.expires_at<=%s
                  AND ai_result.adopted_at IS NULL
                  AND ai_result.rejected_at IS NULL
                  AND ai_result.content_cleared_at IS NULL
                ORDER BY ai_result.expires_at,job.id
                LIMIT %s
                FOR UPDATE OF job SKIP LOCKED
            )
            UPDATE background_jobs AS job
            SET execution_status='expired',finished_at=%s,updated_at=%s
            FROM due
            WHERE job.kindergarten_id=%s AND job.id=due.id
              AND job.execution_status='awaiting_confirmation'
            RETURNING job.id""",
            (kindergarten_id, now, limit, now, now, kindergarten_id),
        )
        return len(result.fetchall())

    def clear_retained_content(
        self,
        kindergarten_id: UUID,
        *,
        now: datetime,
        limit: int,
    ) -> int:
        """按园所幂等清理短期正文，同时保留哈希和追溯元数据。"""

        cutoff = now - timedelta(days=30)
        result = self.connection.execute(
            """WITH removable AS (
                SELECT ai_result.id
                FROM ai_generation_results AS ai_result
                JOIN background_jobs AS job
                  ON job.kindergarten_id=ai_result.kindergarten_id
                 AND job.id=ai_result.job_id
                WHERE ai_result.kindergarten_id=%s
                  AND ai_result.content_cleared_at IS NULL
                  AND ai_result.output_content IS NOT NULL
                  AND ai_result.output_sha256 IS NOT NULL
                  AND (
                    ai_result.adopted_at IS NOT NULL
                    OR (
                      ai_result.created_at<=%s
                      AND job.execution_status IN ('rejected','expired','failed')
                    )
                  )
                ORDER BY ai_result.created_at,ai_result.id
                LIMIT %s
                FOR UPDATE OF ai_result SKIP LOCKED
            )
            UPDATE ai_generation_results AS ai_result
            SET input_context=NULL,output_content=NULL,
                content_cleared_at=%s,updated_at=%s
            FROM removable
            WHERE ai_result.kindergarten_id=%s
              AND ai_result.id=removable.id
              AND ai_result.content_cleared_at IS NULL
            RETURNING ai_result.id""",
            (kindergarten_id, cutoff, limit, now, now, kindergarten_id),
        )
        return len(result.fetchall())
