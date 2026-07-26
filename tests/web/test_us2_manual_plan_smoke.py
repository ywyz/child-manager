import asyncio
import json
from importlib import import_module

import pytest
from nicegui import ui
from nicegui.testing.user_interaction import UserInteraction
from nicegui.testing.user_simulation import user_simulation

from packages.contracts.lesson_plans import PlanContentV1


def test_manual_plan_page_exposes_calendar_list_editor_save_archive_and_history() -> None:
    pages = import_module("apps.web.pages.plans")

    assert {
        "教案",
        "日历视图",
        "列表视图",
        "晨间活动",
        "晨间谈话",
        "集体活动",
        "室内区域游戏",
        "下午户外游戏",
        "一日活动反思",
        "保存",
        "归档",
        "恢复归档",
        "历史版本",
    } <= set(pages.plan_page_text())


def test_editor_autosave_delay_is_three_seconds_and_status_is_not_color_only() -> None:
    editor = import_module("apps.web.components.plan_editor")
    status = import_module("apps.web.components.save_status")

    assert editor.AUTOSAVE_DELAY_SECONDS == 3
    assert status.save_status("saving").text == "保存中"
    assert status.save_status("saved").text == "已保存"
    assert status.save_status("failed").text == "保存失败"


@pytest.mark.asyncio
async def test_plan_home_renders_real_views_and_all_frozen_filters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pages = import_module("apps.web.pages.plans")

    async def fake_settings(_path: str, **_kwargs: object) -> dict[str, object]:
        return {
            "ok": True,
            "status": 200,
            "body": {"items": [{"id": "class-1", "name": "向日葵班"}]},
        }

    async def fake_plans(_path: str, **_kwargs: object) -> dict[str, object]:
        return {
            "ok": True,
            "status": 200,
            "body": {
                "items": [
                    {
                        "id": "plan-1",
                        "plan_date": "2026-03-02",
                        "class_name_snapshot": "向日葵班",
                        "authors": [
                            {
                                "user_id": "teacher-1",
                                "display_name_snapshot": "测试教师",
                            }
                        ],
                        "archived_at": None,
                    }
                ]
            },
        }

    monkeypatch.setattr(pages, "same_origin_api_request", fake_settings)
    monkeypatch.setattr(pages, "plan_api_request", fake_plans)

    async with user_simulation(root=pages.build_plans_page) as user:
        await user.open("/")
        await user.should_see("日历视图")
        await user.should_see("列表视图")
        await user.should_see("日期范围开始")
        await user.should_see("日期范围结束")
        await user.should_see("编写教师")
        await user.should_see("归档状态")
        assert len(user.find(ui.tab).elements) == 2


@pytest.mark.asyncio
async def test_editor_input_debounces_autosave_and_archive_immediately_disables_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pages = import_module("apps.web.pages.plans")
    monkeypatch.setattr(pages, "AUTOSAVE_DELAY_SECONDS", 0.01)
    calls: list[tuple[str, str]] = []
    current = {
        "id": "plan-1",
        "class_id": "class-1",
        "semester_id": "semester-1",
        "plan_date": "2026-03-02",
        "kindergarten_name_snapshot": "测试园",
        "class_name_snapshot": "向日葵班",
        "age_group_name_snapshot": "大班",
        "semester_name_snapshot": "2026 春季学期",
        "semester_start_date_snapshot": "2026-02-04",
        "semester_end_date_snapshot": "2026-06-30",
        "teaching_week_number": 5,
        "teaching_week_text": "第（五）周",
        "activity_date_text": "周（一）3月2日",
        "season": "spring",
        "content": PlanContentV1.empty().model_dump(mode="json"),
        "content_schema_version": 1,
        "version": 1,
        "authors": [
            {
                "user_id": "teacher-1",
                "sort_order": 0,
                "display_name_snapshot": "测试教师",
            }
        ],
        "soft_warnings": [],
        "capabilities": ["plans:view", "plans:edit", "plans:archive"],
        "archived_at": None,
    }

    async def fake_request(
        path: str,
        *,
        method: str = "GET",
        payload: dict[str, object] | None = None,
    ) -> dict[str, object]:
        calls.append((path, method))
        if path.endswith("/autosave"):
            assert payload is not None
            current["content"] = payload["content"]
            current["version"] = int(current["version"]) + 1
        elif path.endswith("/archive"):
            current["version"] = int(current["version"]) + 1
            current["archived_at"] = "2026-03-02T08:00:00Z"
            current["capabilities"] = ["plans:view", "plans:snapshots:view", "plans:archive"]
        return {"ok": True, "status": 200, "body": dict(current)}

    monkeypatch.setattr(pages, "plan_api_request", fake_request)

    async with user_simulation(root=lambda: pages.build_plan_editor_page("plan-1")) as user:
        await user.open("/")
        await user.should_see("已保存")
        textareas = user.find(ui.textarea)
        talk_element = next(
            field for field in textareas.elements if field.props.get("label") == "晨间谈话"
        )
        talk = UserInteraction(user, {talk_element}, "晨间谈话")
        talk.clear().type(
            json.dumps(
                {
                    "topic": "爱护植物",
                    "questions": ["为什么要浇水？"],
                },
                ensure_ascii=False,
            )
        )
        talk.trigger("input")
        await asyncio.sleep(0.05)
        assert ("/plan-1/autosave", "PUT") in calls

        user.find("归档").click()
        await asyncio.sleep(0.05)
        assert ("/plan-1/archive", "POST") in calls
        assert all(not field.enabled for field in user.find(ui.textarea).elements)
