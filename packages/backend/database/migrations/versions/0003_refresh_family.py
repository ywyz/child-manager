"""refresh token family absolute expiration

Revision ID: 0003_refresh_family
Revises: 0002_updated_at
Create Date: 2026-07-17 00:00:00.000000

说明：冻结 Schema 已将 family_expires_at 下沉到 0001_identity_and_audit，
本迁移保留以保持 Alembic 链完整，不再执行额外变更。

"""

from collections.abc import Sequence

revision: str = "0003_refresh_family"
down_revision: str | None = "0002_updated_at"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
