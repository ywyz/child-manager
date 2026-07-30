"""T122 集体活动拆分与新增环节 Worker RED。"""

from copy import deepcopy
from importlib import import_module
from typing import Any
from uuid import uuid4

import pytest

SPLIT_RESULT = {
    "theme": "春天",
    "objectives": ["观察变化"],
    "preparation": ["图片"],
    "focus": "表达发现",
    "difficulty": "连续描述",
    "process": [{"heading": "观察", "lines": ["观察图片"]}],
}


def _jobs() -> Any:
    try:
        return import_module("packages.backend.lesson_plans.group_activity_ai")
    except ModuleNotFoundError:
        pytest.fail("T122 集体活动拆分与新增环节任务尚未实现")


def _service() -> Any:
    candidate = getattr(_jobs(), "GroupActivityJobService", None)
    if candidate is None:
        pytest.fail("T122 集体活动任务服务尚未实现：GroupActivityJobService")
    return candidate()


def _confirmed_source() -> dict[str, str]:
    return {
        "id": str(uuid4()),
        "confirmed_at": "2026-03-02T08:00:00Z",
        "extracted_text": "教师确认的集体活动原文。",
    }


def _assert_complete_split(result: dict[str, Any]) -> None:
    for field in ("theme", "objectives", "preparation", "focus", "difficulty", "process"):
        assert result[field]
    assert all(step["heading"] and step["lines"] for step in result["process"])
    assert all(all(line.strip() for line in step["lines"]) for step in result["process"])


def test_split_requires_confirmed_source_and_completes_every_required_field() -> None:
    service = _service()
    source = _confirmed_source()

    with pytest.raises(ValueError, match="确认"):
        service.create_split_preview(
            {key: value for key, value in source.items() if key != "confirmed_at"}
        )
    preview = service.create_split_preview(source)
    assert preview["task_code"] == "group_activity_split"
    assert preview["input_context"]["source_id"] == source["id"]
    assert preview["input_context"]["source_text"] == source["extracted_text"]
    result = service.complete_split_result(preview, result=deepcopy(SPLIT_RESULT))
    _assert_complete_split(result)
    completed = service.complete_split_result(
        preview,
        result=deepcopy(SPLIT_RESULT) | {"focus": "", "difficulty": ""},
    )
    _assert_complete_split(completed)


def test_split_rejects_ai_added_and_adoption_assigns_false_to_every_split_step() -> None:
    service = _service()
    preview = service.create_split_preview(_confirmed_source())

    with pytest.raises(ValueError, match="is_ai_added"):
        service.complete_split_result(
            preview,
            result=deepcopy(SPLIT_RESULT)
            | {"process": [{"heading": "观察", "lines": ["观察图片"], "is_ai_added": True}]},
        )
    adopted = service.adopt_and_save_split(preview, result=deepcopy(SPLIT_RESULT))
    assert [step["is_ai_added"] for step in adopted["group_activity"]["process"]] == [False]


def test_add_step_requires_saved_adoption_and_freezes_the_current_group_activity() -> None:
    service = _service()
    preview = service.create_split_preview(_confirmed_source())

    with pytest.raises(ValueError, match="采用并保存"):
        service.freeze_add_step_input(
            {"group_activity": deepcopy(SPLIT_RESULT), "adopted_and_saved": True}
        )
    adopted = service.adopt_and_save_split(preview, result=deepcopy(SPLIT_RESULT))
    frozen = service.freeze_add_step_input(adopted)
    assert frozen["group_activity"] == adopted["group_activity"]


def test_add_step_has_independent_preview_and_retries_only_a_real_failed_add_without_rollback() -> (
    None
):
    service = _service()
    source = _confirmed_source()
    split_preview = service.create_split_preview(source)
    adopted = service.adopt_and_save_split(split_preview, result=deepcopy(SPLIT_RESULT))
    frozen = service.freeze_add_step_input(adopted)
    add_preview = service.create_add_step_preview(frozen)

    assert split_preview["id"] != add_preview["id"]
    assert add_preview["task_code"] == "group_activity_add_step"
    assert add_preview["input_context"]["group_activity"] == adopted["group_activity"]
    updated = service.adopt_add_step(
        adopted,
        {"step": {"heading": "延伸", "lines": ["绘制春天"]}, "suggested_insert_index": 1},
    )
    assert [step["is_ai_added"] for step in updated["group_activity"]["process"]] == [False, True]

    preserved_split = deepcopy(adopted)
    failed = service.record_add_step_failure(add_preview, error_code="ai.timeout")
    assert failed["status"] == "failed"
    retry = service.retry_failed_add_step(failed)
    assert retry["task_code"] == "group_activity_add_step"
    assert retry["input_context"]["group_activity"] == preserved_split["group_activity"]
    assert adopted == preserved_split
