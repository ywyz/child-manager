"""identity and audit

Revision ID: 0001_identity_and_audit
Revises: 0000_foundation
Create Date: 2026-07-17 00:00:00.000000

"""

from collections.abc import Sequence
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_identity_and_audit"
down_revision: str | None = "0000_foundation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    _create_kindergartens()
    _create_roles()
    _create_users()
    _create_user_roles()
    _create_refresh_tokens()
    _create_audit_events()
    _seed_roles()


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_table("refresh_tokens")
    op.drop_table("user_roles")
    op.drop_table("users")
    op.drop_table("roles")
    op.drop_table("kindergartens")


def _create_kindergartens() -> None:
    op.create_table(
        "kindergartens",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column(
            "timezone",
            sa.String(64),
            nullable=False,
            server_default="Asia/Shanghai",
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("timezone = 'Asia/Shanghai'", name="ck_kindergartens_timezone"),
    )


def _create_roles() -> None:
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", name="uq_roles_code"),
    )


def _create_users() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("kindergarten_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("username", sa.String(120), nullable=False),
        sa.Column("username_normalized", sa.String(120), nullable=False),
        sa.Column("phone_e164", sa.String(32), nullable=True),
        sa.Column("display_name", sa.String(120), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column(
            "password_changed_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("kindergarten_id", "id", name="uq_users_kindergarten_id"),
        sa.UniqueConstraint(
            "kindergarten_id",
            "username_normalized",
            name="uq_users_kindergarten_username",
        ),
        sa.Index(
            "ix_users_kindergarten_phone",
            "kindergarten_id",
            "phone_e164",
            unique=True,
            postgresql_where=sa.text("phone_e164 IS NOT NULL"),
        ),
        sa.Index("ix_users_kindergarten_active", "kindergarten_id", "is_active"),
        sa.ForeignKeyConstraint(
            ["kindergarten_id"],
            ["kindergartens.id"],
            name="fk_users_kindergarten",
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "created_by"],
            ["users.kindergarten_id", "users.id"],
            name="fk_users_created_by",
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "updated_by"],
            ["users.kindergarten_id", "users.id"],
            name="fk_users_updated_by",
        ),
        sa.CheckConstraint(
            "phone_e164 IS NULL OR phone_e164 <> ''",
            name="ck_users_phone_e164",
        ),
    )


def _create_user_roles() -> None:
    op.create_table(
        "user_roles",
        sa.Column("kindergarten_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("assigned_by", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column(
            "assigned_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("kindergarten_id", "user_id", "role_id"),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "user_id"],
            ["users.kindergarten_id", "users.id"],
            name="fk_user_roles_user",
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
            name="fk_user_roles_role",
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "assigned_by"],
            ["users.kindergarten_id", "users.id"],
            name="fk_user_roles_assigned_by",
        ),
    )


def _create_refresh_tokens() -> None:
    op.create_table(
        "refresh_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("kindergarten_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("token_family_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("token_hash", sa.String(128), nullable=False),
        sa.Column(
            "issued_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("family_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("family_revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoke_reason", sa.String(64), nullable=True),
        sa.Column("replaced_by_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("client_label", sa.String(160), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("kindergarten_id", "id", name="uq_refresh_tokens_kindergarten_id"),
        sa.UniqueConstraint("token_hash", name="uq_refresh_tokens_token_hash"),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "user_id"],
            ["users.kindergarten_id", "users.id"],
            name="fk_refresh_tokens_user",
        ),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "replaced_by_id"],
            ["refresh_tokens.kindergarten_id", "refresh_tokens.id"],
            name="fk_refresh_tokens_replaced_by",
        ),
        sa.CheckConstraint(
            "expires_at > issued_at",
            name="ck_refresh_tokens_expires_after_issued",
        ),
        sa.CheckConstraint(
            "replaced_by_id IS NULL OR revoked_at IS NOT NULL",
            name="ck_refresh_tokens_replaced_implies_revoked",
        ),
        sa.Index(
            "ix_refresh_tokens_user_revoked_expires",
            "kindergarten_id",
            "user_id",
            "revoked_at",
            "expires_at",
        ),
        sa.Index(
            "ix_refresh_tokens_family_revoked",
            "token_family_id",
            "revoked_at",
        ),
    )


def _create_audit_events() -> None:
    op.create_table(
        "audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("kindergarten_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("event_code", sa.String(120), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column(
            "actor_role_codes",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("resource_type", sa.String(80), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("request_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("trace_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("outcome", sa.String(16), nullable=False),
        sa.Column(
            "metadata",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("kindergarten_id", "id", name="uq_audit_events_kindergarten_id"),
        sa.ForeignKeyConstraint(
            ["kindergarten_id", "actor_user_id"],
            ["users.kindergarten_id", "users.id"],
            name="fk_audit_events_actor_user",
        ),
        sa.CheckConstraint(
            "jsonb_typeof(actor_role_codes) = 'array'",
            name="ck_audit_events_actor_role_codes_array",
        ),
        sa.CheckConstraint(
            "jsonb_typeof(metadata) = 'object'",
            name="ck_audit_events_metadata_object",
        ),
        sa.CheckConstraint(
            "outcome IN ('success', 'failure')",
            name="ck_audit_events_outcome",
        ),
        sa.CheckConstraint(
            "updated_at = created_at",
            name="ck_audit_events_immutable",
        ),
        sa.Index(
            "ix_audit_events_lookup",
            "kindergarten_id",
            "event_code",
            "resource_type",
            "resource_id",
        ),
        sa.Index("ix_audit_events_occurred", "occurred_at"),
    )


def _seed_roles() -> None:
    roles_table = sa.table(
        "roles",
        sa.column("id", postgresql.UUID(as_uuid=False)),
        sa.column("code", sa.String),
        sa.column("name", sa.String),
        sa.column("is_system", sa.Boolean),
    )
    op.bulk_insert(
        roles_table,
        [
            {
                "id": str(uuid4()),
                "code": "admin",
                "name": "管理员",
                "is_system": True,
            },
            {
                "id": str(uuid4()),
                "code": "teacher",
                "name": "教师",
                "is_system": True,
            },
        ],
    )
