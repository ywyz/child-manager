from __future__ import annotations

from copy import deepcopy

import pytest

from kindergarten_manager.domain.content import PlanContentV1
from tests.desktop.helpers import pending_module, pending_symbol


def _module():
    return pending_module("kindergarten_manager.domain.ai")


def test_ai_schema_registry_allows_only_slice_2a_sections() -> None:
    module = _module()
    schema_for = pending_symbol(module, "schema_for")

    allowed = {
        "morning_activity",
        "morning_talk",
        "indoor_area_game",
        "afternoon_outdoor_game",
        "daily_reflection",
    }
    assert {code for code in allowed if schema_for(code) is not None} == allowed
    with pytest.raises(ValueError, match="不支持"):
        schema_for("group_activity")


def test_canonical_json_hash_is_key_order_independent_and_rejects_nan() -> None:
    module = _module()
    canonical_json_sha256 = pending_symbol(module, "canonical_json_sha256")

    assert canonical_json_sha256({"主题": "春天", "问题": [1, 2]}) == canonical_json_sha256(
        {"问题": [1, 2], "主题": "春天"}
    )
    with pytest.raises(ValueError):
        canonical_json_sha256({"invalid": float("nan")})


def test_generation_input_contains_only_target_and_explicit_teacher_context() -> None:
    module = _module()
    build_generation_input = pending_symbol(module, "build_generation_input")
    content = PlanContentV1.empty().model_dump()
    content["morning_talk"] = {"topic": "春天", "questions": ["你发现了什么？"]}
    content["daily_reflection"] = {
        "highlights": "不应发送",
        "issues": "不应发送",
        "adjustments": "不应发送",
    }

    frozen = build_generation_input(
        section_code="morning_talk",
        content=content,
        teacher_context="只补充春季观察",
    )

    assert frozen == {
        "schema_code": "morning_talk",
        "target": {"topic": "春天", "questions": ["你发现了什么？"]},
        "teacher_context": "只补充春季观察",
    }
    assert "daily_reflection" not in repr(frozen)


def test_preview_staleness_depends_only_on_target_section_hash() -> None:
    module = _module()
    section_sha256 = pending_symbol(module, "section_sha256")
    preview_is_stale = pending_symbol(module, "preview_is_stale")
    original = PlanContentV1.empty().model_dump()
    expected = section_sha256(original, "morning_talk")

    unrelated = deepcopy(original)
    unrelated["daily_reflection"]["highlights"] = "教师新写的反思"
    assert not preview_is_stale(expected, unrelated, "morning_talk")

    target_changed = deepcopy(original)
    target_changed["morning_talk"]["topic"] = "教师已修改"
    assert preview_is_stale(expected, target_changed, "morning_talk")


@pytest.mark.parametrize(
    ("payload", "category"),
    [
        ({"topic": "缺少问题"}, "missing_field"),
        ({"topic": "春天", "questions": "不是数组"}, "wrong_type"),
        ({"topic": "春天", "questions": [], "extra": "越界"}, "unknown_field"),
    ],
)
def test_structured_output_errors_have_stable_categories(
    payload: dict[str, object],
    category: str,
) -> None:
    module = _module()
    validate_section_output = pending_symbol(module, "validate_section_output")
    validation_error = pending_symbol(module, "AiOutputValidationError")

    with pytest.raises(validation_error) as captured:
        validate_section_output("morning_talk", payload)
    assert captured.value.category == category
