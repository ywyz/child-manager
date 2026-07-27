"""通用后台任务 ORM 模型。"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.backend.database.base import Base


class BackgroundJob(Base):
    __tablename__ = "background_jobs"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    kindergarten_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    parent_job_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    retry_of_job_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    job_type: Mapped[str] = mapped_column(String(64), nullable=False)
    execution_status: Mapped[str | None] = mapped_column(String(32))
    plan_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    target_section: Mapped[str | None] = mapped_column(String(64))
    requested_resource_version: Mapped[int | None] = mapped_column(Integer)
    idempotency_scope: Mapped[str | None] = mapped_column(String(300))
    idempotency_key: Mapped[str | None] = mapped_column(String(200))
    request_fingerprint_sha256: Mapped[str | None] = mapped_column(String(64))
    attempt_count: Mapped[int | None] = mapped_column(Integer)
    max_attempts: Mapped[int | None] = mapped_column(Integer)
    requested_by: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    request_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    trace_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    lease_owner: Mapped[str | None] = mapped_column(String(160))
    lease_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    queued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    error_code: Mapped[str | None] = mapped_column(String(64))
    error_summary: Mapped[str | None] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
