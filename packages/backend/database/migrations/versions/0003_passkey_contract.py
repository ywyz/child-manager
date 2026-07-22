"""删除旧密码认证列，冻结通行密钥身份契约。"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003_passkey_contract"
down_revision: str | None = "0002_passkey_expand"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index("ix_users_kindergarten_active", table_name="users")
    op.drop_column("users", "password_hash")
    op.drop_column("users", "password_changed_at")
    op.drop_column("users", "is_active")
    op.create_index("ix_users_kindergarten_status", "users", ["kindergarten_id", "status"])


def downgrade() -> None:
    op.drop_index("ix_users_kindergarten_status", table_name="users")
    op.add_column("users", sa.Column("is_active", sa.Boolean(), nullable=True))
    op.add_column("users", sa.Column("password_changed_at", sa.DateTime(timezone=True)))
    op.add_column("users", sa.Column("password_hash", sa.Text()))
    op.create_index("ix_users_kindergarten_active", "users", ["kindergarten_id", "is_active"])
