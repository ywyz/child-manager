"""T125 集体活动两阶段 NiceGUI 冒烟 RED。"""

from copy import deepcopy
from importlib import import_module
from typing import Any, cast

import pytest
from nicegui import ui
from nicegui.testing.user_interaction import UserInteraction
from nicegui.testing.user_simulation import user_simulation

from tests.web.test_plan_ai_smoke import PLAN_ID, _job, _plan

SPLIT_JOB_ID = "00000000-0000-0000-0000-000000000031"
ADD_JOB_ID = "00000000-0000-0000-0000-000000000032"
SOURCE_TEXT = "教师确认的春季观察活动原文。"
SPLIT_RESULT = {
    "theme": "春天",
    "objectives": ["观察变化"],
    "preparation": ["图片"],
    "focus": "表达发现",
    "difficulty": "连续描述",
    "process": [{"heading": "观察", "lines": ["观察图片"]}],
}


def _button(user: Any, text: str) -> Any:
    return next(button for button in user.find(ui.button).elements if text in str(button.text))


@pytest.mark.asyncio
async def test_source_confirmation_then_adopted_split_enables_add_step(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pages = import_module("apps.web.pages.plans")
    plan = cast(dict[str, Any], _plan())
    requests: list[tuple[str, str, dict[str, object] | None]] = []
    adopted = False

    async def fake_request(
        path: str,
        *,
        method: str = "GET",
        payload: dict[str, object] | None = None,
        **_kwargs: object,
    ) -> dict[str, object]:
        nonlocal adopted
        requests.append((path, method, payload))
        if path.endswith("/group-activity-sources/text"):
            assert payload is not None
            assert payload["text"] == SOURCE_TEXT
            return {"ok": True, "status": 201, "body": {"id": "source-1"}}
        if path.endswith("/ai/generations"):
            assert payload is not None
            assert payload["task_code"] == "group_activity_split"
            assert payload["source_id"] == "source-1"
            return {
                "ok": True,
                "status": 202,
                "body": {
                    "job": _job(
                        job_id=SPLIT_JOB_ID,
                        status="awaiting_confirmation",
                        target_section="group_activity",
                    )
                },
            }
        if path.endswith("/jobs"):
            items = (
                []
                if adopted
                else [
                    _job(
                        job_id=SPLIT_JOB_ID,
                        status="awaiting_confirmation",
                        target_section="group_activity",
                    )
                ]
            )
            return {
                "ok": True,
                "status": 200,
                "body": {"items": items, "page": 1, "page_size": 20, "total": len(items)},
            }
        if path.endswith(f"/jobs/{SPLIT_JOB_ID}/preview"):
            return {
                "ok": True,
                "status": 200,
                "body": {
                    "job_id": SPLIT_JOB_ID,
                    "target_section": "group_activity",
                    "output_content": SPLIT_RESULT,
                },
            }
        if path.endswith(f"/jobs/{SPLIT_JOB_ID}/adopt"):
            adopted = True
            updated = deepcopy(plan)
            updated["version"] = 2
            updated["content"]["group_activity"] = SPLIT_RESULT | {
                "process": [{"heading": "观察", "lines": ["观察图片"], "is_ai_added": False}]
            }
            return {"ok": True, "status": 200, "body": updated}
        return {"ok": True, "status": 200, "body": plan}

    monkeypatch.setattr(pages, "plan_api_request", fake_request)
    async with user_simulation(root=lambda: pages.build_plan_editor_page(PLAN_ID)) as user:
        await user.open("/")
        await user.should_see("确认集体活动原文")
        await user.should_see("尚未新增适龄环节")
        source_editor = next(
            field
            for field in user.find(ui.textarea).elements
            if field.props.get("label") == "集体活动原文"
        )
        UserInteraction(user, {source_editor}, "集体活动原文").trigger("focus").type(SOURCE_TEXT)
        add_button = _button(user, "新增适龄环节")
        assert not add_button.enabled
        UserInteraction(user, {_button(user, "确认集体活动原文")}, "确认集体活动原文").trigger(
            "keydown.enter", {"key": "Enter"}
        )
        await user.should_see("拆分预览")
        UserInteraction(user, {_button(user, "采用拆分结果")}, "采用拆分结果").trigger(
            "keydown.enter", {"key": "Enter"}
        )
        await user.should_see("可新增适龄环节")
        assert _button(user, "新增适龄环节").enabled

    assert any(
        path.endswith("/group-activity-sources/text") and method == "POST" and payload is not None
        for path, method, payload in requests
    )
    assert any(
        path.endswith("/ai/generations") and method == "POST" and payload is not None
        for path, method, payload in requests
    )
    assert any(
        path == f"/jobs/{SPLIT_JOB_ID}/adopt" and method == "POST"
        for path, method, _payload in requests
    )


@pytest.mark.asyncio
async def test_failed_add_preserves_split_and_added_step_marker_can_be_cleared(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pages = import_module("apps.web.pages.plans")
    plan = cast(dict[str, Any], _plan())
    plan["content"]["group_activity"] = SPLIT_RESULT | {
        "process": [
            {"heading": "观察", "lines": ["观察图片"], "is_ai_added": False},
            {"heading": "延伸", "lines": ["绘制春天"], "is_ai_added": True},
        ]
    }
    requests: list[tuple[str, str, dict[str, object] | None]] = []

    async def fake_request(
        path: str,
        *,
        method: str = "GET",
        payload: dict[str, object] | None = None,
        **_kwargs: object,
    ) -> dict[str, object]:
        requests.append((path, method, payload))
        if path.endswith("/jobs"):
            return {
                "ok": True,
                "status": 200,
                "body": {
                    "items": [
                        _job(
                            job_id=ADD_JOB_ID,
                            status="failed",
                            target_section="group_activity",
                            error_code="ai.timeout",
                        )
                    ],
                    "page": 1,
                    "page_size": 20,
                    "total": 1,
                },
            }
        if path.endswith(f"/jobs/{ADD_JOB_ID}/retry"):
            return {
                "ok": True,
                "status": 202,
                "body": {
                    "job": _job(
                        job_id="00000000-0000-0000-0000-000000000033",
                        status="pending_dispatch",
                        target_section="group_activity",
                    )
                },
            }
        if path.endswith("/autosave"):
            assert method == "PUT"
            assert payload is not None
            content = cast(dict[str, Any], payload["content"])
            assert content["group_activity"]["process"][-1]["is_ai_added"] is False
            plan["content"] = deepcopy(content)
            plan["version"] = int(plan["version"]) + 1
            return {"ok": True, "status": 200, "body": plan}
        return {"ok": True, "status": 200, "body": plan}

    monkeypatch.setattr(pages, "plan_api_request", fake_request)
    async with user_simulation(root=lambda: pages.build_plan_editor_page(PLAN_ID)) as user:
        await user.open("/")
        await user.should_see("新增环节失败，已采用的拆分结果未变化")
        await user.should_see("AI 新增环节")
        split_editor = next(
            field
            for field in user.find(ui.textarea).elements
            if field.props.get("label") == "集体活动"
        )
        assert "观察" in str(split_editor.value)
        UserInteraction(user, {_button(user, "重试新增适龄环节")}, "重试新增适龄环节").trigger(
            "keydown.enter", {"key": "Enter"}
        )
        UserInteraction(user, {_button(user, "取消 AI 新增标记")}, "取消 AI 新增标记").trigger(
            "keydown.enter", {"key": "Enter"}
        )
        await user.should_not_see("AI 新增环节")
        assert "观察" in str(split_editor.value)

    assert any(
        path == f"/jobs/{ADD_JOB_ID}/retry" and method == "POST"
        for path, method, _payload in requests
    )
    assert any(
        path.endswith("/autosave") and method == "PUT" and payload is not None
        for path, method, payload in requests
    )
    assert plan["content"]["group_activity"]["process"][-1]["is_ai_added"] is False
