"""提示词定义、版本与冻结测试运行 ORM 模型。"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKeyConstraint, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.backend.database.base import Base


class PromptDefinition(Base):
    __tablename__ = "prompt_definitions"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    kindergarten_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    code: Mapped[str] = mapped_column(String(160), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    variable_whitelist: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    required_capabilities: Mapped[list[str]] = mapped_column(JSONB, nullable=False)
    result_schema_code: Mapped[str] = mapped_column(String(160), nullable=False)
    result_schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    model_profile_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    active_custom_version_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PromptVersion(Base):
    __tablename__ = "prompt_versions"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    kindergarten_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    prompt_definition_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    source_type: Mapped[str] = mapped_column(String(16), nullable=False)
    lifecycle_state: Mapped[str] = mapped_column(String(16), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    based_on_version_id: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    created_by: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    published_by: Mapped[UUID | None] = mapped_column(PgUUID(as_uuid=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PromptTestRun(Base):
    __tablename__ = "prompt_test_runs"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True)
    kindergarten_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    prompt_definition_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    prompt_version_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    model_profile_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    job_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    input_context: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    input_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    prompt_content: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_content_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    result_schema_code: Mapped[str] = mapped_column(String(160), nullable=False)
    result_schema_version: Mapped[int] = mapped_column(Integer, nullable=False)
    model_call_snapshot: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    input_summary: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=False)
    output_content: Mapped[dict[str, object] | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    elapsed_ms: Mapped[int | None] = mapped_column(Integer)
    error_code: Mapped[str | None] = mapped_column(String(64))
    error_summary: Mapped[str | None] = mapped_column(String(1000))
    created_by: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        ForeignKeyConstraint(
            ["kindergarten_id", "job_id"],
            ["background_jobs.kindergarten_id", "background_jobs.id"],
        ),
    )
