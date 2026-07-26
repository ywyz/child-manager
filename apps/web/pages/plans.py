"""不依赖 AI 的一日活动计划日历、列表与六栏目编辑页。"""

import asyncio
import json
from datetime import date
from typing import Any

from nicegui import ui

from apps.web.api_client import plan_api_request, same_origin_api_request
from apps.web.components.plan_editor import AUTOSAVE_DELAY_SECONDS, SECTION_LABELS
from apps.web.components.save_status import SaveState, save_status


def plan_page_text() -> tuple[str, ...]:
    return (
        "教案",
        "日历视图",
        "列表视图",
        *SECTION_LABELS.values(),
        "保存",
        "归档",
        "恢复归档",
        "历史版本",
    )


def register_plan_pages() -> None:
    @ui.page("/plans")
    def plans_page() -> None:
        ui.label("教案").classes("text-h5")
        ui.label("日历视图")
        ui.label("列表视图")
        class_select = ui.select({}, label="班级").props('aria-label="班级"')
        plan_date = ui.input("活动日期", value=date.today().isoformat()).props(
            'type=date aria-label="活动日期"'
        )
        list_container = ui.column()
        status = ui.label("")

        async def load() -> None:
            classes = await same_origin_api_request("/api/v1/settings/classes?page=1&page_size=100")
            body = classes.get("body", {})
            if isinstance(body, dict):
                options = {
                    str(item["id"]): str(item["name"])
                    for item in body.get("items", [])
                    if isinstance(item, dict) and item.get("id") and item.get("name")
                }
                class_select.options = options
                class_select.update()
                if options and class_select.value is None:
                    class_select.value = next(iter(options))
            plans = await plan_api_request("?page=1&page_size=100")
            plans_body = plans.get("body", {})
            if isinstance(plans_body, dict):
                with list_container:
                    for item in plans_body.get("items", []):
                        if isinstance(item, dict) and item.get("id"):
                            label = (
                                f"{item.get('plan_date', '')} {item.get('class_name_snapshot', '')}"
                            )
                            ui.link(label, f"/plans/{item['id']}")
            if not classes.get("ok") or not plans.get("ok"):
                status.set_text("教案列表读取失败")

        async def open_plan() -> None:
            if not class_select.value or not plan_date.value:
                status.set_text("请选择班级和活动日期")
                return
            result = await plan_api_request(
                "/open",
                method="POST",
                payload={
                    "class_id": str(class_select.value),
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
        ui.timer(0.1, load, once=True)

    @ui.page("/plans/{plan_id}")
    def plan_editor_page(plan_id: str) -> None:
        ui.label("教案").classes("text-h5")
        context = ui.label("")
        warnings = ui.column()
        state_label = ui.label(save_status("idle").text).props('role="status" aria-live="polite"')
        fields: dict[str, Any] = {}
        current: dict[str, Any] = {}
        debounce_generation = [0]
        pending_autosaves: set[asyncio.Task[None]] = set()

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
                set_state("saved")
            elif result.get("status") == 409:
                set_state("conflict")
            else:
                set_state("failed")

        async def autosave_after_delay(generation: int) -> None:
            await asyncio.sleep(AUTOSAVE_DELAY_SECONDS)
            if generation == debounce_generation[0]:
                await save(explicit=False)

        def changed() -> None:
            debounce_generation[0] += 1
            task = asyncio.create_task(autosave_after_delay(debounce_generation[0]))
            pending_autosaves.add(task)
            task.add_done_callback(pending_autosaves.discard)

        ui.label("六栏目编辑器").props('role="heading" aria-level="2"')
        for key, label in SECTION_LABELS.items():
            fields[key] = (
                ui.textarea(label)
                .props(f'aria-label="{label}" aria-describedby="plan-save-status"')
                .classes("w-full")
                .on("change", changed)
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
            with warnings:
                for warning in body.get("soft_warnings", []):
                    if isinstance(warning, dict):
                        ui.label(str(warning.get("message", ""))).props('role="alert"')
            readonly = "plans:edit" not in body.get("capabilities", [])
            for field in fields.values():
                field.set_enabled(not readonly)
            set_state("saved")

        async def explicit_save() -> None:
            await save(explicit=True)

        async def archive() -> None:
            if not current:
                return
            action = "unarchive" if current.get("archived_at") else "archive"
            result = await plan_api_request(
                f"/{plan_id}/{action}",
                method="POST",
                payload={"expected_version": current["version"]},
            )
            body = result.get("body", {})
            if result.get("ok") and isinstance(body, dict):
                current.update(body)
                set_state("saved")
            else:
                set_state("failed")

        async def show_history() -> None:
            result = await plan_api_request(f"/{plan_id}/snapshots?page=1&page_size=100")
            body = result.get("body", {})
            if isinstance(body, dict):
                with history:
                    history.clear()
                    for snapshot in body.get("items", []):
                        if isinstance(snapshot, dict):
                            ui.label(
                                f"{snapshot.get('created_at', '')} "
                                f"{snapshot.get('reason_code', '')}"
                            )
                            snapshot_id = snapshot.get("id")
                            if snapshot_id and "plans:edit" in current.get("capabilities", []):

                                async def restore(
                                    target: str = str(snapshot_id),
                                ) -> None:
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
                                        set_state("saved")
                                        await show_history()
                                    elif result.get("status") == 409:
                                        set_state("conflict")
                                    else:
                                        set_state("failed")

                                ui.button("恢复此版本", on_click=restore).classes("min-h-[44px]")

        ui.button("保存", on_click=explicit_save).classes("min-h-[44px]")
        ui.button("归档", on_click=archive).classes("min-h-[44px]")
        ui.button("恢复归档", on_click=archive).classes("min-h-[44px]")
        ui.button("历史版本", on_click=show_history).classes("min-h-[44px]")
        history = ui.column()
        ui.timer(0.1, load, once=True)
