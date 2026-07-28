"""M6 教案栏目内预览与可恢复状态的 NiceGUI RED 冒烟。"""

from datetime import UTC, datetime
from importlib import import_module
from uuid import uuid4

import pytest
from nicegui import ui
from nicegui.testing.user_interaction import UserInteraction
from nicegui.testing.user_simulation import user_simulation

from packages.contracts.lesson_plans import PlanContentV1

PLAN_ID = "00000000-0000-0000-0000-000000000001"
CLASS_ID = "00000000-0000-0000-0000-000000000002"
SEMESTER_ID = "00000000-0000-0000-0000-000000000003"
TEACHER_ID = "00000000-0000-0000-0000-000000000004"


def _plan() -> dict[str, object]:
    content = PlanContentV1.empty().model_dump(mode="json")
    content["morning_talk"] = {
        "topic": "教师原文",
        "questions": ["原问题一？", "原问题二？", "原问题三？"],
    }
    return {
        "id": PLAN_ID,
        "class_id": CLASS_ID,
        "semester_id": SEMESTER_ID,
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
        "content": content,
        "content_schema_version": 1,
        "version": 1,
        "authors": [
            {
                "user_id": TEACHER_ID,
                "sort_order": 0,
                "display_name_snapshot": "测试教师",
            }
        ],
        "soft_warnings": [],
        "capabilities": ["plans:view", "plans:edit", "plans:archive"],
        "archived_at": None,
    }


def _job(
    *,
    job_id: str,
    status: str,
    target_section: str,
    error_code: str | None = None,
) -> dict[str, object]:
    return {
        "id": job_id,
        "job_type": f"ai.{target_section}",
        "status": status,
        "parent_job_id": None,
        "retry_of_job_id": None,
        "plan_id": PLAN_ID,
        "target_section": target_section,
        "requested_resource_version": 1,
        "attempt_count": 3 if status == "failed" else 1,
        "max_attempts": 3,
        "trace_id": str(uuid4()),
        "created_at": datetime.now(UTC).isoformat(),
        "queued_at": None,
        "started_at": None,
        "finished_at": datetime.now(UTC).isoformat() if status == "failed" else None,
        "error_code": error_code,
        "error_message": "生成失败" if error_code else None,
        "has_partial_failure": False,
        "poll_after_ms": 1500,
        "children": [],
    }


@pytest.mark.asyncio
async def test_generation_autosaves_before_submit_and_renders_accessible_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pages = import_module("apps.web.pages.plans")
    monkeypatch.setattr(pages, "AUTOSAVE_DELAY_SECONDS", 0.01)
    plan = _plan()
    calls: list[tuple[str, str]] = []
    accepted_job = _job(
        job_id="00000000-0000-0000-0000-000000000011",
        status="pending_dispatch",
        target_section="morning_talk",
    )

    async def fake_request(
        path: str,
        *,
        method: str = "GET",
        payload: dict[str, object] | None = None,
        **_kwargs: object,
    ) -> dict[str, object]:
        calls.append((path, method))
        if path.endswith("/jobs"):
            return {
                "ok": True,
                "status": 200,
                "body": {"items": [], "page": 1, "page_size": 20, "total": 0},
            }
        if path.endswith("/autosave"):
            assert payload is not None
            plan["content"] = payload["content"]
            version = plan["version"]
            assert isinstance(version, int)
            plan["version"] = version + 1
            return {"ok": True, "status": 200, "body": dict(plan)}
        if path.endswith("/ai/generations"):
            assert payload is not None
            assert payload["expected_version"] == plan["version"]
            assert payload["task_code"] == "morning_talk"
            assert payload["teacher_context"] == "围绕春天"
            return {"ok": True, "status": 202, "body": {"job": accepted_job}}
        return {"ok": True, "status": 200, "body": dict(plan)}

    monkeypatch.setattr(pages, "plan_api_request", fake_request)

    async with user_simulation(root=lambda: pages.build_plan_editor_page(PLAN_ID)) as user:
        await user.open("/")
        context_input = next(
            field
            for field in user.find(ui.input).elements
            if field.props.get("label") == "本次生成补充"
        )
        context = UserInteraction(user, {context_input}, "本次生成补充")
        context.trigger("focus").type("围绕春天")
        generate_button = next(
            button for button in user.find(ui.button).elements if "生成晨间谈话" in str(button.text)
        )
        UserInteraction(user, {generate_button}, "生成晨间谈话").trigger(
            "keydown.enter",
            {"key": "Enter"},
        )
        await user.should_see("等待投递")

        autosave_index = calls.index((f"/{PLAN_ID}/autosave", "PUT"))
        generation_index = calls.index((f"/{PLAN_ID}/ai/generations", "POST"))
        assert autosave_index < generation_index
        status = next(
            label
            for label in user.find(ui.label).elements
            if label.props.get("role") == "status" and "等待投递" in str(label.text)
        )
        assert status.props.get("aria-live") == "polite"
        assert generate_button.props.get("aria-label")
        assert "min-h-[44px]" in generate_button.classes
        assert context_input.enabled


@pytest.mark.asyncio
async def test_reload_restores_preview_reject_keeps_original_and_failed_column_retries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pages = import_module("apps.web.pages.plans")
    plan = _plan()
    preview_job_id = "00000000-0000-0000-0000-000000000021"
    failed_job_id = "00000000-0000-0000-0000-000000000022"
    preview_job = _job(
        job_id=preview_job_id,
        status="awaiting_confirmation",
        target_section="morning_talk",
    )
    failed_job = _job(
        job_id=failed_job_id,
        status="failed",
        target_section="morning_activity",
        error_code="ai.timeout",
    )
    calls: list[tuple[str, str]] = []

    async def fake_request(
        path: str,
        *,
        method: str = "GET",
        **_kwargs: object,
    ) -> dict[str, object]:
        calls.append((path, method))
        if path.endswith("/jobs"):
            return {
                "ok": True,
                "status": 200,
                "body": {
                    "items": [preview_job, failed_job],
                    "page": 1,
                    "page_size": 20,
                    "total": 2,
                },
            }
        if path.endswith(f"/jobs/{preview_job_id}/preview"):
            return {
                "ok": True,
                "status": 200,
                "body": {
                    "job_id": preview_job_id,
                    "target_section": "morning_talk",
                    "result_schema_code": "prompt.morning_talk.v1",
                    "result_schema_version": 1,
                    "output_content": {
                        "topic": "AI 预览",
                        "questions": ["预览一？", "预览二？", "预览三？"],
                    },
                    "expires_at": "2026-04-01T00:00:00Z",
                    "warnings": [],
                },
            }
        if path.endswith(f"/jobs/{preview_job_id}/reject"):
            return {
                "ok": True,
                "status": 200,
                "body": preview_job | {"status": "rejected"},
            }
        if path.endswith(f"/jobs/{failed_job_id}/retry"):
            return {
                "ok": True,
                "status": 202,
                "body": {
                    "job": _job(
                        job_id="00000000-0000-0000-0000-000000000023",
                        status="pending_dispatch",
                        target_section="morning_activity",
                    )
                },
            }
        return {"ok": True, "status": 200, "body": dict(plan)}

    monkeypatch.setattr(pages, "plan_api_request", fake_request)

    for visit in range(2):
        async with user_simulation(root=lambda: pages.build_plan_editor_page(PLAN_ID)) as user:
            await user.open("/")
            await user.should_see("AI 预览")
            await user.should_see("预览待确认")
            talk = next(
                field
                for field in user.find(ui.textarea).elements
                if field.props.get("label") == "晨间谈话"
            )
            assert "教师原文" in str(talk.value)

            if visit == 0:
                reject_button = next(
                    button
                    for button in user.find(ui.button).elements
                    if "保留原内容" in str(button.text)
                )
                retry_button = next(
                    button
                    for button in user.find(ui.button).elements
                    if "重试失败栏目" in str(button.text)
                )
                UserInteraction(user, {reject_button}, "保留原内容").trigger(
                    "keydown.enter",
                    {"key": "Enter"},
                )
                UserInteraction(user, {retry_button}, "重试失败栏目").trigger(
                    "keydown.enter",
                    {"key": "Enter"},
                )
                await user.should_see("等待投递")
                assert "教师原文" in str(talk.value)
                assert talk.enabled

    assert sum(path.endswith("/jobs") and method == "GET" for path, method in calls) == 2
    assert (f"/jobs/{preview_job_id}/reject", "POST") in calls
    assert (f"/jobs/{failed_job_id}/retry", "POST") in calls
