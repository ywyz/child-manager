"""允许集体活动拆分提示词与结构化预览。"""

from __future__ import annotations

from alembic import op

revision = "0004_desktop_group_activity_ai"
down_revision = "0003_desktop_ai_profiles"
branch_labels = None
depends_on = None

_PROMPT_CODES = (
    "'morning_activity', 'morning_talk', 'indoor_area_game', "
    "'afternoon_outdoor_game', 'daily_reflection', 'group_activity'"
)


def upgrade() -> None:
    with op.batch_alter_table("prompt_overrides") as batch:
        batch.drop_constraint("ck_prompt_overrides_prompt_code", type_="check")
        batch.create_check_constraint(
            "ck_prompt_overrides_prompt_code",
            f"prompt_code IN ({_PROMPT_CODES})",
        )
    with op.batch_alter_table("ai_previews") as batch:
        batch.drop_constraint("ck_ai_previews_section_code", type_="check")
        batch.create_check_constraint(
            "ck_ai_previews_section_code",
            f"section_code IN ({_PROMPT_CODES})",
        )


def downgrade() -> None:
    original_codes = (
        "'morning_activity', 'morning_talk', 'indoor_area_game', "
        "'afternoon_outdoor_game', 'daily_reflection'"
    )
    with op.batch_alter_table("ai_previews") as batch:
        batch.drop_constraint("ck_ai_previews_section_code", type_="check")
        batch.create_check_constraint(
            "ck_ai_previews_section_code",
            f"section_code IN ({original_codes})",
        )
    with op.batch_alter_table("prompt_overrides") as batch:
        batch.drop_constraint("ck_prompt_overrides_prompt_code", type_="check")
        batch.create_check_constraint(
            "ck_prompt_overrides_prompt_code",
            f"prompt_code IN ({original_codes})",
        )
