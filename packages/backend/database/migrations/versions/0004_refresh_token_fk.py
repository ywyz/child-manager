"""refresh token composite foreign key

Revision ID: 0004_refresh_token_fk
Revises: 0003_refresh_family
Create Date: 2026-07-18 00:00:00.000000

说明：冻结 Schema 已将 refresh_tokens 组合外键下沉到 0001_identity_and_audit，
本迁移保留以保持 Alembic 链完整，不再执行额外变更。

"""

from collections.abc import Sequence

revision: str = "0004_refresh_token_fk"
down_revision: str | None = "0003_refresh_family"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
