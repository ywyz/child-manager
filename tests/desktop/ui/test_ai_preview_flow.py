from __future__ import annotations

from uuid import UUID

from tests.desktop.helpers import pending_module, pending_symbol


def _flow():
    module = pending_module("kindergarten_manager.ui.widgets.ai_preview")
    flow_type = pending_symbol(module, "AiPreviewFlow")
    return flow_type()


def test_ai_entry_is_optional_and_unconfigured_state_does_not_block_manual_flow() -> None:
    flow = _flow()

    assert flow.entry_visible is True
    assert flow.generation_enabled is False
    assert flow.status_text == "未配置 AI，可继续手工编辑和导出"


def test_duplicate_start_shows_fixed_single_operation_message() -> None:
    flow = _flow()
    flow.configure(enabled=True)
    operation_id = UUID(int=1)
    flow.mark_started(operation_id)

    assert not flow.request_start("morning_talk")
    assert flow.status_text == "AI 正在生成，请稍候"
    assert flow.notice_text == "已有 AI 任务正在运行"


def test_per_section_preview_failure_and_retry_remain_independent() -> None:
    flow = _flow()
    flow.configure(enabled=True)
    operation_id = UUID(int=2)
    flow.mark_started(operation_id)
    flow.show_preview(operation_id, "morning_talk", "preview-1", {"topic": "春天"})
    flow.show_failure(operation_id, "morning_activity", "生成失败")

    assert flow.preview_for("morning_talk").can_adopt
    assert flow.failure_for("morning_activity").can_retry
    assert flow.request_retry("morning_activity") == "morning_activity"
    assert flow.preview_for("morning_talk").preview_id == "preview-1"


def test_adopt_and_reject_emit_only_explicit_preview_intents() -> None:
    flow = _flow()
    operation_id = UUID(int=3)
    flow.configure(enabled=True)
    flow.mark_started(operation_id)
    flow.show_preview(operation_id, "morning_talk", "preview-2", {"topic": "春天"})

    assert flow.request_adopt("preview-2") == ("adopt", "preview-2")
    assert flow.request_reject("preview-2") == ("reject", "preview-2")
    assert flow.preview_for("morning_talk").status == "ready"


def test_page_change_invalidates_epoch_and_discards_late_signal() -> None:
    flow = _flow()
    operation_id = UUID(int=4)
    flow.configure(enabled=True)
    epoch = flow.page_epoch
    flow.mark_started(operation_id)

    flow.leave_page()
    flow.show_preview(
        operation_id,
        "morning_talk",
        "late-preview",
        {"topic": "迟到"},
        page_epoch=epoch,
    )

    assert flow.page_epoch != epoch
    assert flow.preview_for("morning_talk") is None
