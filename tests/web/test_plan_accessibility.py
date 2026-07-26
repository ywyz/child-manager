import importlib

import pytest
from nicegui import ui
from nicegui.testing.user_simulation import user_simulation

from packages.contracts.lesson_plans import PlanContentV1


@pytest.mark.asyncio
async def test_rendered_plan_editor_has_labelled_status_fields_focus_order_and_touch_targets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pages = importlib.import_module("apps.web.pages.plans")
    plan = {
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

    async def fake_request(_path: str, **_kwargs: object) -> dict[str, object]:
        return {"ok": True, "status": 200, "body": plan}

    monkeypatch.setattr(pages, "plan_api_request", fake_request)

    async with user_simulation(root=lambda: pages.build_plan_editor_page("plan-1")) as user:
        await user.open("/")
        await user.should_see("已保存")
        textareas = sorted(user.find(ui.textarea).elements, key=lambda element: element.id)
        buttons = sorted(user.find(ui.button).elements, key=lambda element: element.id)
        status = next(
            label for label in user.find(ui.label).elements if label.props.get("role") == "status"
        )

        assert [field.props["label"] for field in textareas] == [
            "晨间活动",
            "晨间谈话",
            "集体活动",
            "室内区域游戏",
            "下午户外游戏",
            "一日活动反思",
        ]
        assert all(field.props.get("aria-label") for field in textareas)
        assert all(field.props.get("aria-describedby") == "plan-save-status" for field in textareas)
        assert status.props.get("id") == "plan-save-status"
        assert status.props.get("aria-live") == "polite"
        assert status.text == "已保存"
        assert max(field.id for field in textareas) < min(button.id for button in buttons)
        assert all("min-h-[44px]" in button.classes for button in buttons)
