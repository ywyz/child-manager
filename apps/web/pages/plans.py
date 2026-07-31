"""不依赖 AI 的一日活动计划日历、列表与六栏目编辑页。"""

import asyncio
import json
from datetime import date
from typing import Any
from urllib.parse import urlencode
from uuid import uuid4

from nicegui import ui

from apps.web.api_client import plan_api_request, plan_docx_preview_request, same_origin_api_request
from apps.web.components.ai_preview import AI_SECTION_ACTIONS, preview_title
from apps.web.components.job_status import ai_job_status, poll_interval_ms, should_poll
from apps.web.components.plan_editor import AUTOSAVE_DELAY_SECONDS, SECTION_LABELS
from apps.web.components.save_status import SaveState, save_status


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
    ai_containers: dict[str, Any] = {}
    current: dict[str, Any] = {}
    debounce_generation = [0]
    pending_autosave: list[asyncio.Task[None] | None] = [None]
    polling_jobs: set[str] = set()
    polling_tasks: set[asyncio.Task[None]] = set()
    loaded = asyncio.Event()

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
        source_editor.set_enabled(editable)
        save_button.set_enabled(editable)
        docx_upload.set_enabled(editable)
        docx_preview_text.set_enabled(False)
        docx_confirm = docx_confirm_button[0]
        if docx_confirm is not None:
            docx_confirm.set_enabled(editable and bool(docx_preview))
        archive_button.set_visibility(can_archive and not archived)
        unarchive_button.set_visibility(can_archive and archived)

    async def save(*, explicit: bool) -> bool:
        content = editor_content()
        if content is None or not current:
            return False
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
            return True
        elif result.get("status") == 409:
            set_state("conflict")
        else:
            set_state("failed")
        return False

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
        ai_containers[key] = ui.column().classes("w-full")
    state_label.props('id="plan-save-status"')
    teacher_context = ui.input("本次生成补充").props('aria-label="本次生成补充"').classes("w-full")
    batch_container = ui.column().classes("w-full")
    source_editor = ui.textarea("集体活动原文").props('aria-label="集体活动原文"').classes("w-full")
    docx_preview: dict[str, str] = {}
    docx_preview_text = (
        ui.textarea("DOCX 提取文本").props('aria-label="DOCX 提取文本" readonly').classes("w-full")
    )
    docx_preview_text.set_visibility(False)
    docx_confirm_button: list[Any | None] = [None]
    group_activity_controls = ui.column().classes("w-full")
    add_step_button: list[Any | None] = [None]
    adopted_group_activity_split = [False]

    def group_activity_content() -> dict[str, Any]:
        content = current.get("content", {})
        group_activity = content.get("group_activity", {}) if isinstance(content, dict) else {}
        return group_activity if isinstance(group_activity, dict) else {}

    def group_activity_is_complete(group_activity: dict[str, Any]) -> bool:
        process = group_activity.get("process")
        return (
            all(
                group_activity.get(key)
                for key in ("theme", "objectives", "preparation", "focus", "difficulty")
            )
            and isinstance(process, list)
            and bool(process)
            and all(
                isinstance(step, dict)
                and bool(step.get("heading"))
                and isinstance(step.get("lines"), list)
                and bool(step["lines"])
                for step in process
            )
        )

    def group_activity_has_ai_added(group_activity: dict[str, Any]) -> bool:
        process = group_activity.get("process", [])
        return isinstance(process, list) and any(
            isinstance(step, dict) and step.get("is_ai_added") is True for step in process
        )

    def refresh_group_activity_controls() -> None:
        group_activity = group_activity_content()
        complete = group_activity_is_complete(group_activity)
        has_ai_added = group_activity_has_ai_added(group_activity)
        may_add_step = complete and adopted_group_activity_split[0] and not has_ai_added
        group_activity_controls.clear()
        with group_activity_controls:
            if has_ai_added:
                ui.label("AI 新增环节")

                async def clear_ai_added_marker() -> None:
                    content = editor_content()
                    if content is None:
                        return
                    target = content.get("group_activity")
                    if not isinstance(target, dict):
                        return
                    process = target.get("process")
                    if not isinstance(process, list):
                        return
                    target["process"] = [
                        {**step, "is_ai_added": False}
                        if isinstance(step, dict) and step.get("is_ai_added") is True
                        else step
                        for step in process
                    ]
                    fields["group_activity"].value = json.dumps(
                        target, ensure_ascii=False, indent=2
                    )
                    if await save(explicit=False):
                        refresh_group_activity_controls()

                button = ui.button("取消 AI 新增标记", on_click=clear_ai_added_marker).classes(
                    "min-h-[44px]"
                )
                button.on("keydown.enter", clear_ai_added_marker)
            elif may_add_step:
                ui.label("可新增适龄环节")
            elif complete:
                ui.label("请先采用并保存集体活动拆分结果")
            else:
                ui.label("尚未新增适龄环节")
        editable = (
            "plans:edit" in current.get("capabilities", []) and current.get("archived_at") is None
        )
        button = add_step_button[0]
        if button is not None:
            button.set_enabled(editable and may_add_step)

    def apply_plan_body(body: dict[str, object]) -> None:
        current.update(body)
        content = body.get("content", {})
        if isinstance(content, dict):
            for key, field in fields.items():
                field.value = json.dumps(
                    content.get(key, {}),
                    ensure_ascii=False,
                    indent=2,
                )
        apply_capabilities()
        refresh_group_activity_controls()

    async def render_job(job: dict[str, object]) -> None:
        job_id = str(job.get("id", ""))
        target_section = str(job.get("target_section") or "")
        if job.get("job_type") == "ai.group_activity_split" and job.get("status") == "adopted":
            adopted_group_activity_split[0] = True
            refresh_group_activity_controls()
        is_group_activity = target_section == "group_activity"
        container = ai_containers.get(target_section, batch_container)
        container.clear()
        status_view = ai_job_status(job)
        with container:
            ui.label(status_view.message).props('role="status" aria-live="polite"')
            if is_group_activity and str(job.get("status")) == "failed":
                ui.label("新增环节失败，已采用的拆分结果未变化").props('role="alert"')
        if not job_id:
            return
        if status_view.can_decide:
            preview = await plan_api_request(f"/jobs/{job_id}/preview")
            preview_body = preview.get("body", {})
            if not preview.get("ok") or not isinstance(preview_body, dict):
                return
            output_content = preview_body.get("output_content", {})
            is_group_split = (
                is_group_activity and isinstance(output_content, dict) and "theme" in output_content
            )
            preview_label = "拆分预览" if is_group_split else preview_title(target_section)
            adopt_label = "采用拆分结果" if is_group_split else "采用此预览"
            with container:
                ui.label(preview_label).classes("text-subtitle2")
                ui.label(
                    json.dumps(
                        output_content,
                        ensure_ascii=False,
                        indent=2,
                    )
                ).classes("whitespace-pre-wrap")

                async def adopt() -> None:
                    result = await plan_api_request(
                        f"/jobs/{job_id}/adopt",
                        method="POST",
                        payload={"expected_version": current["version"]},
                    )
                    body = result.get("body", {})
                    if result.get("ok") and isinstance(body, dict):
                        if is_group_split:
                            adopted_group_activity_split[0] = True
                        apply_plan_body(body)
                        await render_job(job | {"status": "adopted"})
                        set_state("saved")
                    elif result.get("status") == 409:
                        set_state("conflict")
                    else:
                        set_state("failed")

                async def reject() -> None:
                    result = await plan_api_request(
                        f"/jobs/{job_id}/reject",
                        method="POST",
                    )
                    body = result.get("body", {})
                    if result.get("ok") and isinstance(body, dict):
                        await render_job(body)
                    else:
                        set_state("failed")

                adopt_button = (
                    ui.button(adopt_label, on_click=adopt)
                    .props(f'aria-label="{adopt_label}"')
                    .classes("min-h-[44px]")
                )
                adopt_button.on("keydown.enter", adopt)
                reject_button = (
                    ui.button("保留原内容", on_click=reject)
                    .props('aria-label="保留原内容"')
                    .classes("min-h-[44px]")
                )
                reject_button.on("keydown.enter", reject)
        elif status_view.can_retry:
            retry_label = "重试新增适龄环节" if is_group_activity else "重试失败栏目"
            with container:

                async def retry() -> None:
                    result = await plan_api_request(
                        f"/jobs/{job_id}/retry",
                        method="POST",
                        request_headers={"Idempotency-Key": str(uuid4())},
                    )
                    body = result.get("body", {})
                    accepted = body.get("job", {}) if isinstance(body, dict) else {}
                    if result.get("ok") and isinstance(accepted, dict):
                        await render_job(accepted)
                    else:
                        set_state("failed")

                retry_button = (
                    ui.button(retry_label, on_click=retry)
                    .props(f'aria-label="{retry_label}"')
                    .classes("min-h-[44px]")
                )
                retry_button.on("keydown.enter", retry)
        elif should_poll(str(job.get("status", ""))) and job_id not in polling_jobs:
            polling_jobs.add(job_id)
            task = asyncio.create_task(poll_job(job_id))
            polling_tasks.add(task)
            task.add_done_callback(polling_tasks.discard)

    async def poll_job(job_id: str) -> None:
        try:
            for _attempt in range(120):
                await asyncio.sleep(poll_interval_ms("pending") / 1000)
                result = await plan_api_request(f"/jobs/{job_id}")
                body = result.get("body", {})
                if not result.get("ok") or not isinstance(body, dict):
                    return
                await render_job(body)
                if not should_poll(str(body.get("status", ""))):
                    return
        finally:
            polling_jobs.discard(job_id)

    async def load_jobs() -> None:
        result = await plan_api_request(f"/{plan_id}/jobs")
        body = result.get("body", {})
        if not result.get("ok") or not isinstance(body, dict):
            return
        has_adopted_split = body.get("has_adopted_group_activity_split")
        if isinstance(has_adopted_split, bool):
            adopted_group_activity_split[0] = has_adopted_split
            refresh_group_activity_controls()
        for item in body.get("items", []):
            if not isinstance(item, dict):
                continue
            if item.get("job_type") == "ai.batch":
                for child in item.get("children", []):
                    if isinstance(child, dict):
                        await render_job(child)
            else:
                await render_job(item)

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
        apply_plan_body(body)
        warnings.clear()
        with warnings:
            for warning in body.get("soft_warnings", []):
                if isinstance(warning, dict):
                    ui.label(str(warning.get("message", ""))).props('role="alert"')
        apply_capabilities()
        set_state("saved")
        loaded.set()
        await load_jobs()

    async def explicit_save() -> None:
        await save(explicit=True)

    async def create_generation(task_code: str, *, source_id: str | None = None) -> None:
        await loaded.wait()
        if not await save(explicit=False):
            return
        payload: dict[str, object] = {
            "task_code": task_code,
            "expected_version": current["version"],
            "teacher_context": str(teacher_context.value or ""),
        }
        if source_id is not None:
            payload["source_id"] = source_id
        result = await plan_api_request(
            f"/{plan_id}/ai/generations",
            method="POST",
            payload=payload,
            request_headers={"Idempotency-Key": str(uuid4())},
        )
        body = result.get("body", {})
        job = body.get("job", {}) if isinstance(body, dict) else {}
        if result.get("ok") and isinstance(job, dict):
            await render_job(job)
        elif result.get("status") == 409:
            set_state("conflict")
        else:
            set_state("failed")

    async def confirm_source_and_split() -> None:
        await loaded.wait()
        source_text = str(source_editor.value or "").strip()
        if not source_text:
            set_state("failed")
            return
        result = await plan_api_request(
            f"/{plan_id}/group-activity-sources/text",
            method="POST",
            payload={"text": source_text},
        )
        body = result.get("body", {})
        source_id = body.get("id") if isinstance(body, dict) else None
        if not result.get("ok") or not source_id:
            set_state("failed")
            return
        await create_generation("group_activity_split", source_id=str(source_id))

    async def preview_docx_source(event: Any) -> None:
        await loaded.wait()
        uploaded = event.file
        result = await plan_docx_preview_request(
            plan_id,
            filename=uploaded.name,
            content_type=uploaded.content_type,
            payload=await uploaded.read(),
        )
        body = result.get("body", {})
        if not result.get("ok") or not isinstance(body, dict):
            set_state("failed")
            return
        original_filename = body.get("original_filename")
        extracted_text = body.get("extracted_text")
        if not isinstance(original_filename, str) or not isinstance(extracted_text, str):
            set_state("failed")
            return
        docx_preview.clear()
        docx_preview.update(
            original_filename=original_filename,
            extracted_text=extracted_text,
        )
        docx_preview_text.value = extracted_text
        docx_preview_text.set_visibility(True)
        apply_capabilities()

    async def confirm_docx_source_and_split() -> None:
        await loaded.wait()
        original_filename = docx_preview.get("original_filename")
        extracted_text = docx_preview.get("extracted_text")
        if not original_filename or not extracted_text:
            set_state("failed")
            return
        result = await plan_api_request(
            f"/{plan_id}/group-activity-sources/docx/confirm",
            method="POST",
            payload={
                "original_filename": original_filename,
                "extracted_text": extracted_text,
            },
        )
        body = result.get("body", {})
        source_id = body.get("id") if isinstance(body, dict) else None
        if not result.get("ok") or not source_id:
            set_state("failed")
            return
        docx_preview.clear()
        docx_preview_text.value = ""
        docx_preview_text.set_visibility(False)
        apply_capabilities()
        await create_generation("group_activity_split", source_id=str(source_id))

    async def create_add_step() -> None:
        await loaded.wait()
        if not adopted_group_activity_split[0] or not group_activity_is_complete(
            group_activity_content()
        ):
            set_state("failed")
            return
        await create_generation("group_activity_add_step")

    async def create_batch() -> None:
        await loaded.wait()
        if not await save(explicit=False):
            return
        result = await plan_api_request(
            f"/{plan_id}/ai/batch",
            method="POST",
            payload={
                "expected_version": current["version"],
                "teacher_context": str(teacher_context.value or ""),
            },
            request_headers={"Idempotency-Key": str(uuid4())},
        )
        body = result.get("body", {})
        job = body.get("job", {}) if isinstance(body, dict) else {}
        if result.get("ok") and isinstance(job, dict):
            await render_job(job)
            for child in job.get("children", []):
                if isinstance(child, dict):
                    await render_job(child)
        else:
            set_state("failed")

    async def create_reflection() -> None:
        await loaded.wait()
        content = editor_content()
        if content is None or not current:
            return
        result = await plan_api_request(
            f"/{plan_id}/ai/generations",
            method="POST",
            payload={
                "task_code": "daily_reflection",
                "expected_version": current["version"],
                "content": content,
            },
            request_headers={"Idempotency-Key": str(uuid4())},
        )
        body = result.get("body", {})
        job = body.get("job", {}) if isinstance(body, dict) else {}
        if result.get("ok") and isinstance(job, dict):
            version = job.get("requested_resource_version")
            if isinstance(version, int):
                current["version"] = version
            await render_job(job)
        elif result.get("status") == 409:
            set_state("conflict")
        else:
            set_state("failed")

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
    source_confirm_button = ui.button(
        "确认集体活动原文", on_click=confirm_source_and_split
    ).classes("min-h-[44px]")
    source_confirm_button.on("keydown.enter", confirm_source_and_split)
    docx_upload = ui.upload(
        label="上传 DOCX 原始教案",
        on_upload=preview_docx_source,
        auto_upload=True,
    ).props(
        'accept=".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document"'
    )
    docx_confirm = ui.button("确认 DOCX 提取文本", on_click=confirm_docx_source_and_split).classes(
        "min-h-[44px]"
    )
    docx_confirm.set_enabled(False)
    docx_confirm.on("keydown.enter", confirm_docx_source_and_split)
    docx_confirm_button[0] = docx_confirm
    add_button = ui.button("新增适龄环节", on_click=create_add_step).classes("min-h-[44px]")
    add_button.set_enabled(False)
    add_button.on("keydown.enter", create_add_step)
    add_step_button[0] = add_button

    def generation_handler(task_code: str) -> Any:
        async def generate() -> None:
            await create_generation(task_code)

        return generate

    for action in AI_SECTION_ACTIONS:
        generate = generation_handler(action.task_code)
        button = (
            ui.button(action.button_label, on_click=generate)
            .props(f'aria-label="{action.button_label}"')
            .classes("min-h-[44px]")
        )
        button.on("keydown.enter", generate)
    batch_button = (
        ui.button("一键生成四栏", on_click=create_batch)
        .props('aria-label="一键生成四栏"')
        .classes("min-h-[44px]")
    )
    batch_button.on("keydown.enter", create_batch)
    reflection_button = (
        ui.button("生成一日活动反思", on_click=create_reflection)
        .props('aria-label="生成一日活动反思"')
        .classes("min-h-[44px]")
    )
    reflection_button.on("keydown.enter", create_reflection)
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
