from importlib import import_module
from typing import Any

import pytest

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
        "保存模型档案",
        "启用模型",
        "提示词草稿",
        "发布新版本",
        "历史版本",
        "恢复为新版本",
        "运行异步测试",
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
