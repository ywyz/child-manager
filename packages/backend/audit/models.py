"""审计事件 ORM 模型。

本模型与 docs/design/database-schema.md §6 冻结 Schema 保持一致。
"""

from datetime import UTC, datetime
from uuid import uuid7

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
    # 冻结 Schema §3.2 要求主键使用 UUIDv7。
    return str(uuid7())


class AuditEvent(Base):
    __tablename__ = "audit_events"
    __table_args__ = (
        UniqueConstraint("kindergarten_id", "id", name="uq_audit_events_kindergarten_id"),
        ForeignKeyConstraint(
            ["kindergarten_id"],
            ["kindergartens.id"],
            name="fk_audit_events_kindergarten",
        ),
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
            "ix_audit_events_kindergarten_occurred",
            "kindergarten_id",
            "occurred_at",
            postgresql_ops={"occurred_at": "DESC"},
        ),
        Index(
            "ix_audit_events_kindergarten_event_code_occurred",
            "kindergarten_id",
            "event_code",
            "occurred_at",
            postgresql_ops={"occurred_at": "DESC"},
        ),
        Index(
            "ix_audit_events_kindergarten_resource_occurred",
            "kindergarten_id",
            "resource_type",
            "resource_id",
            "occurred_at",
            postgresql_ops={"occurred_at": "DESC"},
        ),
        Index(
            "ix_audit_events_kindergarten_actor_occurred",
            "kindergarten_id",
            "actor_user_id",
            "occurred_at",
            postgresql_ops={"occurred_at": "DESC"},
        ),
    )

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=_uuid)
    kindergarten_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), nullable=False)
    event_code: Mapped[str] = mapped_column(String(120), nullable=False)
    actor_user_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), nullable=True)
    actor_role_codes: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    resource_type: Mapped[str] = mapped_column(String(80), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    trace_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    job_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
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
