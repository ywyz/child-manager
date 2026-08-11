"""增加桌面 Slice 2A 非敏感 AI 配置、提示词覆盖与预览。"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002_desktop_ai"
down_revision = "0001_desktop_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_configuration",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("base_url", sa.Text()),
        sa.Column("model_name", sa.Text()),
        sa.Column("credential_configured", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Integer(), nullable=False),
        sa.Column("created_at_utc_ms", sa.Integer(), nullable=False),
        sa.Column("updated_at_utc_ms", sa.Integer(), nullable=False),
        sa.CheckConstraint("id = 1", name="ck_ai_configuration_singleton"),
        sa.CheckConstraint(
            "base_url IS NULL OR length(trim(base_url)) BETWEEN 1 AND 2048",
            name="ck_ai_configuration_base_url",
        ),
        sa.CheckConstraint(
            "model_name IS NULL OR length(trim(model_name)) BETWEEN 1 AND 200",
            name="ck_ai_configuration_model_name",
        ),
        sa.CheckConstraint(
            "credential_configured IN (0, 1)",
            name="ck_ai_configuration_credential_configured",
        ),
        sa.CheckConstraint("enabled IN (0, 1)", name="ck_ai_configuration_enabled"),
    )
    op.create_table(
        "prompt_overrides",
        sa.Column("prompt_code", sa.Text(), primary_key=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("updated_at_utc_ms", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "prompt_code IN ('morning_activity', 'morning_talk', 'indoor_area_game', "
            "'afternoon_outdoor_game', 'daily_reflection')",
            name="ck_prompt_overrides_prompt_code",
        ),
        sa.CheckConstraint(
            "length(trim(content)) BETWEEN 1 AND 12000",
            name="ck_prompt_overrides_content",
        ),
    )
    op.create_table(
        "ai_previews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lesson_plan_id", sa.Integer(), nullable=False),
        sa.Column("operation_id", sa.Text(), nullable=False),
        sa.Column("section_code", sa.Text(), nullable=False),
        sa.Column("result_schema_code", sa.Text(), nullable=False),
        sa.Column("result_json", sa.Text(), nullable=False),
        sa.Column("frozen_input_sha256", sa.Text(), nullable=False),
        sa.Column("target_section_sha256", sa.Text(), nullable=False),
        sa.Column("state", sa.Text(), nullable=False),
        sa.Column("created_at_utc_ms", sa.Integer(), nullable=False),
        sa.Column("decided_at_utc_ms", sa.Integer()),
        sa.ForeignKeyConstraint(
            ["lesson_plan_id"],
            ["lesson_plans.id"],
            name="fk_ai_previews_lesson_plan_id_lesson_plans",
            ondelete="CASCADE",
        ),
        sa.CheckConstraint("length(operation_id) = 36", name="ck_ai_previews_operation_id"),
        sa.CheckConstraint(
            "section_code IN ('morning_activity', 'morning_talk', 'indoor_area_game', "
            "'afternoon_outdoor_game', 'daily_reflection')",
            name="ck_ai_previews_section_code",
        ),
        sa.CheckConstraint(
            "result_schema_code = section_code",
            name="ck_ai_previews_result_schema_code",
        ),
        sa.CheckConstraint("json_valid(result_json)", name="ck_ai_previews_result_json"),
        sa.CheckConstraint(
            "length(frozen_input_sha256) = 64 AND frozen_input_sha256 NOT GLOB '*[^0-9a-f]*'",
            name="ck_ai_previews_frozen_input_sha256",
        ),
        sa.CheckConstraint(
            "length(target_section_sha256) = 64 AND target_section_sha256 NOT GLOB '*[^0-9a-f]*'",
            name="ck_ai_previews_target_section_sha256",
        ),
        sa.CheckConstraint(
            "state IN ('ready', 'adopted', 'rejected', 'invalidated')",
            name="ck_ai_previews_state",
        ),
        sa.CheckConstraint(
            "(state = 'ready' AND decided_at_utc_ms IS NULL) OR "
            "(state != 'ready' AND decided_at_utc_ms IS NOT NULL)",
            name="ck_ai_previews_decision_time",
        ),
    )
    op.create_index(
        "uq_ai_previews_operation_section",
        "ai_previews",
        ["operation_id", "section_code"],
        unique=True,
    )
    op.create_index(
        "ix_ai_previews_plan_state",
        "ai_previews",
        ["lesson_plan_id", "state"],
    )


def downgrade() -> None:
    op.drop_index("ix_ai_previews_plan_state", table_name="ai_previews")
    op.drop_index("uq_ai_previews_operation_section", table_name="ai_previews")
    op.drop_table("ai_previews")
    op.drop_table("prompt_overrides")
    op.drop_table("ai_configuration")
