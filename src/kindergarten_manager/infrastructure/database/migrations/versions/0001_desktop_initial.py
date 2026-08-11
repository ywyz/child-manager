"""创建桌面 Slice 1 基础表。"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0001_desktop_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "app_profile",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("application_id", sa.Text(), nullable=False),
        sa.Column("teacher_display_name", sa.Text(), nullable=False),
        sa.Column("theme", sa.Text(), nullable=False),
        sa.Column("last_daily_backup_date", sa.Text()),
        sa.Column("created_at_utc_ms", sa.Integer(), nullable=False),
        sa.Column("updated_at_utc_ms", sa.Integer(), nullable=False),
        sa.CheckConstraint("id = 1", name="ck_app_profile_singleton"),
        sa.CheckConstraint(
            "application_id = 'cn.kindergartenmanager.desktop'",
            name="ck_app_profile_application_id",
        ),
        sa.CheckConstraint(
            "length(trim(teacher_display_name)) BETWEEN 1 AND 50",
            name="ck_app_profile_teacher_name",
        ),
        sa.CheckConstraint("theme IN ('system', 'light', 'dark')", name="ck_app_profile_theme"),
    )
    op.create_table(
        "kindergarten_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("timezone", sa.Text(), nullable=False),
        sa.Column("created_at_utc_ms", sa.Integer(), nullable=False),
        sa.Column("updated_at_utc_ms", sa.Integer(), nullable=False),
        sa.CheckConstraint("id = 1", name="ck_kindergarten_settings_singleton"),
        sa.CheckConstraint(
            "length(trim(name)) BETWEEN 1 AND 100",
            name="ck_kindergarten_settings_name",
        ),
        sa.CheckConstraint(
            "timezone = 'Asia/Shanghai'",
            name="ck_kindergarten_settings_timezone",
        ),
    )
    op.create_table(
        "class_groups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("age_group", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Integer(), nullable=False),
        sa.Column("created_at_utc_ms", sa.Integer(), nullable=False),
        sa.Column("updated_at_utc_ms", sa.Integer(), nullable=False),
        sa.CheckConstraint("length(trim(name)) BETWEEN 1 AND 50", name="ck_class_groups_name"),
        sa.CheckConstraint(
            "age_group IN ('nursery', 'small', 'middle', 'large', 'mixed')",
            name="ck_class_groups_age_group",
        ),
        sa.CheckConstraint("sort_order >= 0", name="ck_class_groups_sort_order"),
        sa.CheckConstraint("is_active IN (0, 1)", name="ck_class_groups_active"),
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_class_groups_name_nocase ON class_groups(name COLLATE NOCASE)"
    )
    op.create_table(
        "class_areas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("class_id", sa.Integer(), nullable=False),
        sa.Column("area_type", sa.Text(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at_utc_ms", sa.Integer(), nullable=False),
        sa.Column("updated_at_utc_ms", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["class_id"],
            ["class_groups.id"],
            name="fk_class_areas_class_id_class_groups",
            ondelete="CASCADE",
        ),
        sa.CheckConstraint("area_type IN ('indoor', 'outdoor')", name="ck_class_areas_area_type"),
        sa.CheckConstraint("length(trim(name)) BETWEEN 1 AND 50", name="ck_class_areas_name"),
        sa.CheckConstraint("sort_order >= 0", name="ck_class_areas_sort_order"),
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_class_areas_class_type_name_nocase "
        "ON class_areas(class_id, area_type, name COLLATE NOCASE)"
    )
    op.create_table(
        "semesters",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("start_date", sa.Text(), nullable=False),
        sa.Column("end_date", sa.Text(), nullable=False),
        sa.Column("is_current", sa.Integer(), nullable=False),
        sa.Column("created_at_utc_ms", sa.Integer(), nullable=False),
        sa.Column("updated_at_utc_ms", sa.Integer(), nullable=False),
        sa.CheckConstraint("length(trim(name)) BETWEEN 1 AND 100", name="ck_semesters_name"),
        sa.CheckConstraint("end_date >= start_date", name="ck_semesters_date_range"),
        sa.CheckConstraint("is_current IN (0, 1)", name="ck_semesters_current"),
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_semesters_one_current ON semesters(is_current) WHERE is_current = 1"
    )
    op.create_table(
        "lesson_plans",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("class_id", sa.Integer(), nullable=False),
        sa.Column("semester_id", sa.Integer(), nullable=False),
        sa.Column("plan_date", sa.Text(), nullable=False),
        sa.Column("author_name", sa.Text(), nullable=False),
        sa.Column("content_schema_version", sa.Integer(), nullable=False),
        sa.Column("content_json", sa.Text(), nullable=False),
        sa.Column("content_revision", sa.Integer(), nullable=False),
        sa.Column("archived_at_utc_ms", sa.Integer()),
        sa.Column("created_at_utc_ms", sa.Integer(), nullable=False),
        sa.Column("updated_at_utc_ms", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["class_id"],
            ["class_groups.id"],
            name="fk_lesson_plans_class_id_class_groups",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["semester_id"],
            ["semesters.id"],
            name="fk_lesson_plans_semester_id_semesters",
            ondelete="RESTRICT",
        ),
        sa.CheckConstraint(
            "length(trim(author_name)) BETWEEN 1 AND 50",
            name="ck_lesson_plans_author_name",
        ),
        sa.CheckConstraint("content_schema_version = 1", name="ck_lesson_plans_schema_version"),
        sa.CheckConstraint("content_revision >= 1", name="ck_lesson_plans_revision"),
    )
    op.execute(
        "CREATE UNIQUE INDEX uq_lesson_plans_class_date ON lesson_plans(class_id, plan_date)"
    )
    op.create_table(
        "lesson_plan_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lesson_plan_id", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("author_name", sa.Text(), nullable=False),
        sa.Column("content_schema_version", sa.Integer(), nullable=False),
        sa.Column("content_json", sa.Text(), nullable=False),
        sa.Column("source_revision", sa.Integer(), nullable=False),
        sa.Column("created_at_utc_ms", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["lesson_plan_id"],
            ["lesson_plans.id"],
            name="fk_lesson_plan_versions_plan_id_lesson_plans",
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "reason IN ('explicit_save', 'pre_ai_adopt', 'pre_history_restore', "
            "'pre_archive', 'pre_unarchive')",
            name="ck_lesson_plan_versions_reason",
        ),
        sa.CheckConstraint(
            "description IS NULL OR length(trim(description)) <= 200",
            name="ck_lesson_plan_versions_description",
        ),
        sa.CheckConstraint(
            "content_schema_version = 1",
            name="ck_lesson_plan_versions_schema_version",
        ),
        sa.CheckConstraint("source_revision >= 1", name="ck_lesson_plan_versions_revision"),
    )
    op.execute(
        "CREATE TRIGGER trg_lesson_plan_versions_immutable_update "
        "BEFORE UPDATE ON lesson_plan_versions BEGIN "
        "SELECT RAISE(ABORT, 'lesson plan versions are immutable'); END"
    )
    op.execute(
        "CREATE TRIGGER trg_lesson_plan_versions_immutable_delete "
        "BEFORE DELETE ON lesson_plan_versions BEGIN "
        "SELECT RAISE(ABORT, 'lesson plan versions are immutable'); END"
    )
    op.create_table(
        "calendar_overrides",
        sa.Column("override_date", sa.Text(), primary_key=True),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("note", sa.Text()),
        sa.Column("created_at_utc_ms", sa.Integer(), nullable=False),
        sa.Column("updated_at_utc_ms", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "status IN ('workday', 'non_workday')",
            name="ck_calendar_overrides_status",
        ),
        sa.CheckConstraint(
            "note IS NULL OR length(trim(note)) <= 200",
            name="ck_calendar_overrides_note",
        ),
    )


def downgrade() -> None:
    op.drop_table("calendar_overrides")
    op.execute("DROP TRIGGER trg_lesson_plan_versions_immutable_delete")
    op.execute("DROP TRIGGER trg_lesson_plan_versions_immutable_update")
    op.drop_table("lesson_plan_versions")
    op.drop_index("uq_lesson_plans_class_date", table_name="lesson_plans")
    op.drop_table("lesson_plans")
    op.drop_index("uq_semesters_one_current", table_name="semesters")
    op.drop_table("semesters")
    op.drop_index("uq_class_areas_class_type_name_nocase", table_name="class_areas")
    op.drop_table("class_areas")
    op.drop_index("uq_class_groups_name_nocase", table_name="class_groups")
    op.drop_table("class_groups")
    op.drop_table("kindergarten_settings")
    op.drop_table("app_profile")
