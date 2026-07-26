"""不依赖 AI 的一日活动计划日历、列表与六栏目编辑页。"""

import asyncio
import json
from datetime import date
from typing import Any
from urllib.parse import urlencode

from nicegui import ui

from apps.web.api_client import plan_api_request, same_origin_api_request
from apps.web.components.plan_editor import AUTOSAVE_DELAY_SECONDS, SECTION_LABELS
from apps.web.components.save_status import SaveState, save_status


def plan_page_text() -> tuple[str, ...]:
    return (
        "教案",
        "日历视图",
        "列表视图",
        "日期范围开始",
        "日期范围结束",
        "编写教师",
        "归档状态",
        *SECTION_LABELS.values(),
        "保存",
        "归档",
        "恢复归档",
        "历史版本",
    )


def build_plans_page() -> None:
    """构建可由真实服务或 NiceGUI 用户模拟器调用的教案首页。"""

    ui.label("教案").classes("text-h5")
    ui.label("打开或创建教案").classes("text-subtitle1")
    open_class_select = ui.select({}, label="班级").props('aria-label="班级"')
    plan_date = ui.input("活动日期", value=date.today().isoformat()).props(
        'type=date aria-label="活动日期"'
    )
    status = ui.label("").props('role="status" aria-live="polite"')

    async def open_plan() -> None:
        if not open_class_select.value or not plan_date.value:
            status.set_text("请选择班级和活动日期")
            return
        result = await plan_api_request(
            "/open",
            method="POST",
            payload={
                "class_id": str(open_class_select.value),
                "plan_date": str(plan_date.value),
            },
        )
        body = result.get("body", {})
        if result.get("ok") and isinstance(body, dict) and body.get("id"):
            ui.navigate.to(f"/plans/{body['id']}")
        else:
            status.set_text(
                str(body.get("message", "打开教案失败"))
                if isinstance(body, dict)
                else "打开教案失败"
            )

    ui.button("打开或创建教案", on_click=open_plan).classes("min-h-[44px]")
    ui.separator()
    ui.label("筛选教案").classes("text-subtitle1")
    with ui.row().classes("items-end w-full"):
        filter_class = ui.select({}, label="筛选班级").props('clearable aria-label="筛选班级"')
        date_from = ui.input("日期范围开始").props('type=date clearable aria-label="日期范围开始"')
        date_to = ui.input("日期范围结束").props('type=date clearable aria-label="日期范围结束"')
        author_select = ui.select({}, label="编写教师").props('clearable aria-label="编写教师"')
        archived_select = ui.select(
            {
                "all": "全部",
                "active": "未归档",
                "archived": "已归档",
            },
            value="all",
            label="归档状态",
        ).props('aria-label="归档状态"')

    with ui.tabs() as tabs:
        calendar_tab = ui.tab("日历视图")
        list_tab = ui.tab("列表视图")
    with ui.tab_panels(tabs, value=calendar_tab).classes("w-full"):
        with ui.tab_panel(calendar_tab):
            calendar_container = ui.grid(columns=4).classes("w-full")
        with ui.tab_panel(list_tab):
            list_container = ui.column().classes("w-full")

    def query_path() -> str:
        parameters: dict[str, str | int] = {"page": 1, "page_size": 100}
        if filter_class.value:
            parameters["class_id"] = str(filter_class.value)
        if date_from.value:
            parameters["date_from"] = str(date_from.value)
        if date_to.value:
            parameters["date_to"] = str(date_to.value)
        if author_select.value:
            parameters["author_id"] = str(author_select.value)
        if archived_select.value == "active":
            parameters["archived"] = "false"
        elif archived_select.value == "archived":
            parameters["archived"] = "true"
        return f"?{urlencode(parameters)}"

    async def load_plans() -> None:
        result = await plan_api_request(query_path())
        body = result.get("body", {})
        if not result.get("ok") or not isinstance(body, dict):
            status.set_text("教案列表读取失败")
            return
        items = [item for item in body.get("items", []) if isinstance(item, dict)]
        author_options = (
            dict(author_select.options) if isinstance(author_select.options, dict) else {}
        )
        for item in items:
            for author in item.get("authors", []):
                if (
                    isinstance(author, dict)
                    and author.get("user_id")
                    and author.get("display_name_snapshot")
                ):
                    author_options[str(author["user_id"])] = str(author["display_name_snapshot"])
        author_select.options = author_options
        author_select.update()

        calendar_container.clear()
        list_container.clear()
        with calendar_container:
            if not items:
                ui.label("没有符合条件的教案")
            for item in sorted(items, key=lambda value: str(value.get("plan_date", ""))):
                if not item.get("id"):
                    continue
                with ui.card().classes("w-full"):
                    ui.label(str(item.get("plan_date", ""))).classes("text-subtitle2")
                    ui.link(
                        str(item.get("class_name_snapshot", "")),
                        f"/plans/{item['id']}",
                    )
                    if item.get("archived_at"):
                        ui.label("已归档")
        with list_container:
            if not items:
                ui.label("没有符合条件的教案")
            for item in items:
                if not item.get("id"):
                    continue
                label = f"{item.get('plan_date', '')} {item.get('class_name_snapshot', '')}"
                if item.get("archived_at"):
                    label += "（已归档）"
                ui.link(label, f"/plans/{item['id']}")
        status.set_text(f"共 {body.get('total', len(items))} 份教案")

    async def load() -> None:
        classes = await same_origin_api_request("/api/v1/settings/classes?page=1&page_size=100")
        body = classes.get("body", {})
        if not classes.get("ok") or not isinstance(body, dict):
            status.set_text("班级读取失败")
            return
        options = {
            str(item["id"]): str(item["name"])
            for item in body.get("items", [])
            if isinstance(item, dict) and item.get("id") and item.get("name")
        }
        for select in (open_class_select, filter_class):
            select.options = options
            select.update()
        if options and open_class_select.value is None:
            open_class_select.value = next(iter(options))
        await load_plans()

    ui.button("应用筛选", on_click=load_plans).classes("min-h-[44px]")
    ui.timer(0.1, load, once=True)


def build_plan_editor_page(plan_id: str) -> None:
    """构建教案编辑页，并让归档能力变化立即反映到控件。"""

    ui.label("教案").classes("text-h5")
    context = ui.label("")
    warnings = ui.column()
    state_label = ui.label(save_status("idle").text).props('role="status" aria-live="polite"')
    fields: dict[str, Any] = {}
    current: dict[str, Any] = {}
    debounce_generation = [0]
    pending_autosave: list[asyncio.Task[None] | None] = [None]

    def set_state(state: SaveState) -> None:
        value = save_status(state)
        state_label.set_text(value.text)
        state_label.classes(replace=value.css_class)

    def editor_content() -> dict[str, object] | None:
        content: dict[str, object] = {}
        for key, field in fields.items():
            try:
                parsed = json.loads(str(field.value or "{}"))
            except json.JSONDecodeError:
                set_state("failed")
                return None
            if not isinstance(parsed, dict):
                set_state("failed")
                return None
            content[key] = parsed
        return content

    def apply_capabilities() -> None:
        capabilities = set(current.get("capabilities", []))
        archived = current.get("archived_at") is not None
        editable = "plans:edit" in capabilities and not archived
        can_archive = "plans:archive" in capabilities
        for field in fields.values():
            field.set_enabled(editable)
        save_button.set_enabled(editable)
        archive_button.set_visibility(can_archive and not archived)
        unarchive_button.set_visibility(can_archive and archived)

    async def save(*, explicit: bool) -> None:
        content = editor_content()
        if content is None or not current:
            return
        set_state("saving")
        result = await plan_api_request(
            f"/{plan_id}/{'save' if explicit else 'autosave'}",
            method="PUT",
            payload={
                "expected_version": current["version"],
                "content": content,
                "authors": [
                    {
                        "user_id": author["user_id"],
                        "sort_order": author["sort_order"],
                    }
                    for author in current.get("authors", [])
                ],
            },
        )
        body = result.get("body", {})
        if result.get("ok") and isinstance(body, dict):
            current.update(body)
            apply_capabilities()
            set_state("saved")
        elif result.get("status") == 409:
            set_state("conflict")
        else:
            set_state("failed")

    async def autosave_after_delay(generation: int) -> None:
        try:
            await asyncio.sleep(AUTOSAVE_DELAY_SECONDS)
        except asyncio.CancelledError:
            return
        if generation == debounce_generation[0]:
            await save(explicit=False)

    def changed() -> None:
        debounce_generation[0] += 1
        if pending_autosave[0] is not None:
            pending_autosave[0].cancel()
        pending_autosave[0] = asyncio.create_task(autosave_after_delay(debounce_generation[0]))

    ui.label("六栏目编辑器").props('role="heading" aria-level="2"')
    for key, label in SECTION_LABELS.items():
        fields[key] = (
            ui.textarea(label)
            .props(f'aria-label="{label}" aria-describedby="plan-save-status"')
            .classes("w-full")
            .on("input", changed)
        )
    state_label.props('id="plan-save-status"')

    async def load() -> None:
        result = await plan_api_request(f"/{plan_id}")
        body = result.get("body", {})
        if not result.get("ok") or not isinstance(body, dict):
            set_state("failed")
            return
        current.update(body)
        context.set_text(
            " · ".join(
                str(body.get(key, ""))
                for key in (
                    "kindergarten_name_snapshot",
                    "class_name_snapshot",
                    "semester_name_snapshot",
                    "activity_date_text",
                    "teaching_week_text",
                )
                if body.get(key)
            )
        )
        content = body.get("content", {})
        if isinstance(content, dict):
            for key, field in fields.items():
                field.value = json.dumps(content.get(key, {}), ensure_ascii=False, indent=2)
        warnings.clear()
        with warnings:
            for warning in body.get("soft_warnings", []):
                if isinstance(warning, dict):
                    ui.label(str(warning.get("message", ""))).props('role="alert"')
        apply_capabilities()
        set_state("saved")

    async def explicit_save() -> None:
        await save(explicit=True)

    async def set_archived(*, archived: bool) -> None:
        if not current:
            return
        action = "archive" if archived else "unarchive"
        result = await plan_api_request(
            f"/{plan_id}/{action}",
            method="POST",
            payload={"expected_version": current["version"]},
        )
        body = result.get("body", {})
        if result.get("ok") and isinstance(body, dict):
            current.update(body)
            apply_capabilities()
            set_state("saved")
        elif result.get("status") == 409:
            set_state("conflict")
        else:
            set_state("failed")

    async def show_history() -> None:
        result = await plan_api_request(f"/{plan_id}/snapshots?page=1&page_size=100")
        body = result.get("body", {})
        if not isinstance(body, dict):
            return
        history.clear()
        with history:
            for snapshot in body.get("items", []):
                if not isinstance(snapshot, dict):
                    continue
                ui.label(f"{snapshot.get('created_at', '')} {snapshot.get('reason_code', '')}")
                snapshot_id = snapshot.get("id")
                if not snapshot_id or "plans:edit" not in current.get("capabilities", []):
                    continue

                async def restore(target: str = str(snapshot_id)) -> None:
                    result = await plan_api_request(
                        f"/{plan_id}/snapshots/{target}/restore",
                        method="POST",
                        payload={"expected_version": current["version"]},
                    )
                    restored = result.get("body", {})
                    if result.get("ok") and isinstance(restored, dict):
                        current.update(restored)
                        content = restored.get("content", {})
                        if isinstance(content, dict):
                            for key, field in fields.items():
                                field.value = json.dumps(
                                    content.get(key, {}),
                                    ensure_ascii=False,
                                    indent=2,
                                )
                        apply_capabilities()
                        set_state("saved")
                        await show_history()
                    elif result.get("status") == 409:
                        set_state("conflict")
                    else:
                        set_state("failed")

                ui.button("恢复此版本", on_click=restore).classes("min-h-[44px]")

    save_button = ui.button("保存", on_click=explicit_save).classes("min-h-[44px]")
    archive_button = ui.button(
        "归档",
        on_click=lambda: set_archived(archived=True),
    ).classes("min-h-[44px]")
    unarchive_button = ui.button(
        "恢复归档",
        on_click=lambda: set_archived(archived=False),
    ).classes("min-h-[44px]")
    ui.button("历史版本", on_click=show_history).classes("min-h-[44px]")
    history = ui.column()
    ui.timer(0.1, load, once=True)


def register_plan_pages() -> None:
    ui.page("/plans")(build_plans_page)
    ui.page("/plans/{plan_id}")(build_plan_editor_page)
