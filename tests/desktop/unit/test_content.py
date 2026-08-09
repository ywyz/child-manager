from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from kindergarten_manager.domain.content import PlanContentV1
from tests.desktop.helpers import implemented

FIXTURE = Path("tests/fixtures/word/daily_activity_plan_v1.json")
SECTION_KEYS = {
    "morning_activity",
    "morning_talk",
    "group_activity",
    "indoor_area_game",
    "afternoon_outdoor_game",
    "daily_reflection",
}


def _sample() -> dict[str, Any]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))["content_snapshot"]


def test_empty_content_keeps_all_word_semantic_sections_structured() -> None:
    content = implemented(PlanContentV1.empty)

    assert set(content.model_dump().keys()) == {"schema_version", *SECTION_KEYS}
    assert content.model_dump()["schema_version"] == 1
    assert content.model_dump()["morning_activity"]["physical_cycle"] == "体能大循环"


def test_content_validates_known_fields_and_has_stable_canonical_json() -> None:
    content = implemented(lambda: PlanContentV1.model_validate(_sample()))

    encoded = content.canonical_json()
    assert json.loads(encoded)["group_activity"]["theme"] == "寻找春天"
    assert encoded == content.canonical_json()
    assert "schema_version" in encoded


def test_unknown_fields_and_duplicate_areas_are_rejected() -> None:
    sample = _sample()
    sample["unknown_section"] = {}
    with pytest.raises(ValueError):
        implemented(lambda: PlanContentV1.model_validate(sample))

    duplicate = _sample()
    duplicate["indoor_area_game"]["areas"] = ["阅读区", "阅读区"]
    with pytest.raises(ValueError, match="重复"):
        implemented(lambda: PlanContentV1.model_validate(duplicate))
