"""通用后台任务 ORM 模型。"""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.backend.database.base import Base


class BackgroundJob(Base):
    __tablename__ = "background_jobs"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    kindergarten_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    parent_job_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    retry_of_job_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    job_type: Mapped[str] = mapped_column(String(64), nullable=False)
    execution_status: Mapped[str | None] = mapped_column(String(32))
    plan_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    target_section: Mapped[str | None] = mapped_column(String(64))
    requested_resource_version: Mapped[int | None] = mapped_column(Integer)
    idempotency_scope: Mapped[str | None] = mapped_column(String(300))
    idempotency_key: Mapped[str | None] = mapped_column(String(200))
    request_fingerprint_sha256: Mapped[str | None] = mapped_column(String(64))
    attempt_count: Mapped[int | None] = mapped_column(Integer)
    max_attempts: Mapped[int | None] = mapped_column(Integer)
    requested_by: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    request_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    trace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    lease_owner: Mapped[str | None] = mapped_column(String(160))
    lease_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    queued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_code: Mapped[str | None] = mapped_column(String(64))
    error_summary: Mapped[str | None] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AiGenerationResult(Base):
    __tablename__ = "ai_generation_results"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    kindergarten_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    job_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    plan_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    target_section: Mapped[str] = mapped_column(String(64), nullable=False)
    requested_resource_version: Mapped[int] = mapped_column(Integer, nullable=False)
    # 数据库 CHECK 提供等价的非空约束; 非法 pending 形状统一返回 CheckViolation。
    target_section_baseline_sha256: Mapped[str | None] = mapped_column(String(64))
    input_context: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    input_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    model_profile_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    model_name_snapshot: Mapped[str] = mapped_column(String(200), nullable=False)
    prompt_definition_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    prompt_version_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    prompt_content_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    result_schema_code: Mapped[str] = mapped_column(String(160), nullable=False)
    result_schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    output_content: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    output_sha256: Mapped[str | None] = mapped_column(String(64))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    adopted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    adopted_by: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    rejected_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rejected_by: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    content_cleared_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("kindergarten_id", "id", name="uq_ai_generation_results_kg_id"),
        UniqueConstraint("kindergarten_id", "job_id", name="uq_ai_generation_results_job"),
        ForeignKeyConstraint(["kindergarten_id"], ["kindergartens.id"]),
        ForeignKeyConstraint(
            ["kindergarten_id", "plan_id"],
            ["daily_activity_plans.kindergarten_id", "daily_activity_plans.id"],
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "plan_id", "job_id"],
            [
                "background_jobs.kindergarten_id",
                "background_jobs.plan_id",
                "background_jobs.id",
            ],
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "model_profile_id"],
            ["ai_model_profiles.kindergarten_id", "ai_model_profiles.id"],
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "prompt_definition_id"],
            ["prompt_definitions.kindergarten_id", "prompt_definitions.id"],
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "prompt_definition_id", "prompt_version_id"],
            [
                "prompt_versions.kindergarten_id",
                "prompt_versions.prompt_definition_id",
                "prompt_versions.id",
            ],
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "adopted_by"],
            ["users.kindergarten_id", "users.id"],
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "rejected_by"],
            ["users.kindergarten_id", "users.id"],
        ),
        CheckConstraint(
            """target_section IN (
                'morning_activity',
                'morning_talk',
                'group_activity',
                'indoor_area_game',
                'afternoon_outdoor_game',
                'daily_reflection'
            )""",
            name="ck_ai_generation_results_target_section",
        ),
        CheckConstraint(
            "requested_resource_version > 0 AND result_schema_version > 0",
            name="ck_ai_generation_results_versions",
        ),
        CheckConstraint(
            """target_section_baseline_sha256 IS NOT NULL
            AND target_section_baseline_sha256 ~ '^[0-9a-f]{64}$'
            AND input_sha256 ~ '^[0-9a-f]{64}$'
            AND prompt_content_sha256 ~ '^[0-9a-f]{64}$'
            AND (output_sha256 IS NULL OR output_sha256 ~ '^[0-9a-f]{64}$')""",
            name="ck_ai_generation_results_hashes",
        ),
        CheckConstraint(
            """(input_context IS NULL OR jsonb_typeof(input_context)='object')
            AND (output_content IS NULL OR jsonb_typeof(output_content)='object')""",
            name="ck_ai_generation_results_json_objects",
        ),
        CheckConstraint(
            """(
                output_content IS NULL
                AND output_sha256 IS NULL
                AND content_cleared_at IS NULL
            ) OR (
                output_content IS NOT NULL
                AND output_sha256 IS NOT NULL
                AND content_cleared_at IS NULL
            ) OR (
                output_content IS NULL
                AND output_sha256 IS NOT NULL
                AND content_cleared_at IS NOT NULL
            )""",
            name="ck_ai_generation_results_output_lifecycle",
        ),
        CheckConstraint(
            """(
                content_cleared_at IS NULL
                AND input_context IS NOT NULL
            ) OR (
                content_cleared_at IS NOT NULL
                AND input_context IS NULL
                AND output_content IS NULL
                AND output_sha256 IS NOT NULL
            )""",
            name="ck_ai_generation_results_content_cleanup",
        ),
        CheckConstraint(
            """((adopted_at IS NULL AND adopted_by IS NULL)
                OR (adopted_at IS NOT NULL AND adopted_by IS NOT NULL))
            AND ((rejected_at IS NULL AND rejected_by IS NULL)
                OR (rejected_at IS NOT NULL AND rejected_by IS NOT NULL))
            AND NOT (adopted_at IS NOT NULL AND rejected_at IS NOT NULL)
            AND (
                (adopted_at IS NULL AND rejected_at IS NULL)
                OR output_sha256 IS NOT NULL
            )""",
            name="ck_ai_generation_results_decision",
        ),
        Index(
            "ix_ai_generation_results_plan_section",
            "kindergarten_id",
            "plan_id",
            "target_section",
            text("created_at DESC"),
        ),
        Index(
            "ix_ai_generation_results_expires_pending",
            "expires_at",
            postgresql_where=text("adopted_at IS NULL AND rejected_at IS NULL"),
        ),
    )
