"""建立 AI 生成结果冻结输入与一次性输出生命周期。"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0008_ai_generation_results"
down_revision: str | None = "0007_ai_prompts_jobs"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamps() -> tuple[sa.Column[Any], sa.Column[Any]]:
    return (
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )


def upgrade() -> None:
    op.create_table(
        "ai_generation_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("kindergarten_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_section", sa.String(64), nullable=False),
        sa.Column("requested_resource_version", sa.Integer(), nullable=False),
        # CHECK 同样强制非空; 非法 pending 形状使用统一的约束错误类型。
        sa.Column("target_section_baseline_sha256", sa.String(64)),
        sa.Column("input_context", postgresql.JSONB()),
        sa.Column("input_sha256", sa.String(64), nullable=False),
        sa.Column("model_profile_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("model_name_snapshot", sa.String(200), nullable=False),
        sa.Column("prompt_definition_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("prompt_version_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("prompt_content_sha256", sa.String(64), nullable=False),
        sa.Column("result_schema_code", sa.String(160), nullable=False),
        sa.Column("result_schema_version", sa.Integer(), nullable=False),
        sa.Column("output_content", postgresql.JSONB()),
        sa.Column("output_sha256", sa.String(64)),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("adopted_at", sa.DateTime(timezone=True)),
        sa.Column("adopted_by", postgresql.UUID(as_uuid=True)),
        sa.Column("rejected_at", sa.DateTime(timezone=True)),
        sa.Column("rejected_by", postgresql.UUID(as_uuid=True)),
        sa.Column("content_cleared_at", sa.DateTime(timezone=True)),
        *_timestamps(),
        sa.UniqueConstraint("kindergarten_id", "id", name="uq_ai_generation_results_kg_id"),
        sa.UniqueConstraint("kindergarten_id", "job_id", name="uq_ai_generation_results_job"),
        sa.ForeignKeyConstraint(["kindergarten_id"], ["kindergartens.id"]),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "plan_id"],
            ["daily_activity_plans.kindergarten_id", "daily_activity_plans.id"],
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "plan_id", "job_id"],
            [
                "background_jobs.kindergarten_id",
                "background_jobs.plan_id",
                "background_jobs.id",
            ],
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "model_profile_id"],
            ["ai_model_profiles.kindergarten_id", "ai_model_profiles.id"],
        ),
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
            ["kindergarten_id", "adopted_by"],
            ["users.kindergarten_id", "users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "rejected_by"],
            ["users.kindergarten_id", "users.id"],
        ),
        sa.CheckConstraint(
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
        sa.CheckConstraint(
            "requested_resource_version > 0 AND result_schema_version > 0",
            name="ck_ai_generation_results_versions",
        ),
        sa.CheckConstraint(
            """target_section_baseline_sha256 IS NOT NULL
            AND target_section_baseline_sha256 ~ '^[0-9a-f]{64}$'
            AND input_sha256 ~ '^[0-9a-f]{64}$'
            AND prompt_content_sha256 ~ '^[0-9a-f]{64}$'
            AND (output_sha256 IS NULL OR output_sha256 ~ '^[0-9a-f]{64}$')""",
            name="ck_ai_generation_results_hashes",
        ),
        sa.CheckConstraint(
            """(input_context IS NULL OR jsonb_typeof(input_context)='object')
            AND (output_content IS NULL OR jsonb_typeof(output_content)='object')""",
            name="ck_ai_generation_results_json_objects",
        ),
        sa.CheckConstraint(
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
        sa.CheckConstraint(
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
        sa.CheckConstraint(
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
    )
    op.create_index(
        "ix_ai_generation_results_plan_section",
        "ai_generation_results",
        ["kindergarten_id", "plan_id", "target_section", sa.text("created_at DESC")],
    )
    op.create_index(
        "ix_ai_generation_results_expires_pending",
        "ai_generation_results",
        ["expires_at"],
        postgresql_where=sa.text("adopted_at IS NULL AND rejected_at IS NULL"),
    )
    op.execute(
        """
        CREATE FUNCTION reject_ai_generation_result_frozen_mutation()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF ROW(
                NEW.kindergarten_id,
                NEW.job_id,
                NEW.plan_id,
                NEW.target_section,
                NEW.requested_resource_version,
                NEW.target_section_baseline_sha256,
                NEW.input_sha256,
                NEW.model_profile_id,
                NEW.model_name_snapshot,
                NEW.prompt_definition_id,
                NEW.prompt_version_id,
                NEW.prompt_content_sha256,
                NEW.result_schema_code,
                NEW.result_schema_version
            ) IS DISTINCT FROM ROW(
                OLD.kindergarten_id,
                OLD.job_id,
                OLD.plan_id,
                OLD.target_section,
                OLD.requested_resource_version,
                OLD.target_section_baseline_sha256,
                OLD.input_sha256,
                OLD.model_profile_id,
                OLD.model_name_snapshot,
                OLD.prompt_definition_id,
                OLD.prompt_version_id,
                OLD.prompt_content_sha256,
                OLD.result_schema_code,
                OLD.result_schema_version
            ) THEN
                RAISE EXCEPTION 'AI generation result frozen fields are immutable';
            END IF;

            IF NEW.input_context IS DISTINCT FROM OLD.input_context
               AND NOT (
                   OLD.input_context IS NOT NULL
                   AND NEW.input_context IS NULL
                   AND OLD.content_cleared_at IS NULL
                   AND NEW.content_cleared_at IS NOT NULL
                   AND OLD.output_sha256 IS NOT NULL
               )
            THEN
                RAISE EXCEPTION 'AI generation result input context is immutable';
            END IF;

            IF NEW.content_cleared_at IS DISTINCT FROM OLD.content_cleared_at
               AND NOT (
                   OLD.content_cleared_at IS NULL
                   AND NEW.content_cleared_at IS NOT NULL
                   AND OLD.output_sha256 IS NOT NULL
               )
            THEN
                RAISE EXCEPTION 'AI generation result cleanup marker is immutable';
            END IF;

            IF OLD.adopted_at IS NOT NULL
               AND ROW(NEW.adopted_at, NEW.adopted_by)
                   IS DISTINCT FROM ROW(OLD.adopted_at, OLD.adopted_by)
            THEN
                RAISE EXCEPTION 'AI generation result adoption is immutable';
            END IF;

            IF OLD.rejected_at IS NOT NULL
               AND ROW(NEW.rejected_at, NEW.rejected_by)
                   IS DISTINCT FROM ROW(OLD.rejected_at, OLD.rejected_by)
            THEN
                RAISE EXCEPTION 'AI generation result rejection is immutable';
            END IF;

            IF (
                (OLD.adopted_at IS NULL AND NEW.adopted_at IS NOT NULL)
                OR (OLD.rejected_at IS NULL AND NEW.rejected_at IS NOT NULL)
            ) AND OLD.output_sha256 IS NULL
            THEN
                RAISE EXCEPTION 'AI generation result decision requires existing output';
            END IF;

            RETURN NEW;
        END;
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER ai_generation_results_frozen_fields
        BEFORE UPDATE ON ai_generation_results
        FOR EACH ROW EXECUTE FUNCTION reject_ai_generation_result_frozen_mutation()
        """
    )
    op.execute(
        """
        CREATE FUNCTION reject_ai_generation_result_output_overwrite()
        RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF OLD.output_sha256 IS NOT NULL THEN
                IF NEW.output_sha256 IS DISTINCT FROM OLD.output_sha256 THEN
                    RAISE EXCEPTION 'AI generation result output hash is immutable';
                END IF;
                IF NEW.output_content IS DISTINCT FROM OLD.output_content
                   AND NOT (
                       OLD.output_content IS NOT NULL
                       AND NEW.output_content IS NULL
                       AND OLD.content_cleared_at IS NULL
                       AND NEW.content_cleared_at IS NOT NULL
                   )
                THEN
                    RAISE EXCEPTION 'AI generation result output is write-once';
                END IF;
            END IF;
            RETURN NEW;
        END;
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER ai_generation_results_output_once
        BEFORE UPDATE ON ai_generation_results
        FOR EACH ROW EXECUTE FUNCTION reject_ai_generation_result_output_overwrite()
        """
    )


def downgrade() -> None:
    op.drop_table("ai_generation_results")
    op.execute("DROP FUNCTION reject_ai_generation_result_output_overwrite()")
    op.execute("DROP FUNCTION reject_ai_generation_result_frozen_mutation()")
