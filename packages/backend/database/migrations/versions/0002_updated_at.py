"""add updated_at to identity audit tables

Revision ID: 0002_add_updated_at_to_identity_audit
Revises: 0001_identity_and_audit
Create Date: 2026-07-17 00:00:00.000000

说明：冻结 Schema 已将 updated_at 下沉到 0001_identity_and_audit，
本迁移保留以保持 Alembic 链完整，不再执行额外变更。

"""

from collections.abc import Sequence

revision: str = "0002_updated_at"
down_revision: str | None = "0001_identity_and_audit"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
