from importlib import import_module

import pytest
from pydantic import ValidationError


def _contracts():
    return import_module("packages.contracts.lesson_plans")


def _schemas():
    return import_module("packages.backend.lesson_plans.schemas")


def test_empty_v1_content_supports_progressive_manual_editing() -> None:
    content = _contracts().PlanContentV1.empty()

    assert content.morning_activity.physical_cycle == "体能大循环"
    assert content.morning_activity.objectives == []
    assert content.morning_talk.questions == []
    assert content.daily_reflection.highlights == ""


def test_completeness_is_independent_from_progressive_schema_validation() -> None:
    content = _contracts().PlanContentV1.empty()
    content.morning_activity.group_game = "接力跑"
    content.morning_activity.free_game = "跳绳"
    content.morning_activity.focus_guidance = "注意摆臂。"
    content.morning_activity.objectives = ["目标一。", "目标二。", "目标三。"]
    content.morning_activity.guidance_points = ["要点一。", "要点二。", "要点三。"]
    content.morning_talk.topic = "爱护植物"
    content.morning_talk.questions = ["问题一？", "问题二？", "问题三？"]

    status = _schemas().content_completeness(content)

    assert status["morning_activity"] is True
    assert status["morning_talk"] is True
    assert status["group_activity"] is False


def test_statement_and_question_punctuation_are_strictly_chinese() -> None:
    content = _contracts().PlanContentV1.empty()
    content.morning_talk.topic = "分享"
    content.morning_talk.questions = ["问题一?", "问题二？", "问题三？"]

    assert _schemas().content_completeness(content)["morning_talk"] is False


def test_reflection_is_nfkc_normalized_and_limited_to_200_codepoints() -> None:
    contracts = _contracts()
    content = contracts.PlanContentV1.empty()
    content.daily_reflection = contracts.DailyReflection(
        highlights="Ａ",
        issues="好" * 99,
        adjustments="改" * 100,
    )

    assert content.daily_reflection.highlights == "A"
    with pytest.raises(ValidationError):
        contracts.DailyReflection(highlights="好" * 201, issues="", adjustments="")


def test_unknown_fields_and_unknown_content_versions_are_not_silently_coerced() -> None:
    contracts = _contracts()
    with pytest.raises(ValidationError):
        contracts.PlanContentV1.model_validate(
            {**contracts.PlanContentV1.empty().model_dump(), "future_section": {}}
        )

    parsed = _schemas().parse_content_for_editing({"future_section": {}}, schema_version=2)
    assert parsed.content is None
    assert parsed.editable is False
