"""一日活动计划 SQLAlchemy 模型。"""

from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    SmallInteger,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.backend.database.base import Base


class Timestamped:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class DailyActivityPlan(Timestamped, Base):
    __tablename__ = "daily_activity_plans"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    kindergarten_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    class_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    semester_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    plan_date: Mapped[date] = mapped_column(Date, nullable=False)
    kindergarten_name_snapshot: Mapped[str] = mapped_column(String(200), nullable=False)
    class_name_snapshot: Mapped[str] = mapped_column(String(120), nullable=False)
    age_group_name_snapshot: Mapped[str] = mapped_column(String(120), nullable=False)
    semester_name_snapshot: Mapped[str] = mapped_column(String(160), nullable=False)
    semester_start_date_snapshot: Mapped[date] = mapped_column(Date, nullable=False)
    semester_end_date_snapshot: Mapped[date] = mapped_column(Date, nullable=False)
    teaching_week_number: Mapped[int | None] = mapped_column(Integer)
    teaching_week_text: Mapped[str | None] = mapped_column(String(40))
    activity_date_text: Mapped[str] = mapped_column(String(40), nullable=False)
    season_code: Mapped[str] = mapped_column(String(16), nullable=False)
    content: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    content_schema_version: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    archived_by: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    created_by: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    updated_by: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)

    __table_args__ = (
        UniqueConstraint("kindergarten_id", "id", name="uq_daily_activity_plans_kg_id"),
        UniqueConstraint(
            "kindergarten_id",
            "class_id",
            "plan_date",
            name="uq_daily_activity_plans_kg_class_date",
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "class_id"], ["classes.kindergarten_id", "classes.id"]
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "semester_id"], ["semesters.kindergarten_id", "semesters.id"]
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "created_by"], ["users.kindergarten_id", "users.id"]
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "updated_by"], ["users.kindergarten_id", "users.id"]
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "archived_by"], ["users.kindergarten_id", "users.id"]
        ),
        CheckConstraint(
            """(
                plan_date BETWEEN semester_start_date_snapshot AND semester_end_date_snapshot
                AND teaching_week_number IS NOT NULL
                AND teaching_week_number > 0
                AND teaching_week_text IS NOT NULL
            ) OR (
                plan_date NOT BETWEEN semester_start_date_snapshot AND semester_end_date_snapshot
                AND teaching_week_number IS NULL
                AND teaching_week_text IS NULL
            )""",
            name="ck_daily_activity_plans_week_context",
        ),
        CheckConstraint("content_schema_version >= 1", name="ck_daily_activity_plans_schema"),
        CheckConstraint("version >= 1", name="ck_daily_activity_plans_version"),
        CheckConstraint(
            "season_code IN ('spring','summer','autumn','winter')",
            name="ck_daily_activity_plans_season",
        ),
        Index("ix_daily_activity_plans_list", "kindergarten_id", "plan_date", "class_id"),
    )


class DailyActivityPlanAuthor(Timestamped, Base):
    __tablename__ = "daily_activity_plan_authors"

    kindergarten_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    plan_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    display_name_snapshot: Mapped[str] = mapped_column(String(120), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    added_by: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["kindergarten_id", "plan_id"],
            ["daily_activity_plans.kindergarten_id", "daily_activity_plans.id"],
        ),
        ForeignKeyConstraint(["kindergarten_id", "user_id"], ["users.kindergarten_id", "users.id"]),
        ForeignKeyConstraint(
            ["kindergarten_id", "added_by"], ["users.kindergarten_id", "users.id"]
        ),
        UniqueConstraint(
            "kindergarten_id",
            "plan_id",
            "sort_order",
            name="uq_daily_activity_plan_authors_order",
        ),
        CheckConstraint("sort_order >= 0", name="ck_daily_activity_plan_authors_order"),
    )


class DailyActivityPlanSnapshot(Timestamped, Base):
    __tablename__ = "daily_activity_plan_snapshots"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    kindergarten_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    plan_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    plan_version: Mapped[int] = mapped_column(Integer, nullable=False)
    reason_code: Mapped[str] = mapped_column(String(24), nullable=False)
    context_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    content: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    content_schema_version: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    content_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_by: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))

    __table_args__ = (
        UniqueConstraint(
            "kindergarten_id", "plan_id", "id", name="uq_daily_activity_plan_snapshots_plan_id"
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "plan_id"],
            ["daily_activity_plans.kindergarten_id", "daily_activity_plans.id"],
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "created_by"], ["users.kindergarten_id", "users.id"]
        ),
        CheckConstraint("plan_version >= 1", name="ck_daily_activity_plan_snapshots_version"),
        CheckConstraint(
            """reason_code IN
            ('manual_save','ai_adopted','archive','unarchive','before_restore','restored')""",
            name="ck_daily_activity_plan_snapshots_reason",
        ),
        CheckConstraint(
            "content_sha256 ~ '^[0-9a-f]{64}$'",
            name="ck_daily_activity_plan_snapshots_sha256",
        ),
        Index(
            "ix_daily_activity_plan_snapshots_history",
            "kindergarten_id",
            "plan_id",
            "created_at",
        ),
    )


class WorkdayCache(Timestamped, Base):
    __tablename__ = "workday_cache"

    kindergarten_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("kindergartens.id"), primary_key=True
    )
    calendar_date: Mapped[date] = mapped_column(Date, primary_key=True)
    result_code: Mapped[str] = mapped_column(String(16), nullable=False)
    source_code: Mapped[str] = mapped_column(String(16), nullable=False)
    source_version: Mapped[str] = mapped_column(String(80), nullable=False)
    detail: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        CheckConstraint(
            "result_code IN ('workday','non_workday','unknown')",
            name="ck_workday_cache_result",
        ),
        CheckConstraint(
            "source_code IN ('local','online','combined','unavailable')",
            name="ck_workday_cache_source",
        ),
        CheckConstraint(
            "(source_code <> 'unavailable') OR result_code = 'unknown'",
            name="ck_workday_cache_unavailable",
        ),
        CheckConstraint("expires_at > checked_at", name="ck_workday_cache_expiry"),
        Index("ix_workday_cache_expiry", "kindergarten_id", "expires_at"),
    )
