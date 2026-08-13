"""增加独立的视觉模型预配置。"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0003_desktop_ai_profiles"
down_revision = "0002_desktop_ai"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("ai_configuration") as batch:
        batch.add_column(sa.Column("vision_base_url", sa.Text()))
        batch.add_column(sa.Column("vision_model_name", sa.Text()))
        batch.add_column(
            sa.Column(
                "vision_credential_configured",
                sa.Integer(),
                nullable=False,
                server_default="0",
            )
        )
        batch.add_column(
            sa.Column("vision_enabled", sa.Integer(), nullable=False, server_default="0")
        )
        batch.create_check_constraint(
            "ck_ai_configuration_vision_base_url",
            "vision_base_url IS NULL OR length(trim(vision_base_url)) BETWEEN 1 AND 2048",
        )
        batch.create_check_constraint(
            "ck_ai_configuration_vision_model_name",
            "vision_model_name IS NULL OR length(trim(vision_model_name)) BETWEEN 1 AND 200",
        )
        batch.create_check_constraint(
            "ck_ai_configuration_vision_credential_configured",
            "vision_credential_configured IN (0, 1)",
        )
        batch.create_check_constraint(
            "ck_ai_configuration_vision_enabled",
            "vision_enabled IN (0, 1)",
        )


def downgrade() -> None:
    with op.batch_alter_table("ai_configuration") as batch:
        batch.drop_constraint(
            "ck_ai_configuration_vision_enabled",
            type_="check",
        )
        batch.drop_constraint(
            "ck_ai_configuration_vision_credential_configured",
            type_="check",
        )
        batch.drop_constraint(
            "ck_ai_configuration_vision_model_name",
            type_="check",
        )
        batch.drop_constraint(
            "ck_ai_configuration_vision_base_url",
            type_="check",
        )
        batch.drop_column("vision_enabled")
        batch.drop_column("vision_credential_configured")
        batch.drop_column("vision_model_name")
        batch.drop_column("vision_base_url")
