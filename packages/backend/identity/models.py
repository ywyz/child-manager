"""身份与认证 ORM 模型。

本模型与 docs/design/database-schema.md §5 冻结 Schema 保持一致。
"""

from datetime import UTC, datetime
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKeyConstraint,
    Index,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from packages.backend.database.base import Base


def _now() -> datetime:
    return datetime.now(UTC)


def _uuid() -> str:
    return str(uuid4())


class Kindergarten(Base):
    __tablename__ = "kindergartens"
    __table_args__ = (
        CheckConstraint("timezone = 'Asia/Shanghai'", name="ck_kindergartens_timezone"),
    )

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False, default="Asia/Shanghai")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now, onupdate=_now
    )


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=_uuid)
    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("kindergarten_id", "id", name="uq_users_kindergarten_id"),
        UniqueConstraint(
            "kindergarten_id",
            "username_normalized",
            name="uq_users_kindergarten_username",
        ),
        Index(
            "ix_users_kindergarten_phone",
            "kindergarten_id",
            "phone_e164",
            unique=True,
            postgresql_where=sa.text("phone_e164 IS NOT NULL"),
        ),
        Index("ix_users_kindergarten_active", "kindergarten_id", "is_active"),
        ForeignKeyConstraint(
            ["kindergarten_id"],
            ["kindergartens.id"],
            name="fk_users_kindergarten",
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "created_by"],
            ["users.kindergarten_id", "users.id"],
            name="fk_users_created_by",
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "updated_by"],
            ["users.kindergarten_id", "users.id"],
            name="fk_users_updated_by",
        ),
        CheckConstraint(
            "phone_e164 IS NULL OR phone_e164 <> ''",
            name="ck_users_phone_e164",
        ),
    )

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=_uuid)
    kindergarten_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), nullable=False)
    username: Mapped[str] = mapped_column(String(120), nullable=False)
    username_normalized: Mapped[str] = mapped_column(String(120), nullable=False)
    phone_e164: Mapped[str | None] = mapped_column(String(32), nullable=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    password_changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), nullable=True)
    updated_by: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now, onupdate=_now
    )

    roles: Mapped[list[Role]] = relationship(
        "Role",
        secondary="user_roles",
        primaryjoin="User.id == UserRole.user_id",
        secondaryjoin="Role.id == UserRole.role_id",
        lazy="selectin",
        viewonly=True,
    )


class UserRole(Base):
    __tablename__ = "user_roles"
    __table_args__ = (
        ForeignKeyConstraint(
            ["kindergarten_id", "user_id"],
            ["users.kindergarten_id", "users.id"],
            name="fk_user_roles_user",
        ),
        ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
            name="fk_user_roles_role",
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "assigned_by"],
            ["users.kindergarten_id", "users.id"],
            name="fk_user_roles_assigned_by",
        ),
    )

    kindergarten_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True)
    user_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True)
    role_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True)
    assigned_by: Mapped[str] = mapped_column(Uuid(as_uuid=False), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now, onupdate=_now
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = (
        UniqueConstraint("kindergarten_id", "id", name="uq_refresh_tokens_kindergarten_id"),
        ForeignKeyConstraint(
            ["kindergarten_id", "user_id"],
            ["users.kindergarten_id", "users.id"],
            name="fk_refresh_tokens_user",
        ),
        ForeignKeyConstraint(
            ["kindergarten_id", "replaced_by_id"],
            ["refresh_tokens.kindergarten_id", "refresh_tokens.id"],
            name="fk_refresh_tokens_replaced_by",
        ),
        CheckConstraint(
            "expires_at > issued_at",
            name="ck_refresh_tokens_expires_after_issued",
        ),
        CheckConstraint(
            "replaced_by_id IS NULL OR revoked_at IS NOT NULL",
            name="ck_refresh_tokens_replaced_implies_revoked",
        ),
        Index(
            "ix_refresh_tokens_user_revoked_expires",
            "kindergarten_id",
            "user_id",
            "revoked_at",
            "expires_at",
        ),
        Index(
            "ix_refresh_tokens_family_revoked",
            "token_family_id",
            "revoked_at",
        ),
    )

    id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=_uuid)
    kindergarten_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), nullable=False)
    user_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), nullable=False)
    token_family_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    family_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    family_revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    revoke_reason: Mapped[str | None] = mapped_column(String(64), nullable=True)
    replaced_by_id: Mapped[str | None] = mapped_column(Uuid(as_uuid=False), nullable=True)
    client_label: Mapped[str | None] = mapped_column(String(160), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=_now, onupdate=_now
    )
