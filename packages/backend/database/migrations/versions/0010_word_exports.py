"""建立 Word 导出冻结输入、状态与园所隔离约束。"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0010_word_exports"
down_revision: str | None = "0009_group_activity_sources"
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
        "daily_activity_plan_exports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("kindergarten_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plan_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plan_version", sa.Integer(), nullable=False),
        sa.Column("snapshot_id", postgresql.UUID(as_uuid=True)),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default=sa.text("'pending'")),
        sa.Column("display_filename", sa.String(255), nullable=False),
        sa.Column("storage_key", sa.String(255), nullable=False),
        sa.Column("context_snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("content_snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("content_schema_version", sa.SmallInteger(), nullable=False),
        sa.Column("content_sha256", sa.String(64), nullable=False),
        sa.Column("file_size", sa.BigInteger()),
        sa.Column("file_sha256", sa.String(64)),
        sa.Column("template_code", sa.String(80), nullable=False),
        sa.Column("template_filename", sa.String(255), nullable=False),
        sa.Column("template_sha256", sa.String(64), nullable=False),
        sa.Column("exported_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("exported_at", sa.DateTime(timezone=True)),
        sa.Column("error_code", sa.String(120)),
        sa.Column("error_summary", sa.String(1000)),
        sa.Column("file_missing_at", sa.DateTime(timezone=True)),
        *_timestamps(),
        sa.UniqueConstraint(
            "kindergarten_id",
            "id",
            name="uq_daily_activity_plan_exports_kg_id",
        ),
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
            ["kindergarten_id", "exported_by"],
            ["users.kindergarten_id", "users.id"],
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "plan_id", "snapshot_id"],
            [
                "daily_activity_plan_snapshots.kindergarten_id",
                "daily_activity_plan_snapshots.plan_id",
                "daily_activity_plan_snapshots.id",
            ],
        ),
        sa.CheckConstraint(
            "plan_version >= 1 AND content_schema_version >= 1",
            name="ck_daily_activity_plan_exports_versions",
        ),
        sa.CheckConstraint(
            "jsonb_typeof(context_snapshot)='object' AND context_snapshot <> '{}'::jsonb "
            "AND jsonb_typeof(content_snapshot)='object' AND content_snapshot <> '{}'::jsonb",
            name="ck_daily_activity_plan_exports_snapshots",
        ),
        sa.CheckConstraint(
            "content_sha256 ~ '^[0-9a-f]{64}$' "
            "AND template_sha256 ~ '^[0-9a-f]{64}$' "
            "AND (file_sha256 IS NULL OR file_sha256 ~ '^[0-9a-f]{64}$')",
            name="ck_daily_activity_plan_exports_hashes",
        ),
        sa.CheckConstraint(
            "status IN ('pending','succeeded','failed')",
            name="ck_daily_activity_plan_exports_status",
        ),
        sa.CheckConstraint(
            "storage_key !~ '[/\\\\]' AND storage_key <> ''",
            name="ck_daily_activity_plan_exports_storage_key",
        ),
        sa.CheckConstraint(
            """(
                status='pending' AND file_size IS NULL AND file_sha256 IS NULL
                AND exported_at IS NULL AND error_code IS NULL AND error_summary IS NULL
                AND file_missing_at IS NULL
            ) OR (
                status='succeeded' AND file_size >= 0 AND file_sha256 IS NOT NULL
                AND exported_at IS NOT NULL AND error_code IS NULL AND error_summary IS NULL
            ) OR (
                status='failed' AND file_size IS NULL AND file_sha256 IS NULL
                AND exported_at IS NULL AND error_code IS NOT NULL
                AND file_missing_at IS NULL
            )""",
            name="ck_daily_activity_plan_exports_outcome",
        ),
    )
    op.create_index(
        "uq_daily_activity_plan_exports_job_id",
        "daily_activity_plan_exports",
        ["kindergarten_id", "job_id"],
        unique=True,
    )
    op.create_index(
        "uq_daily_activity_plan_exports_storage_key",
        "daily_activity_plan_exports",
        ["kindergarten_id", "storage_key"],
        unique=True,
    )
    op.create_index(
        "ix_daily_activity_plan_exports_history",
        "daily_activity_plan_exports",
        ["kindergarten_id", "plan_id", sa.text("created_at DESC")],
    )
    op.create_index(
        "ix_daily_activity_plan_exports_actor_history",
        "daily_activity_plan_exports",
        ["kindergarten_id", "exported_by", sa.text("created_at DESC")],
    )
    op.execute(
        """
        CREATE FUNCTION enforce_daily_activity_plan_export_job_type()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM background_jobs AS job
                WHERE job.kindergarten_id=NEW.kindergarten_id
                  AND job.plan_id=NEW.plan_id
                  AND job.id=NEW.job_id
                  AND job.job_type='word.export'
            ) THEN
                RAISE EXCEPTION 'daily activity plan export requires a word.export job';
            END IF;
            RETURN NEW;
        END;
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER daily_activity_plan_export_job_type
        BEFORE INSERT OR UPDATE OF kindergarten_id,plan_id,job_id
        ON daily_activity_plan_exports
        FOR EACH ROW EXECUTE FUNCTION enforce_daily_activity_plan_export_job_type()
        """
    )
    op.execute(
        """
        CREATE FUNCTION reject_daily_activity_plan_export_input_mutation()
        RETURNS trigger
        LANGUAGE plpgsql
        AS $$
        BEGIN
            IF NEW.plan_id IS DISTINCT FROM OLD.plan_id
               OR NEW.plan_version IS DISTINCT FROM OLD.plan_version
               OR NEW.snapshot_id IS DISTINCT FROM OLD.snapshot_id
               OR NEW.job_id IS DISTINCT FROM OLD.job_id
               OR NEW.storage_key IS DISTINCT FROM OLD.storage_key
               OR NEW.context_snapshot IS DISTINCT FROM OLD.context_snapshot
               OR NEW.content_snapshot IS DISTINCT FROM OLD.content_snapshot
               OR NEW.content_schema_version IS DISTINCT FROM OLD.content_schema_version
               OR NEW.content_sha256 IS DISTINCT FROM OLD.content_sha256
               OR NEW.template_code IS DISTINCT FROM OLD.template_code
               OR NEW.template_filename IS DISTINCT FROM OLD.template_filename
               OR NEW.template_sha256 IS DISTINCT FROM OLD.template_sha256
               OR NEW.exported_by IS DISTINCT FROM OLD.exported_by THEN
                RAISE EXCEPTION 'daily activity plan export inputs are immutable';
            END IF;
            RETURN NEW;
        END;
        $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER daily_activity_plan_export_inputs_immutable
        BEFORE UPDATE ON daily_activity_plan_exports
        FOR EACH ROW EXECUTE FUNCTION reject_daily_activity_plan_export_input_mutation()
        """
    )


def downgrade() -> None:
    op.drop_table("daily_activity_plan_exports")
    op.execute("DROP FUNCTION reject_daily_activity_plan_export_input_mutation()")
    op.execute("DROP FUNCTION enforce_daily_activity_plan_export_job_type()")
