"""Slice 1 SQLite 表元数据；Schema 只由独立 Alembic 链创建。"""

from __future__ import annotations

import sqlalchemy as sa

metadata = sa.MetaData(
    naming_convention={
        "ix": "ix_%(table_name)s_%(column_0_name)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

app_profile = sa.Table(
    "app_profile",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("application_id", sa.Text, nullable=False),
    sa.Column("teacher_display_name", sa.Text, nullable=False),
    sa.Column("theme", sa.Text, nullable=False),
    sa.Column("last_daily_backup_date", sa.Text),
    sa.Column("created_at_utc_ms", sa.Integer, nullable=False),
    sa.Column("updated_at_utc_ms", sa.Integer, nullable=False),
    sa.CheckConstraint("id = 1", name="singleton"),
    sa.CheckConstraint(
        "application_id = 'cn.kindergartenmanager.desktop'",
        name="application_id",
    ),
    sa.CheckConstraint(
        "length(trim(teacher_display_name)) BETWEEN 1 AND 50",
        name="teacher_name",
    ),
    sa.CheckConstraint("theme IN ('system', 'light', 'dark')", name="theme"),
)

kindergarten_settings = sa.Table(
    "kindergarten_settings",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("name", sa.Text, nullable=False),
    sa.Column("timezone", sa.Text, nullable=False),
    sa.Column("created_at_utc_ms", sa.Integer, nullable=False),
    sa.Column("updated_at_utc_ms", sa.Integer, nullable=False),
    sa.CheckConstraint("id = 1", name="singleton"),
    sa.CheckConstraint("length(trim(name)) BETWEEN 1 AND 100", name="name"),
    sa.CheckConstraint("timezone = 'Asia/Shanghai'", name="timezone"),
)

class_groups = sa.Table(
    "class_groups",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("name", sa.Text, nullable=False),
    sa.Column("age_group", sa.Text, nullable=False),
    sa.Column("sort_order", sa.Integer, nullable=False),
    sa.Column("is_active", sa.Integer, nullable=False),
    sa.Column("created_at_utc_ms", sa.Integer, nullable=False),
    sa.Column("updated_at_utc_ms", sa.Integer, nullable=False),
    sa.CheckConstraint("length(trim(name)) BETWEEN 1 AND 50", name="name"),
    sa.CheckConstraint(
        "age_group IN ('nursery', 'small', 'middle', 'large', 'mixed')",
        name="age_group",
    ),
    sa.CheckConstraint("sort_order >= 0", name="sort_order"),
    sa.CheckConstraint("is_active IN (0, 1)", name="active"),
)
sa.Index(
    "uq_class_groups_name_nocase",
    class_groups.c.name.collate("NOCASE"),
    unique=True,
)

class_areas = sa.Table(
    "class_areas",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("class_id", sa.Integer, nullable=False),
    sa.Column("area_type", sa.Text, nullable=False),
    sa.Column("name", sa.Text, nullable=False),
    sa.Column("sort_order", sa.Integer, nullable=False),
    sa.Column("created_at_utc_ms", sa.Integer, nullable=False),
    sa.Column("updated_at_utc_ms", sa.Integer, nullable=False),
    sa.ForeignKeyConstraint(
        ["class_id"],
        ["class_groups.id"],
        name="fk_class_areas_class_id_class_groups",
        ondelete="CASCADE",
    ),
    sa.CheckConstraint("area_type IN ('indoor', 'outdoor')", name="area_type"),
    sa.CheckConstraint("length(trim(name)) BETWEEN 1 AND 50", name="name"),
    sa.CheckConstraint("sort_order >= 0", name="sort_order"),
)
sa.Index(
    "uq_class_areas_class_type_name_nocase",
    class_areas.c.class_id,
    class_areas.c.area_type,
    class_areas.c.name.collate("NOCASE"),
    unique=True,
)

semesters = sa.Table(
    "semesters",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("name", sa.Text, nullable=False),
    sa.Column("start_date", sa.Text, nullable=False),
    sa.Column("end_date", sa.Text, nullable=False),
    sa.Column("is_current", sa.Integer, nullable=False),
    sa.Column("created_at_utc_ms", sa.Integer, nullable=False),
    sa.Column("updated_at_utc_ms", sa.Integer, nullable=False),
    sa.CheckConstraint("length(trim(name)) BETWEEN 1 AND 100", name="name"),
    sa.CheckConstraint("end_date >= start_date", name="date_range"),
    sa.CheckConstraint("is_current IN (0, 1)", name="current"),
)
sa.Index(
    "uq_semesters_one_current",
    semesters.c.is_current,
    unique=True,
    sqlite_where=semesters.c.is_current == 1,
)

lesson_plans = sa.Table(
    "lesson_plans",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("class_id", sa.Integer, nullable=False),
    sa.Column("semester_id", sa.Integer, nullable=False),
    sa.Column("plan_date", sa.Text, nullable=False),
    sa.Column("author_name", sa.Text, nullable=False),
    sa.Column("content_schema_version", sa.Integer, nullable=False),
    sa.Column("content_json", sa.Text, nullable=False),
    sa.Column("content_revision", sa.Integer, nullable=False),
    sa.Column("archived_at_utc_ms", sa.Integer),
    sa.Column("created_at_utc_ms", sa.Integer, nullable=False),
    sa.Column("updated_at_utc_ms", sa.Integer, nullable=False),
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
    sa.CheckConstraint("length(trim(author_name)) BETWEEN 1 AND 50", name="author_name"),
    sa.CheckConstraint("content_schema_version = 1", name="schema_version"),
    sa.CheckConstraint("content_revision >= 1", name="revision"),
)
sa.Index(
    "uq_lesson_plans_class_date",
    lesson_plans.c.class_id,
    lesson_plans.c.plan_date,
    unique=True,
)

lesson_plan_versions = sa.Table(
    "lesson_plan_versions",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("lesson_plan_id", sa.Integer, nullable=False),
    sa.Column("reason", sa.Text, nullable=False),
    sa.Column("description", sa.Text),
    sa.Column("author_name", sa.Text, nullable=False),
    sa.Column("content_schema_version", sa.Integer, nullable=False),
    sa.Column("content_json", sa.Text, nullable=False),
    sa.Column("source_revision", sa.Integer, nullable=False),
    sa.Column("created_at_utc_ms", sa.Integer, nullable=False),
    sa.ForeignKeyConstraint(
        ["lesson_plan_id"],
        ["lesson_plans.id"],
        name="fk_lesson_plan_versions_plan_id_lesson_plans",
        ondelete="CASCADE",
    ),
    sa.CheckConstraint(
        "reason IN ('explicit_save', 'pre_ai_adopt', 'pre_history_restore', "
        "'pre_archive', 'pre_unarchive')",
        name="reason",
    ),
    sa.CheckConstraint(
        "description IS NULL OR length(trim(description)) <= 200",
        name="description",
    ),
    sa.CheckConstraint("content_schema_version = 1", name="schema_version"),
    sa.CheckConstraint("source_revision >= 1", name="revision"),
)

calendar_overrides = sa.Table(
    "calendar_overrides",
    metadata,
    sa.Column("override_date", sa.Text, primary_key=True),
    sa.Column("status", sa.Text, nullable=False),
    sa.Column("note", sa.Text),
    sa.Column("created_at_utc_ms", sa.Integer, nullable=False),
    sa.Column("updated_at_utc_ms", sa.Integer, nullable=False),
    sa.CheckConstraint("status IN ('workday', 'non_workday')", name="status"),
    sa.CheckConstraint("note IS NULL OR length(trim(note)) <= 200", name="note"),
)
