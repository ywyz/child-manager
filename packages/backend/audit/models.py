"""不可变、最小化身份审计 ORM 模型。"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.backend.database.base import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    kindergarten_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("kindergartens.id"), nullable=False
    )
    event_code: Mapped[str] = mapped_column(String(120))
    actor_user_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    actor_role_codes: Mapped[list[str]] = mapped_column(JSONB)
    resource_type: Mapped[str] = mapped_column(String(80))
    resource_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    request_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    trace_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    job_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    outcome: Mapped[str] = mapped_column(String(16))
    metadata_json: Mapped[dict[str, object]] = mapped_column("metadata", JSONB, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("kindergarten_id", "id", name="uq_audit_events_kindergarten_id_id"),
        ForeignKeyConstraint(
            ["kindergarten_id", "actor_user_id"], ["users.kindergarten_id", "users.id"]
        ),
        CheckConstraint(
            "jsonb_typeof(actor_role_codes) = 'array'", name="ck_audit_actor_roles_array"
        ),
        CheckConstraint("jsonb_typeof(metadata) = 'object'", name="ck_audit_metadata_object"),
        CheckConstraint("outcome IN ('success', 'failure')", name="ck_audit_outcome"),
        CheckConstraint("updated_at = created_at", name="ck_audit_immutable_timestamps"),
        Index("ix_audit_occurred", "kindergarten_id", occurred_at.desc()),
        Index("ix_audit_event_occurred", "kindergarten_id", "event_code", occurred_at.desc()),
        Index(
            "ix_audit_resource_occurred",
            "kindergarten_id",
            "resource_type",
            "resource_id",
            occurred_at.desc(),
        ),
        Index("ix_audit_actor_occurred", "kindergarten_id", "actor_user_id", occurred_at.desc()),
    )
