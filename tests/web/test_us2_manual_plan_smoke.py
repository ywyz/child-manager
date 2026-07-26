from importlib import import_module


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
