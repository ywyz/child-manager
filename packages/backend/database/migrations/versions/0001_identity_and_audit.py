"""建立 M2 身份、会话和早期审计 Schema。"""

from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_identity_and_audit"
down_revision: str | None = "0000_foundation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ADMIN_ROLE_ID = UUID("00000000-0000-7000-8000-000000000001")
TEACHER_ROLE_ID = UUID("00000000-0000-7000-8000-000000000002")


def _timestamps() -> tuple[sa.Column[datetime], sa.Column[datetime]]:
    return (
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
    )


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
    op.create_table(
        "kindergartens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("timezone", sa.String(64), nullable=False, server_default="Asia/Shanghai"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_timestamps(),
        sa.CheckConstraint("timezone = 'Asia/Shanghai'", name="ck_kindergartens_timezone"),
    )
    roles = op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(64), nullable=False, unique=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.bulk_insert(
        roles,
        [
            {"id": ADMIN_ROLE_ID, "code": "admin", "name": "管理员", "is_system": True},
            {"id": TEACHER_ROLE_ID, "code": "teacher", "name": "教师", "is_system": True},
        ],
    )
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("kindergarten_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(120), nullable=False),
        sa.Column("username_normalized", sa.String(120), nullable=False),
        sa.Column("phone_e164", sa.String(32)),
        sa.Column("display_name", sa.String(120), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("password_changed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True)),
        sa.Column("created_by", postgresql.UUID(as_uuid=True)),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True)),
        *_timestamps(),
        sa.ForeignKeyConstraint(["kindergarten_id"], ["kindergartens.id"]),
        sa.UniqueConstraint("kindergarten_id", "id", name="uq_users_kindergarten_id_id"),
        sa.UniqueConstraint(
            "kindergarten_id", "username_normalized", name="uq_users_kindergarten_username"
        ),
    )
    op.create_index(
        "uq_users_kindergarten_phone",
        "users",
        ["kindergarten_id", "phone_e164"],
        unique=True,
        postgresql_where=sa.text("phone_e164 IS NOT NULL"),
    )
    op.create_index("ix_users_kindergarten_active", "users", ["kindergarten_id", "is_active"])
    op.create_foreign_key(
        "fk_users_created_by_same_kindergarten",
        "users",
        "users",
        ["kindergarten_id", "created_by"],
        ["kindergarten_id", "id"],
    )
    op.create_foreign_key(
        "fk_users_updated_by_same_kindergarten",
        "users",
        "users",
        ["kindergarten_id", "updated_by"],
        ["kindergarten_id", "id"],
    )
    op.create_table(
        "user_roles",
        sa.Column("kindergarten_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("assigned_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "user_id"], ["users.kindergarten_id", "users.id"]
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "assigned_by"], ["users.kindergarten_id", "users.id"]
        ),
    )
    op.create_table(
        "refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("kindergarten_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_family_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("token_hash", sa.String(128), nullable=False, unique=True),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True)),
        sa.Column("last_reauthenticated_at", sa.DateTime(timezone=True)),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("revoke_reason", sa.String(64)),
        sa.Column("replaced_by_id", postgresql.UUID(as_uuid=True)),
        sa.Column("client_label", sa.String(160)),
        *_timestamps(),
        sa.UniqueConstraint("kindergarten_id", "id", name="uq_refresh_tokens_kindergarten_id_id"),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "user_id"], ["users.kindergarten_id", "users.id"]
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "replaced_by_id"],
            ["refresh_tokens.kindergarten_id", "refresh_tokens.id"],
        ),
        sa.CheckConstraint("expires_at > issued_at", name="ck_refresh_tokens_expiry"),
        sa.CheckConstraint(
            "replaced_by_id IS NULL OR revoked_at IS NOT NULL",
            name="ck_refresh_tokens_replaced_revoked",
        ),
    )
    op.create_index(
        "ix_refresh_tokens_user_active",
        "refresh_tokens",
        ["kindergarten_id", "user_id", "revoked_at", "expires_at"],
    )
    op.create_index(
        "ix_refresh_tokens_family_revoked", "refresh_tokens", ["token_family_id", "revoked_at"]
    )
    op.create_table(
        "audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("kindergarten_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_code", sa.String(120), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True)),
        sa.Column("actor_role_codes", postgresql.JSONB(), nullable=False),
        sa.Column("resource_type", sa.String(80), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True)),
        sa.Column("request_id", postgresql.UUID(as_uuid=True)),
        sa.Column("trace_id", postgresql.UUID(as_uuid=True)),
        sa.Column("job_id", postgresql.UUID(as_uuid=True)),
        sa.Column("outcome", sa.String(16), nullable=False),
        sa.Column(
            "metadata", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")
        ),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        *_timestamps(),
        sa.UniqueConstraint("kindergarten_id", "id", name="uq_audit_events_kindergarten_id_id"),
        sa.ForeignKeyConstraint(["kindergarten_id"], ["kindergartens.id"]),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "actor_user_id"], ["users.kindergarten_id", "users.id"]
        ),
        sa.CheckConstraint(
            "jsonb_typeof(actor_role_codes) = 'array'", name="ck_audit_actor_roles_array"
        ),
        sa.CheckConstraint("jsonb_typeof(metadata) = 'object'", name="ck_audit_metadata_object"),
        sa.CheckConstraint("outcome IN ('success', 'failure')", name="ck_audit_outcome"),
        sa.CheckConstraint("updated_at = created_at", name="ck_audit_immutable_timestamps"),
    )
    op.create_index(
        "ix_audit_occurred", "audit_events", ["kindergarten_id", sa.text("occurred_at DESC")]
    )
    op.create_index(
        "ix_audit_event_occurred",
        "audit_events",
        ["kindergarten_id", "event_code", sa.text("occurred_at DESC")],
    )
    op.create_index(
        "ix_audit_resource_occurred",
        "audit_events",
        ["kindergarten_id", "resource_type", "resource_id", sa.text("occurred_at DESC")],
    )
    op.create_index(
        "ix_audit_actor_occurred",
        "audit_events",
        ["kindergarten_id", "actor_user_id", sa.text("occurred_at DESC")],
    )


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("refresh_tokens")
    op.drop_table("user_roles")
    op.drop_table("users")
    op.drop_table("roles")
    op.drop_table("kindergartens")
