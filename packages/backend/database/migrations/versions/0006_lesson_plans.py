"""建立无 AI 教案手工闭环 Schema。"""

from collections.abc import Sequence
from typing import Any

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006_lesson_plans"
down_revision: str | None = "0005_password_totp_backup_login"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


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
        "daily_activity_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("kindergarten_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("class_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("semester_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plan_date", sa.Date(), nullable=False),
        sa.Column("kindergarten_name_snapshot", sa.String(200), nullable=False),
        sa.Column("class_name_snapshot", sa.String(120), nullable=False),
        sa.Column("age_group_name_snapshot", sa.String(120), nullable=False),
        sa.Column("semester_name_snapshot", sa.String(160), nullable=False),
        sa.Column("semester_start_date_snapshot", sa.Date(), nullable=False),
        sa.Column("semester_end_date_snapshot", sa.Date(), nullable=False),
        sa.Column("teaching_week_number", sa.Integer()),
        sa.Column("teaching_week_text", sa.String(40)),
        sa.Column("activity_date_text", sa.String(40), nullable=False),
        sa.Column("season_code", sa.String(16), nullable=False),
        sa.Column("content", postgresql.JSONB(), nullable=False),
        sa.Column(
            "content_schema_version", sa.SmallInteger(), nullable=False, server_default=sa.text("1")
        ),
        sa.Column("version", sa.Integer(), nullable=False, server_default=sa.text("1")),
        sa.Column("archived_at", sa.DateTime(timezone=True)),
        sa.Column("archived_by", postgresql.UUID(as_uuid=True)),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=False),
        *_timestamps(),
        sa.UniqueConstraint("kindergarten_id", "id", name="uq_daily_activity_plans_kg_id"),
        sa.UniqueConstraint(
            "kindergarten_id",
            "class_id",
            "plan_date",
            name="uq_daily_activity_plans_kg_class_date",
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "class_id"], ["classes.kindergarten_id", "classes.id"]
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "semester_id"], ["semesters.kindergarten_id", "semesters.id"]
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "created_by"], ["users.kindergarten_id", "users.id"]
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "updated_by"], ["users.kindergarten_id", "users.id"]
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "archived_by"], ["users.kindergarten_id", "users.id"]
        ),
        sa.CheckConstraint(
            """(
                plan_date BETWEEN semester_start_date_snapshot AND semester_end_date_snapshot
                AND teaching_week_number IS NOT NULL AND teaching_week_number > 0
                AND teaching_week_text IS NOT NULL
            ) OR (
                plan_date NOT BETWEEN semester_start_date_snapshot AND semester_end_date_snapshot
                AND teaching_week_number IS NULL AND teaching_week_text IS NULL
            )""",
            name="ck_daily_activity_plans_week_context",
        ),
        sa.CheckConstraint("content_schema_version >= 1", name="ck_daily_activity_plans_schema"),
        sa.CheckConstraint("version >= 1", name="ck_daily_activity_plans_version"),
        sa.CheckConstraint(
            "season_code IN ('spring','summer','autumn','winter')",
            name="ck_daily_activity_plans_season",
        ),
    )
    op.create_index(
        "ix_daily_activity_plans_list",
        "daily_activity_plans",
        ["kindergarten_id", "plan_date", "class_id"],
    )

    op.create_table(
        "daily_activity_plan_authors",
        sa.Column("kindergarten_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("display_name_snapshot", sa.String(120), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("added_by", postgresql.UUID(as_uuid=True), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "plan_id"],
            ["daily_activity_plans.kindergarten_id", "daily_activity_plans.id"],
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "user_id"], ["users.kindergarten_id", "users.id"]
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "added_by"], ["users.kindergarten_id", "users.id"]
        ),
        sa.UniqueConstraint(
            "kindergarten_id",
            "plan_id",
            "sort_order",
            name="uq_daily_activity_plan_authors_order",
        ),
        sa.CheckConstraint("sort_order >= 0", name="ck_daily_activity_plan_authors_order"),
    )

    op.create_table(
        "daily_activity_plan_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("kindergarten_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plan_version", sa.Integer(), nullable=False),
        sa.Column("reason_code", sa.String(24), nullable=False),
        sa.Column("context_snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("content", postgresql.JSONB(), nullable=False),
        sa.Column("content_schema_version", sa.SmallInteger(), nullable=False),
        sa.Column("content_sha256", sa.String(64), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
        *_timestamps(),
        sa.UniqueConstraint(
            "kindergarten_id",
            "plan_id",
            "id",
            name="uq_daily_activity_plan_snapshots_plan_id",
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "plan_id"],
            ["daily_activity_plans.kindergarten_id", "daily_activity_plans.id"],
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "created_by"], ["users.kindergarten_id", "users.id"]
        ),
        sa.CheckConstraint("plan_version >= 1", name="ck_daily_activity_plan_snapshots_version"),
        sa.CheckConstraint(
            """reason_code IN
            ('manual_save','ai_adopted','archive','unarchive','before_restore','restored')""",
            name="ck_daily_activity_plan_snapshots_reason",
        ),
        sa.CheckConstraint(
            "content_sha256 ~ '^[0-9a-f]{64}$'",
            name="ck_daily_activity_plan_snapshots_sha256",
        ),
    )
    op.create_index(
        "ix_daily_activity_plan_snapshots_history",
        "daily_activity_plan_snapshots",
        ["kindergarten_id", "plan_id", "created_at"],
    )
    op.execute(
        """
        CREATE FUNCTION reject_daily_activity_plan_snapshot_mutation()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            RAISE EXCEPTION 'daily activity plan snapshots are immutable';
        END;
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER daily_activity_plan_snapshots_immutable
        BEFORE UPDATE OR DELETE ON daily_activity_plan_snapshots
        FOR EACH ROW EXECUTE FUNCTION reject_daily_activity_plan_snapshot_mutation()
        """
    )

    op.create_table(
        "workday_cache",
        sa.Column(
            "kindergarten_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("kindergartens.id"),
            primary_key=True,
        ),
        sa.Column("calendar_date", sa.Date(), primary_key=True),
        sa.Column("result_code", sa.String(16), nullable=False),
        sa.Column("source_code", sa.String(16), nullable=False),
        sa.Column("source_version", sa.String(80), nullable=False),
        sa.Column("detail", postgresql.JSONB(), nullable=False),
        sa.Column("checked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        *_timestamps(),
        sa.CheckConstraint(
            "result_code IN ('workday','non_workday','unknown')",
            name="ck_workday_cache_result",
        ),
        sa.CheckConstraint(
            "source_code IN ('local','online','combined','unavailable')",
            name="ck_workday_cache_source",
        ),
        sa.CheckConstraint(
            "(source_code <> 'unavailable') OR result_code = 'unknown'",
            name="ck_workday_cache_unavailable",
        ),
        sa.CheckConstraint("expires_at > checked_at", name="ck_workday_cache_expiry"),
    )
    op.create_index("ix_workday_cache_expiry", "workday_cache", ["kindergarten_id", "expires_at"])


def downgrade() -> None:
    op.drop_table("workday_cache")
    op.drop_table("daily_activity_plan_snapshots")
    op.execute("DROP FUNCTION reject_daily_activity_plan_snapshot_mutation()")
    op.drop_table("daily_activity_plan_authors")
    op.drop_table("daily_activity_plans")
