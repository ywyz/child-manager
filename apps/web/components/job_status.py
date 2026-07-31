"""异步提示词测试的稳定中文状态与无障碍语义。"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PromptTestStatus:
    message: str
    action_label: str | None
    can_retry: bool


@dataclass(frozen=True, slots=True)
class AiJobStatus:
    message: str
    can_retry: bool = False
    can_decide: bool = False


def should_poll(status: str) -> bool:
    return status in {"pending_dispatch", "queued", "running", "retrying"}


def poll_interval_ms(status: str) -> int:
    del status
    return 1500


def prompt_test_status(payload: dict[str, object]) -> PromptTestStatus:
    status = str(payload.get("status", "pending_dispatch"))
    error_code = str(payload.get("error_code") or "")
    if error_code == "prompt.configuration_changed":
        return PromptTestStatus("模型调用配置已变化，请重新测试。", "重新测试", True)
    if status == "succeeded":
        return PromptTestStatus("测试完成。", None, False)
    if status == "failed":
        return PromptTestStatus("测试失败，请检查配置后重试。", "重新测试", True)
    return PromptTestStatus("AI 正在生成，请稍候。", None, False)


def ai_job_status(payload: dict[str, object]) -> AiJobStatus:
    status = str(payload.get("status", "pending_dispatch"))
    if status == "pending_dispatch":
        return AiJobStatus("等待投递")
    if status in {"queued", "running"}:
        return AiJobStatus("AI 正在生成，请稍候")
    if status == "retrying":
        return AiJobStatus("生成失败，正在重试")
    if status == "awaiting_confirmation":
        return AiJobStatus("预览待确认", can_decide=True)
    if status == "failed":
        return AiJobStatus("生成失败", can_retry=True)
    if status == "adopted":
        return AiJobStatus("已采用")
    if status == "rejected":
        return AiJobStatus("已保留原内容")
    if status == "expired":
        return AiJobStatus("预览已过期")
    return AiJobStatus("任务状态未知")


def ai_prompt_accessibility_semantics() -> dict[str, dict[str, object]]:
    return {
        "api_key_input": {
            "label": "API Key（仅写入）",
            "error_id": "ai-api-key-error",
        },
        "test_button": {"keyboard_activatable": True},
        "test_status": {"aria_live": "polite"},
    }
