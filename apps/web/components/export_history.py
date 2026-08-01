"""Word 导出历史的中文状态与独立列表组件。"""

from collections.abc import Awaitable, Callable
from typing import Any

from nicegui import ui

REQUIRED_SECTION_LABELS = {
    "morning_activity": "晨间活动",
    "morning_talk": "晨间谈话",
    "indoor_area_game": "室内区域游戏",
    "group_activity": "集体活动",
    "afternoon_outdoor_game": "下午户外游戏",
}

_STATUS_TEXT = {
    "pending": "等待导出",
    "succeeded": "导出成功",
    "failed": "导出失败，请重试",
}


def missing_section_labels(section_codes: list[object]) -> list[str]:
    """把服务端前五栏代码映射为稳定中文，不把反思纳入确认。"""

    return [
        REQUIRED_SECTION_LABELS[code]
        for value in section_codes
        if (code := str(value)) in REQUIRED_SECTION_LABELS
    ]


def is_terminal_export_status(status: object) -> bool:
    return str(status) in {"succeeded", "failed"}


def render_export_history(
    container: Any,
    *,
    items: list[dict[str, object]],
    on_download: Callable[[str], Awaitable[None]],
) -> None:
    """独立渲染每次导出，成功记录可重复下载。"""

    container.clear()
    with container:
        ui.label(f"共 {len(items)} 次导出")
        for item in items:
            export_id = str(item.get("id", ""))
            status = str(item.get("status", "pending"))
            with ui.card().classes("w-full"):
                ui.label(str(item.get("display_filename", "")))
                ui.label(_STATUS_TEXT.get(status, "等待导出")).props(
                    'role="status" aria-live="polite"'
                )
                if status != "succeeded" or not export_id:
                    continue

                async def download(target: str = export_id) -> None:
                    await on_download(target)

                button = (
                    ui.button("下载", on_click=download)
                    .props('aria-label="下载 Word"')
                    .classes("min-h-[44px]")
                )
                button.on("keydown.enter", download)
