"""建立 AI 模型、提示词与 PostgreSQL 权威任务基础。"""

from __future__ import annotations

import json
from collections.abc import Sequence
from hashlib import sha256
from typing import Any
from uuid import NAMESPACE_URL, UUID, uuid5

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007_ai_prompts_jobs"
down_revision: str | None = "0006_lesson_plans"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_COMMON = [
    "age_group_name",
    "class_name",
    "plan_date",
    "season",
    "teacher_context",
    "teaching_week_text",
    "weekday_text",
]
_CAPABILITIES = ["structured_output", "text"]
_DEFAULTS = (
    (
        "daily_activity_plan.morning_activity",
        "晨间活动",
        _COMMON,
        "prompt.morning_activity.v1",
        "请根据日期 {{plan_date}}、星期 {{weekday_text}}、教学周 {{teaching_week_text}}、"
        "季节 {{season}}、班级 {{class_name}}、年龄段 {{age_group_name}}与教师补充"
        " {{teacher_context}}，生成结构化晨间活动。",
    ),
    (
        "daily_activity_plan.morning_talk",
        "晨间谈话",
        _COMMON,
        "prompt.morning_talk.v1",
        "请根据日期 {{plan_date}}、星期 {{weekday_text}}、教学周 {{teaching_week_text}}、"
        "季节 {{season}}、班级 {{class_name}}、年龄段 {{age_group_name}}与教师补充"
        " {{teacher_context}}，生成结构化晨间谈话。",
    ),
    (
        "daily_activity_plan.group_activity_split",
        "集体活动拆分",
        ["age_group_name", "source_text", "teacher_context"],
        "prompt.group_activity_split.v1",
        "请把原始集体活动 {{source_text}} 按 {{age_group_name}} 幼儿特点与教师补充"
        " {{teacher_context}} 拆分为结构化活动。",
    ),
    (
        "daily_activity_plan.group_activity_add_step",
        "集体活动新增环节",
        ["age_group_name", "group_activity", "teacher_context"],
        "prompt.group_activity_add_step.v1",
        "请为集体活动 {{group_activity}} 按 {{age_group_name}} 幼儿特点与教师补充"
        " {{teacher_context}} 增加一个适龄环节。",
    ),
    (
        "daily_activity_plan.indoor_area_game",
        "室内区域游戏",
        sorted([*_COMMON, "indoor_areas"]),
        "prompt.indoor_area_game.v1",
        "请根据日期 {{plan_date}}、星期 {{weekday_text}}、教学周 {{teaching_week_text}}、"
        "季节 {{season}}、班级 {{class_name}}、年龄段 {{age_group_name}}、教师补充"
        " {{teacher_context}}与室内区域 {{indoor_areas}}，生成结构化区域游戏指导。",
    ),
    (
        "daily_activity_plan.afternoon_outdoor_game",
        "下午户外游戏",
        sorted([*_COMMON, "outdoor_areas"]),
        "prompt.afternoon_outdoor_game.v1",
        "请根据日期 {{plan_date}}、星期 {{weekday_text}}、教学周 {{teaching_week_text}}、"
        "季节 {{season}}、班级 {{class_name}}、年龄段 {{age_group_name}}、教师补充"
        " {{teacher_context}}与户外区域 {{outdoor_areas}}，生成结构化户外游戏指导。",
    ),
    (
        "daily_activity_plan.daily_reflection",
        "一日活动反思",
        ["age_group_name", "class_name", "current_plan", "plan_date"],
        "prompt.daily_reflection.v1",
        "请根据日期 {{plan_date}}、班级 {{class_name}}、年龄段 {{age_group_name}}和五个"
        "上游栏目 {{current_plan}}，生成结构化一日活动反思。",
    ),
)


def _timestamps() -> tuple[sa.Column[Any], sa.Column[Any]]:
    return (
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )


def upgrade() -> None:
    op.create_table(
        "ai_model_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("kindergarten_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("name_normalized", sa.String(120), nullable=False),
        sa.Column("api_base_url", sa.String(500), nullable=False),
        sa.Column("model_name", sa.String(200), nullable=False),
        sa.Column("api_key_ciphertext", sa.LargeBinary()),
        sa.Column("api_key_encryption_version", sa.SmallInteger()),
        sa.Column("api_key_key_id", sa.String(64)),
        sa.Column("api_key_nonce", sa.LargeBinary()),
        sa.Column("api_key_last_four", sa.String(8)),
        sa.Column(
            "call_config_revision", sa.BigInteger(), nullable=False, server_default=sa.text("1")
        ),
        sa.Column("max_concurrency", sa.Integer(), nullable=False, server_default=sa.text("2")),
        sa.Column("rate_limit_per_minute", sa.Integer()),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("risk_confirmed_by", postgresql.UUID(as_uuid=True)),
        sa.Column("risk_confirmed_at", sa.DateTime(timezone=True)),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=False),
        *_timestamps(),
        sa.UniqueConstraint("kindergarten_id", "id", name="uq_ai_model_profiles_kg_id"),
        sa.UniqueConstraint(
            "kindergarten_id", "name_normalized", name="uq_ai_model_profiles_kg_name"
        ),
        sa.ForeignKeyConstraint(["kindergarten_id"], ["kindergartens.id"]),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "created_by"], ["users.kindergarten_id", "users.id"]
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "updated_by"], ["users.kindergarten_id", "users.id"]
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "risk_confirmed_by"], ["users.kindergarten_id", "users.id"]
        ),
        sa.CheckConstraint(
            """(
                api_key_ciphertext IS NULL
                AND api_key_encryption_version IS NULL
                AND api_key_key_id IS NULL
                AND api_key_nonce IS NULL
                AND api_key_last_four IS NULL
            ) OR (
                api_key_ciphertext IS NOT NULL
                AND api_key_encryption_version IS NOT NULL
                AND api_key_encryption_version >= 1
                AND api_key_key_id IS NOT NULL
                AND api_key_nonce IS NOT NULL
                AND octet_length(api_key_nonce) = 12
                AND api_key_last_four IS NOT NULL
            )""",
            name="ck_ai_model_profiles_key_envelope",
        ),
        sa.CheckConstraint(
            "call_config_revision >= 1", name="ck_ai_model_profiles_call_config_revision"
        ),
        sa.CheckConstraint("max_concurrency >= 1", name="ck_ai_model_profiles_concurrency"),
        sa.CheckConstraint(
            "rate_limit_per_minute IS NULL OR rate_limit_per_minute >= 1",
            name="ck_ai_model_profiles_rate_limit",
        ),
        sa.CheckConstraint(
            """(risk_confirmed_by IS NULL AND risk_confirmed_at IS NULL)
            OR (risk_confirmed_by IS NOT NULL AND risk_confirmed_at IS NOT NULL)""",
            name="ck_ai_model_profiles_risk_confirmation",
        ),
        sa.CheckConstraint(
            """NOT is_active OR (
                api_key_ciphertext IS NOT NULL
                AND risk_confirmed_by IS NOT NULL
                AND risk_confirmed_at IS NOT NULL
            )""",
            name="ck_ai_model_profiles_enable_ready",
        ),
    )
    op.create_index(
        "uq_ai_model_profiles_default",
        "ai_model_profiles",
        ["kindergarten_id"],
        unique=True,
        postgresql_where=sa.text("is_default AND is_active"),
    )

    op.create_table(
        "ai_model_profile_capabilities",
        sa.Column("kindergarten_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("model_profile_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("capability_code", sa.String(64), primary_key=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "model_profile_id"],
            ["ai_model_profiles.kindergarten_id", "ai_model_profiles.id"],
        ),
        sa.CheckConstraint(
            "capability_code IN ('text','vision','structured_output')",
            name="ck_ai_model_capabilities_code",
        ),
    )

    op.create_table(
        "prompt_definitions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("kindergarten_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("code", sa.String(160), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("variable_whitelist", postgresql.JSONB(), nullable=False),
        sa.Column("required_capabilities", postgresql.JSONB(), nullable=False),
        sa.Column("result_schema_code", sa.String(160), nullable=False),
        sa.Column(
            "result_schema_version", sa.Integer(), nullable=False, server_default=sa.text("1")
        ),
        sa.Column("model_profile_id", postgresql.UUID(as_uuid=True)),
        sa.Column("active_custom_version_id", postgresql.UUID(as_uuid=True)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_timestamps(),
        sa.UniqueConstraint("kindergarten_id", "id", name="uq_prompt_definitions_kg_id"),
        sa.UniqueConstraint("kindergarten_id", "code", name="uq_prompt_definitions_kg_code"),
        sa.ForeignKeyConstraint(["kindergarten_id"], ["kindergartens.id"]),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "model_profile_id"],
            ["ai_model_profiles.kindergarten_id", "ai_model_profiles.id"],
        ),
        sa.CheckConstraint(
            "jsonb_typeof(variable_whitelist)='array'",
            name="ck_prompt_definitions_whitelist",
        ),
        sa.CheckConstraint(
            "jsonb_typeof(required_capabilities)='array'",
            name="ck_prompt_definitions_capabilities",
        ),
        sa.CheckConstraint(
            "result_schema_version = 1", name="ck_prompt_definitions_schema_version"
        ),
    )

    op.create_table(
        "prompt_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("kindergarten_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("prompt_definition_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("source_type", sa.String(16), nullable=False),
        sa.Column("lifecycle_state", sa.String(16), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("content_sha256", sa.String(64), nullable=False),
        sa.Column("based_on_version_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
        sa.Column("published_by", postgresql.UUID(as_uuid=True)),
        sa.Column("published_at", sa.DateTime(timezone=True)),
        *_timestamps(),
        sa.UniqueConstraint(
            "kindergarten_id",
            "prompt_definition_id",
            "id",
            name="uq_prompt_versions_definition_id",
        ),
        sa.UniqueConstraint(
            "kindergarten_id",
            "prompt_definition_id",
            "version_number",
            name="uq_prompt_versions_number",
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "prompt_definition_id"],
            ["prompt_definitions.kindergarten_id", "prompt_definitions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "prompt_definition_id", "based_on_version_id"],
            [
                "prompt_versions.kindergarten_id",
                "prompt_versions.prompt_definition_id",
                "prompt_versions.id",
            ],
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "created_by"], ["users.kindergarten_id", "users.id"]
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "published_by"], ["users.kindergarten_id", "users.id"]
        ),
        sa.CheckConstraint("version_number >= 1", name="ck_prompt_versions_number"),
        sa.CheckConstraint("source_type IN ('system','custom')", name="ck_prompt_versions_source"),
        sa.CheckConstraint(
            "lifecycle_state IN ('draft','published')", name="ck_prompt_versions_state"
        ),
        sa.CheckConstraint("content_sha256 ~ '^[0-9a-f]{64}$'", name="ck_prompt_versions_sha256"),
        sa.CheckConstraint(
            """(
                lifecycle_state='draft'
                AND published_at IS NULL
                AND published_by IS NULL
            ) OR (
                lifecycle_state='published'
                AND published_at IS NOT NULL
                AND (
                    (source_type='system' AND published_by IS NULL)
                    OR (source_type='custom' AND published_by IS NOT NULL)
                )
            )""",
            name="ck_prompt_versions_publication",
        ),
    )
    op.create_index(
        "uq_prompt_versions_single_draft",
        "prompt_versions",
        ["kindergarten_id", "prompt_definition_id"],
        unique=True,
        postgresql_where=sa.text("source_type='custom' AND lifecycle_state='draft'"),
    )
    op.create_foreign_key(
        "fk_prompt_definitions_active_custom",
        "prompt_definitions",
        "prompt_versions",
        ["kindergarten_id", "id", "active_custom_version_id"],
        ["kindergarten_id", "prompt_definition_id", "id"],
    )
    op.execute(
        """
        CREATE FUNCTION reject_published_prompt_version_mutation()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF OLD.lifecycle_state = 'published' THEN
                RAISE EXCEPTION 'published prompt versions are immutable';
            END IF;
            RETURN NEW;
        END;
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER prompt_versions_published_immutable
        BEFORE UPDATE OR DELETE ON prompt_versions
        FOR EACH ROW EXECUTE FUNCTION reject_published_prompt_version_mutation()
        """
    )

    op.create_table(
        "background_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("kindergarten_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("parent_job_id", postgresql.UUID(as_uuid=True)),
        sa.Column("retry_of_job_id", postgresql.UUID(as_uuid=True)),
        sa.Column("job_type", sa.String(64), nullable=False),
        sa.Column("execution_status", sa.String(32)),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True)),
        sa.Column("target_section", sa.String(64)),
        sa.Column("requested_resource_version", sa.Integer()),
        sa.Column("idempotency_scope", sa.String(300)),
        sa.Column("idempotency_key", sa.String(200)),
        sa.Column("request_fingerprint_sha256", sa.String(64)),
        sa.Column("attempt_count", sa.Integer()),
        sa.Column("max_attempts", sa.Integer()),
        sa.Column("requested_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("request_id", postgresql.UUID(as_uuid=True)),
        sa.Column("trace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lease_owner", sa.String(160)),
        sa.Column("lease_expires_at", sa.DateTime(timezone=True)),
        sa.Column("last_heartbeat_at", sa.DateTime(timezone=True)),
        sa.Column("queued_at", sa.DateTime(timezone=True)),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("error_code", sa.String(64)),
        sa.Column("error_summary", sa.String(1000)),
        *_timestamps(),
        sa.UniqueConstraint("kindergarten_id", "id", name="uq_background_jobs_kg_id"),
        sa.UniqueConstraint("kindergarten_id", "plan_id", "id", name="uq_background_jobs_plan_id"),
        sa.ForeignKeyConstraint(["kindergarten_id"], ["kindergartens.id"]),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "requested_by"], ["users.kindergarten_id", "users.id"]
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "parent_job_id"],
            ["background_jobs.kindergarten_id", "background_jobs.id"],
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "retry_of_job_id"],
            ["background_jobs.kindergarten_id", "background_jobs.id"],
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "plan_id"],
            ["daily_activity_plans.kindergarten_id", "daily_activity_plans.id"],
        ),
        sa.CheckConstraint(
            "job_type IN ('ai.batch','ai.section','prompt.test','word.export')",
            name="ck_background_jobs_type",
        ),
        sa.CheckConstraint(
            """(
                job_type = 'ai.batch'
                AND execution_status IS NULL
                AND attempt_count IS NULL
                AND max_attempts IS NULL
                AND lease_owner IS NULL
                AND lease_expires_at IS NULL
                AND last_heartbeat_at IS NULL
                AND queued_at IS NULL
                AND started_at IS NULL
                AND finished_at IS NULL
            ) OR (
                job_type <> 'ai.batch'
                AND execution_status IS NOT NULL
                AND attempt_count IS NOT NULL
                AND max_attempts = 3
            )""",
            name="ck_background_jobs_batch_execution",
        ),
        sa.CheckConstraint(
            """execution_status IS NULL OR execution_status IN
            ('pending_dispatch','queued','running','retrying','awaiting_confirmation',
             'succeeded','failed','adopted','rejected','expired')""",
            name="ck_background_jobs_status",
        ),
        sa.CheckConstraint(
            """(idempotency_scope IS NULL AND idempotency_key IS NULL
                AND request_fingerprint_sha256 IS NULL)
            OR (idempotency_scope IS NOT NULL AND idempotency_key IS NOT NULL
                AND request_fingerprint_sha256 ~ '^[0-9a-f]{64}$')""",
            name="ck_background_jobs_idempotency",
        ),
        sa.CheckConstraint(
            "attempt_count IS NULL OR (attempt_count >= 0 AND attempt_count <= max_attempts)",
            name="ck_background_jobs_attempts",
        ),
        sa.CheckConstraint(
            "(lease_owner IS NULL AND lease_expires_at IS NULL AND last_heartbeat_at IS NULL)"
            " OR (lease_owner IS NOT NULL AND lease_expires_at IS NOT NULL)",
            name="ck_background_jobs_lease",
        ),
        sa.CheckConstraint(
            """requested_resource_version IS NULL OR requested_resource_version > 0""",
            name="ck_background_jobs_requested_resource_version",
        ),
        sa.CheckConstraint(
            "parent_job_id IS NULL OR parent_job_id <> id",
            name="ck_background_jobs_parent_not_self",
        ),
        sa.CheckConstraint(
            "retry_of_job_id IS NULL OR retry_of_job_id <> id",
            name="ck_background_jobs_retry_not_self",
        ),
        sa.CheckConstraint(
            """execution_status IS NULL
            OR (
                execution_status IN ('succeeded','failed','adopted','rejected','expired')
                AND finished_at IS NOT NULL
            )
            OR (
                execution_status NOT IN ('succeeded','failed','adopted','rejected','expired')
                AND finished_at IS NULL
            )""",
            name="ck_background_jobs_terminal_finished",
        ),
        sa.CheckConstraint(
            """execution_status IS NULL
            OR (
                execution_status = 'failed'
                AND error_code IS NOT NULL
            )
            OR (
                execution_status <> 'failed'
                AND error_code IS NULL
                AND error_summary IS NULL
            )""",
            name="ck_background_jobs_failure_error",
        ),
    )
    op.create_index(
        "uq_background_jobs_idempotency",
        "background_jobs",
        ["kindergarten_id", "requested_by", "idempotency_scope", "idempotency_key"],
        unique=True,
        postgresql_where=sa.text("idempotency_scope IS NOT NULL"),
    )
    op.create_index(
        "uq_background_jobs_parent_section",
        "background_jobs",
        ["kindergarten_id", "parent_job_id", "target_section"],
        unique=True,
        postgresql_where=sa.text("parent_job_id IS NOT NULL"),
    )
    op.create_index(
        "ix_background_jobs_dispatch",
        "background_jobs",
        ["execution_status", "lease_expires_at", "created_at"],
    )

    op.create_table(
        "prompt_test_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("kindergarten_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("prompt_definition_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("prompt_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("input_context", postgresql.JSONB(), nullable=False),
        sa.Column("input_sha256", sa.String(64), nullable=False),
        sa.Column("prompt_content", sa.Text(), nullable=False),
        sa.Column("prompt_content_sha256", sa.String(64), nullable=False),
        sa.Column("result_schema_code", sa.String(160), nullable=False),
        sa.Column("result_schema_version", sa.Integer(), nullable=False),
        sa.Column("model_call_snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("input_summary", postgresql.JSONB(), nullable=False),
        sa.Column("output_content", postgresql.JSONB()),
        sa.Column("status", sa.String(32), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("elapsed_ms", sa.Integer()),
        sa.Column("error_code", sa.String(64)),
        sa.Column("error_summary", sa.String(1000)),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        *_timestamps(),
        sa.UniqueConstraint("kindergarten_id", "id", name="uq_prompt_test_runs_kg_id"),
        sa.UniqueConstraint("kindergarten_id", "job_id", name="uq_prompt_test_runs_job"),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "prompt_definition_id"],
            ["prompt_definitions.kindergarten_id", "prompt_definitions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "prompt_definition_id", "prompt_version_id"],
            [
                "prompt_versions.kindergarten_id",
                "prompt_versions.prompt_definition_id",
                "prompt_versions.id",
            ],
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "model_profile_id"],
            ["ai_model_profiles.kindergarten_id", "ai_model_profiles.id"],
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "job_id"],
            ["background_jobs.kindergarten_id", "background_jobs.id"],
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "created_by"], ["users.kindergarten_id", "users.id"]
        ),
        sa.CheckConstraint("input_sha256 ~ '^[0-9a-f]{64}$'", name="ck_prompt_test_runs_input_sha"),
        sa.CheckConstraint(
            "prompt_content_sha256 ~ '^[0-9a-f]{64}$'",
            name="ck_prompt_test_runs_prompt_sha",
        ),
        sa.CheckConstraint(
            """model_call_snapshot ?& ARRAY[
                'profile_id','base_url','model_name','capabilities','call_config_revision'
            ] AND (model_call_snapshot - ARRAY[
                'profile_id','base_url','model_name','capabilities','call_config_revision'
            ]) = '{}'::jsonb AND NOT model_call_snapshot ?| ARRAY[
                'api_key','api_key_ciphertext','api_key_nonce','api_key_key_id','key_id'
            ]""",
            name="ck_prompt_test_runs_model_call_snapshot",
        ),
        sa.CheckConstraint(
            """input_summary ?& ARRAY['provided_variable_names','all_values_redacted']
            AND (input_summary - ARRAY[
                'provided_variable_names','all_values_redacted'
            ]) = '{}'::jsonb
            AND input_summary->>'all_values_redacted'='true'""",
            name="ck_prompt_test_runs_input_summary",
        ),
        sa.CheckConstraint(
            "status IN ('pending','succeeded','failed')", name="ck_prompt_test_runs_status"
        ),
        sa.CheckConstraint(
            "elapsed_ms IS NULL OR elapsed_ms >= 0", name="ck_prompt_test_runs_elapsed"
        ),
        sa.CheckConstraint(
            """(
                status='pending'
                AND output_content IS NULL
                AND elapsed_ms IS NULL
                AND error_code IS NULL
                AND error_summary IS NULL
            ) OR (
                status='succeeded'
                AND output_content IS NOT NULL
                AND jsonb_typeof(output_content)='object'
                AND elapsed_ms IS NOT NULL
                AND error_code IS NULL
                AND error_summary IS NULL
            ) OR (
                status='failed'
                AND output_content IS NULL
                AND error_code IS NOT NULL
            )""",
            name="ck_prompt_test_runs_outcome",
        ),
    )
    op.create_index(
        "ix_prompt_test_runs_retention",
        "prompt_test_runs",
        ["kindergarten_id", "prompt_definition_id", "created_at"],
    )
    op.execute(
        """
        CREATE FUNCTION reject_prompt_test_frozen_context_mutation()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF ROW(
                NEW.prompt_definition_id, NEW.prompt_version_id, NEW.model_profile_id, NEW.job_id,
                NEW.input_context, NEW.input_sha256, NEW.prompt_content,
                NEW.prompt_content_sha256, NEW.result_schema_code, NEW.result_schema_version,
                NEW.model_call_snapshot, NEW.input_summary
            ) IS DISTINCT FROM ROW(
                OLD.prompt_definition_id, OLD.prompt_version_id, OLD.model_profile_id, OLD.job_id,
                OLD.input_context, OLD.input_sha256, OLD.prompt_content,
                OLD.prompt_content_sha256, OLD.result_schema_code, OLD.result_schema_version,
                OLD.model_call_snapshot, OLD.input_summary
            ) THEN
                RAISE EXCEPTION 'prompt test frozen context is immutable';
            END IF;
            RETURN NEW;
        END;
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER prompt_test_runs_frozen_context
        BEFORE UPDATE ON prompt_test_runs
        FOR EACH ROW EXECUTE FUNCTION reject_prompt_test_frozen_context_mutation()
        """
    )
    _seed_defaults()


def _seed_defaults() -> None:
    bind = op.get_bind()
    kindergarten_ids = [
        UUID(str(row[0]))
        for row in bind.execute(sa.text("SELECT id FROM kindergartens ORDER BY id")).fetchall()
    ]
    for kindergarten_id in kindergarten_ids:
        for code, name, whitelist, schema_code, content in _DEFAULTS:
            definition_id = uuid5(
                NAMESPACE_URL,
                f"child-manager:{kindergarten_id}:prompt-definition:{code}",
            )
            version_id = uuid5(
                NAMESPACE_URL,
                f"child-manager:{kindergarten_id}:prompt-version:{code}:system-v1",
            )
            bind.execute(
                sa.text(
                    """INSERT INTO prompt_definitions
                    (id, kindergarten_id, code, name, variable_whitelist,
                     required_capabilities, result_schema_code, result_schema_version,
                     is_active)
                    VALUES (:id,:kg,:code,:name,CAST(:variables AS jsonb),
                            CAST(:capabilities AS jsonb),:schema_code,1,true)
                    ON CONFLICT (kindergarten_id, code) DO NOTHING"""
                ),
                {
                    "id": definition_id,
                    "kg": kindergarten_id,
                    "code": code,
                    "name": name,
                    "variables": json.dumps(sorted(whitelist)),
                    "capabilities": json.dumps(_CAPABILITIES),
                    "schema_code": schema_code,
                },
            )
            bind.execute(
                sa.text(
                    """INSERT INTO prompt_versions
                    (id, kindergarten_id, prompt_definition_id, version_number,
                     source_type, lifecycle_state, content, content_sha256,
                     published_at)
                    VALUES (:id,:kg,:definition_id,1,'system','published',
                            :content,:digest,now())
                    ON CONFLICT (kindergarten_id, prompt_definition_id, version_number)
                    DO NOTHING"""
                ),
                {
                    "id": version_id,
                    "kg": kindergarten_id,
                    "definition_id": definition_id,
                    "content": content,
                    "digest": sha256(content.encode()).hexdigest(),
                },
            )


def downgrade() -> None:
    op.drop_table("prompt_test_runs")
    op.execute("DROP FUNCTION reject_prompt_test_frozen_context_mutation()")
    op.drop_table("background_jobs")
    op.drop_constraint(
        "fk_prompt_definitions_active_custom",
        "prompt_definitions",
        type_="foreignkey",
    )
    op.drop_table("prompt_versions")
    op.execute("DROP FUNCTION reject_published_prompt_version_mutation()")
    op.drop_table("prompt_definitions")
    op.drop_table("ai_model_profile_capabilities")
    op.drop_table("ai_model_profiles")
