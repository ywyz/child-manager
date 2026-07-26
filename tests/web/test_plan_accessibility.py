from importlib import import_module


def test_plan_editor_accessibility_contract_has_labels_focus_and_touch_targets() -> None:
    editor = import_module("apps.web.components.plan_editor")

    contract = editor.accessibility_contract()
    assert contract["keyboard_order"] == (
        "班级",
        "活动日期",
        "六栏目编辑器",
        "保存",
        "归档",
        "历史版本",
    )
    assert contract["errors_are_labelled"] is True
    assert contract["status_uses_text"] is True
    assert contract["minimum_touch_target_px"] >= 44
