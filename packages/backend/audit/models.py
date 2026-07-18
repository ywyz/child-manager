"""审计事件 ORM 模型。

本模型与 docs/design/database-schema.md §6 冻结 Schema 保持一致。
"""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from packages.backend.database.base import Base


def _now() -> datetime:
    return datetime.now(UTC)


def _uuid() -> str:
    return str(uuid4())


class AuditEvent(Base):
    __tablename__ = "audit_events"
    __table_args__ = (
        UniqueConstraint("kindergarten_id", "id", name="uq_audit_events_kindergarten_id"),
        ForeignKeyConstraint(
            ["kindergarten_id", "actor_user_id"],
            ["users.kindergarten_id", "users.id"],
            name="fk_audit_events_actor_user",
        ),
        CheckConstraint(
            "jsonb_typeof(actor_role_codes) = 'array'",
            name="ck_audit_events_actor_role_codes_array",
        ),
        CheckConstraint(
            "jsonb_typeof(metadata) = 'object'",
            name="ck_audit_events_metadata_object",
        ),
        CheckConstraint(
            "outcome IN ('success', 'failure')",
            name="ck_audit_events_outcome",
        ),
        CheckConstraint(
            "updated_at = created_at",
            name="ck_audit_events_immutable",
        ),
        Index(
            "ix_audit_events_lookup",
            "kindergarten_id",
            "event_code",
            "resource_type",
            "resource_id",
        ),
        Index(
            "ix_audit_events_occurred",
            "occurred_at",
        ),
    )

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=_uuid)
    kindergarten_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), nullable=False)
    event_code: Mapped[str] = mapped_column(String(120), nullable=False)
    actor_user_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), nullable=True)
    actor_role_codes: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    resource_type: Mapped[str] = mapped_column(String(80), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), nullable=True)
    request_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), nullable=True)
    trace_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), nullable=True)
    job_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), nullable=True)
    outcome: Mapped[str] = mapped_column(String(16), nullable=False)
    event_metadata: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
