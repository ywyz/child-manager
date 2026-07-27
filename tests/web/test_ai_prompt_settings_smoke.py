import asyncio
from importlib import import_module
from typing import Any

import pytest
from nicegui.testing.user_simulation import user_simulation

from apps.web.pages import settings as settings_page


def _job_status_module() -> Any:
    try:
        return import_module("apps.web.components.job_status")
    except ModuleNotFoundError:
        pytest.fail("T085 尚未提供异步任务状态组件", pytrace=False)


def test_settings_page_exposes_model_and_prompt_admin_flows() -> None:
    assert {
        "AI 模型档案",
        "提示词中心",
        "API Key（仅写入）",
        "外部数据处理风险",
        "模型能力",
        "最大并发",
        "保存模型档案",
        "启用模型",
        "停用模型",
        "提示词草稿",
        "发布新版本",
        "历史版本",
        "恢复为新版本",
        "运行异步测试",
        "恢复任务状态",
        "重新测试",
        "最近 20 条测试记录",
    } <= set(settings_page.settings_page_text())


def test_key_is_masked_and_never_rendered_as_an_editable_value() -> None:
    assert settings_page.masked_api_key_text("••••alue") == "已配置：••••alue"
    assert "secret" not in settings_page.masked_api_key_text("••••cret").lower()


def test_job_status_recovers_configuration_change_with_chinese_action() -> None:
    module = _job_status_module()
    state = module.prompt_test_status(
        {
            "status": "failed",
            "error_code": "prompt.configuration_changed",
            "error_summary": "provider details must stay hidden",
        }
    )
    assert state.message == "模型调用配置已变化，请重新测试。"
    assert state.action_label == "重新测试"
    assert state.can_retry is True


def test_job_status_refreshes_until_terminal_and_restores_after_page_reload() -> None:
    module = _job_status_module()
    assert module.should_poll("pending_dispatch") is True
    assert module.should_poll("queued") is True
    assert module.should_poll("running") is True
    assert module.should_poll("succeeded") is False
    assert module.should_poll("failed") is False
    assert module.poll_interval_ms("pending_dispatch") in range(1000, 2001)


def test_controls_have_keyboard_focus_and_error_label_associations() -> None:
    module = _job_status_module()
    semantics = module.ai_prompt_accessibility_semantics()
    assert semantics["api_key_input"]["label"] == "API Key（仅写入）"
    assert semantics["api_key_input"]["error_id"] == "ai-api-key-error"
    assert semantics["test_button"]["keyboard_activatable"] is True
    assert semantics["test_status"]["aria_live"] == "polite"


@pytest.mark.asyncio
async def test_settings_controls_call_model_prompt_and_job_public_api_seams(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, str, dict[str, str] | None]] = []

    async def fake_request(
        path: str,
        *,
        method: str = "GET",
        payload: dict[str, object] | None = None,
        request_headers: dict[str, str] | None = None,
    ) -> dict[str, object]:
        del payload
        calls.append((path, method, request_headers))
        if path.startswith("/api/v1/settings/ai-model-profiles?"):
            return {
                "ok": True,
                "status": 200,
                "body": {
                    "items": [
                        {
                            "id": "01900000-0000-7000-8000-000000000001",
                            "name": "测试模型",
                            "api_base_url": "https://ai.example.test/v1",
                            "model_name": "model",
                            "api_key_masked": "••••cret",
                        }
                    ]
                },
            }
        if path.startswith("/api/v1/prompts?"):
            return {
                "ok": True,
                "status": 200,
                "body": {
                    "items": [
                        {
                            "code": "daily_activity_plan.morning_talk",
                            "effective_version_id": "01900000-0000-7000-8000-000000000002",
                        }
                    ]
                },
            }
        if path == "/api/v1/settings/ai-model-profiles":
            return {
                "ok": True,
                "status": 201,
                "body": {"id": "01900000-0000-7000-8000-000000000001"},
            }
        if path.endswith("/tests"):
            return {
                "ok": True,
                "status": 202,
                "body": {
                    "job": {
                        "id": "01900000-0000-7000-8000-000000000003",
                        "status": "succeeded",
                    }
                },
            }
        return {"ok": True, "status": 200, "body": {"id": "version-id"}}

    monkeypatch.setattr(settings_page, "same_origin_api_request", fake_request)

    async with user_simulation(root=settings_page.build_ai_prompt_settings_section) as user:
        await user.open("/")
        await asyncio.sleep(0.15)
        user.find("新建模型档案").click()
        user.find("保存模型档案").click()
        user.find("外部数据处理风险").click()
        user.find("启用模型").click()
        user.find("停用模型").click()
        user.find("发布新版本").click()
        user.find("运行异步测试").click()
        await asyncio.sleep(0.1)

    paths = {(path, method) for path, method, _headers in calls}
    assert ("/api/v1/settings/ai-model-profiles", "POST") in paths
    assert (
        "/api/v1/settings/ai-model-profiles/01900000-0000-7000-8000-000000000001/enable",
        "POST",
    ) in paths
    assert (
        "/api/v1/settings/ai-model-profiles/01900000-0000-7000-8000-000000000001/disable",
        "POST",
    ) in paths
    assert ("/api/v1/prompts/daily_activity_plan.morning_talk/publish", "POST") in paths
    test_call = next(item for item in calls if item[0].endswith("/tests"))
    assert test_call[2] is not None
    assert test_call[2]["Idempotency-Key"].startswith("web-prompt-test-")
