"""Word 导出 SQLAlchemy 模型。"""

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    Integer,
    SmallInteger,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.backend.database.base import Base


class DailyActivityPlanExport(Base):
    __tablename__ = "daily_activity_plan_exports"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    kindergarten_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    plan_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    plan_version: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    job_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    display_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_key: Mapped[str] = mapped_column(String(255), nullable=False)
    context_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    content_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    content_schema_version: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    content_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    file_size: Mapped[int | None] = mapped_column(BigInteger)
    file_sha256: Mapped[str | None] = mapped_column(String(64))
    template_code: Mapped[str] = mapped_column(String(80), nullable=False)
    template_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    template_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    exported_by: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    exported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_code: Mapped[str | None] = mapped_column(String(120))
    error_summary: Mapped[str | None] = mapped_column(String(1000))
    file_missing_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("kindergarten_id", "id", name="uq_daily_activity_plan_exports_kg_id"),
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
            ["kindergarten_id", "exported_by"], ["users.kindergarten_id", "users.id"]
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "plan_id", "snapshot_id"],
            [
                "daily_activity_plan_snapshots.kindergarten_id",
                "daily_activity_plan_snapshots.plan_id",
                "daily_activity_plan_snapshots.id",
            ],
        ),
        CheckConstraint("plan_version >= 1 AND content_schema_version >= 1"),
        CheckConstraint(
            "jsonb_typeof(context_snapshot)='object' AND context_snapshot <> '{}'::jsonb "
            "AND jsonb_typeof(content_snapshot)='object' AND content_snapshot <> '{}'::jsonb"
        ),
        CheckConstraint("status IN ('pending','succeeded','failed')"),
        Index(
            "uq_daily_activity_plan_exports_job_id",
            "kindergarten_id",
            "job_id",
            unique=True,
        ),
        Index(
            "uq_daily_activity_plan_exports_storage_key",
            "kindergarten_id",
            "storage_key",
            unique=True,
        ),
        Index(
            "ix_daily_activity_plan_exports_history",
            "kindergarten_id",
            "plan_id",
            text("created_at DESC"),
        ),
    )
