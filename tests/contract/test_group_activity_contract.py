"""US5 集体活动来源与两阶段 AI 契约 RED。"""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest
from pydantic import ValidationError

from packages.contracts import lesson_plans as contracts


def _contract(name: str) -> type[Any]:
    candidate = getattr(contracts, name, None)
    if candidate is None:
        pytest.fail(f"T118 集体活动来源契约尚未实现：{name}")
    return candidate


def _source_payload() -> dict[str, object]:
    return {
        "id": uuid4(),
        "plan_id": uuid4(),
        "source_type": "docx",
        "original_filename": "班级教案.docx",
        "source_sha256": "a" * 64,
        "extracted_character_count": 12,
        "uploaded_by": uuid4(),
        "created_at": datetime(2026, 3, 2, tzinfo=UTC),
    }


def test_source_metadata_is_closed_and_never_exposes_original_text_or_attachment() -> None:
    source_type = _contract("LessonPlanSource")
    source = source_type(**_source_payload())

    assert source.source_type == "docx"
    assert source.original_filename == "班级教案.docx"
    assert set(source.model_dump()) == set(_source_payload())
    with pytest.raises(ValidationError):
        source_type(**(_source_payload() | {"text": "不得长期返回正文"}))
    with pytest.raises(ValidationError):
        source_type(**(_source_payload() | {"attachment": "不得保存附件"}))


def test_source_page_is_closed_and_preserves_pagination_metadata() -> None:
    page_type = _contract("LessonPlanSourcePage")
    page = page_type(items=[_source_payload()], page=2, page_size=20, total=21)

    assert page.page == 2
    assert page.total == 21
    with pytest.raises(ValidationError):
        page_type(items=[], page=1, page_size=20, total=0, binary_payload=b"forbidden")


def test_split_and_incremental_add_schemas_are_closed_and_validate_index_bounds() -> None:
    split_type = _contract("AiGroupActivity")
    add_step_type = _contract("GroupActivityAddStepResult")
    validate_index = _contract("validate_group_add_step_result")
    split = {
        "theme": "春天",
        "objectives": ["观察变化"],
        "preparation": ["图片"],
        "focus": "表达发现",
        "difficulty": "连续描述",
        "process": [{"heading": "观察", "lines": ["观察图片"]}],
    }

    assert split_type(**split).theme == "春天"
    for field in split:
        with pytest.raises(ValidationError):
            split_type(**{key: value for key, value in split.items() if key != field})
    with pytest.raises(ValidationError):
        split_type(**(split | {"process": [{**split["process"][0], "is_ai_added": True}]}))

    add_step = add_step_type(
        step={"heading": "延伸", "lines": ["绘制春天"]}, suggested_insert_index=1
    )
    assert validate_index(add_step, process_length=1) == add_step
    with pytest.raises(ValueError, match="索引"):
        validate_index(add_step.model_copy(update={"suggested_insert_index": 2}), process_length=1)
    with pytest.raises(ValidationError):
        add_step_type(
            step={"heading": "延伸", "lines": ["绘制春天"], "is_ai_added": True},
            suggested_insert_index=1,
        )
    with pytest.raises(ValidationError):
        add_step_type(step={"heading": "延伸", "lines": ["绘制春天"]}, suggested_insert_index=-1)
