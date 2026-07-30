"""建立集体活动来源元数据与同园隔离约束。"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0009_group_activity_sources"
down_revision: str | None = "0008_ai_generation_results"
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
        "lesson_plan_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("kindergarten_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_type", sa.String(16), nullable=False),
        sa.Column("original_filename", sa.String(255)),
        sa.Column("source_sha256", sa.String(64), nullable=False),
        sa.Column("extracted_character_count", sa.Integer(), nullable=False),
        sa.Column("extracted_text", sa.Text(), nullable=False),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), nullable=False),
        *_timestamps(),
        sa.UniqueConstraint("kindergarten_id", "id", name="uq_lesson_plan_sources_kg_id"),
        sa.ForeignKeyConstraint(["kindergarten_id"], ["kindergartens.id"]),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "plan_id"],
            ["daily_activity_plans.kindergarten_id", "daily_activity_plans.id"],
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "uploaded_by"], ["users.kindergarten_id", "users.id"]
        ),
        sa.CheckConstraint(
            "source_type IN ('pasted_text','docx')",
            name="ck_lesson_plan_sources_type",
        ),
        sa.CheckConstraint(
            "extracted_character_count BETWEEN 1 AND 200000",
            name="ck_lesson_plan_sources_character_count",
        ),
        sa.CheckConstraint(
            "source_sha256 ~ '^[0-9a-f]{64}$'",
            name="ck_lesson_plan_sources_sha256",
        ),
        sa.CheckConstraint(
            "char_length(extracted_text) = extracted_character_count",
            name="ck_lesson_plan_sources_text_length",
        ),
    )
    op.create_index(
        "ix_lesson_plan_sources_history",
        "lesson_plan_sources",
        ["kindergarten_id", "plan_id", sa.text("created_at DESC")],
    )


def downgrade() -> None:
    op.drop_table("lesson_plan_sources")
