"""管理员首期必要设置页面。"""

import asyncio
import json
from uuid import uuid4

from nicegui import ui

from apps.web.api_client import same_origin_api_request
from apps.web.components.job_status import prompt_test_status, should_poll


def settings_page_text() -> tuple[str, ...]:
    return (
        "系统设置",
        "幼儿园信息",
        "学期管理",
        "用户与班级",
        "保存园所名称",
        "创建学期",
        "设为当前学期",
        "创建班级",
        "保存教师关系",
        "主班教师",
        "区域尚未配置",
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
    )


def masked_api_key_text(masked: str) -> str:
    """只渲染服务端给出的末四位脱敏摘要。"""

    return f"已配置：{masked}"


def build_ai_prompt_settings_section() -> None:
    ui.label("AI 模型档案").classes("text-h6")
    model_name = ui.input("模型档案名称")
    api_base_url = ui.input("API 地址")
    provider_model_name = ui.input("模型名")
    api_key = ui.input("API Key（仅写入）").props(
        'type=password autocomplete=new-password aria-describedby="ai-api-key-error"'
    )
    risk_confirmed = ui.checkbox("外部数据处理风险")
    model_status = ui.label("").props('id="ai-api-key-error" aria-live="polite"')
    profile_id: list[str] = []

    ui.label("提示词中心").classes("text-h6")
    prompt_code = ui.input(
        "提示词标识",
        value="daily_activity_plan.morning_talk",
    )
    prompt_version_id = ui.input("测试版本 ID")
    prompt_profile_id = ui.input("测试模型档案 ID")
    prompt_draft = ui.textarea("提示词草稿")
    historical_version_id = ui.input("历史版本 ID")
    test_variables = ui.textarea(
        "测试变量（JSON）",
        value="{}",
    )
    prompt_status = ui.label("").props('aria-live="polite"')

    async def save_model_profile() -> None:
        result = await same_origin_api_request(
            "/api/v1/settings/ai-model-profiles",
            method="POST",
            payload={
                "name": model_name.value or "",
                "api_base_url": api_base_url.value or "",
                "model_name": provider_model_name.value or "",
                "api_key": api_key.value or None,
                "capability_codes": ["text", "structured_output"],
                "max_concurrency": 2,
                "rate_limit_per_minute": None,
                "is_default": False,
            },
        )
        body = result.get("body", {})
        if result.get("ok") and isinstance(body, dict) and body.get("id"):
            profile_id[:] = [str(body["id"])]
            prompt_profile_id.value = profile_id[0]
            api_key.value = ""
            model_status.set_text("模型档案已保存")
        else:
            model_status.set_text("模型档案保存失败")

    async def enable_model_profile() -> None:
        selected = profile_id[0] if profile_id else str(prompt_profile_id.value or "")
        if not selected or not risk_confirmed.value:
            model_status.set_text("启用前必须确认外部数据处理风险")
            return
        result = await same_origin_api_request(
            f"/api/v1/settings/ai-model-profiles/{selected}/enable",
            method="POST",
            payload={"confirm_external_data_risk": True},
        )
        model_status.set_text("模型档案已启用" if result.get("ok") else "模型档案启用失败")

    async def save_prompt_draft() -> None:
        result = await same_origin_api_request(
            f"/api/v1/prompts/{prompt_code.value}/draft",
            method="PUT",
            payload={
                "content": prompt_draft.value or "",
                "based_on_version_id": prompt_version_id.value or None,
            },
        )
        body = result.get("body", {})
        if result.get("ok") and isinstance(body, dict) and body.get("id"):
            prompt_version_id.value = str(body["id"])
            prompt_status.set_text("提示词草稿已保存")
        else:
            prompt_status.set_text("提示词草稿保存失败")

    async def publish_prompt() -> None:
        result = await same_origin_api_request(
            f"/api/v1/prompts/{prompt_code.value}/publish",
            method="POST",
            payload={},
        )
        body = result.get("body", {})
        if result.get("ok") and isinstance(body, dict) and body.get("id"):
            prompt_version_id.value = str(body["id"])
            prompt_status.set_text("提示词新版本已发布")
        else:
            prompt_status.set_text("提示词发布失败")

    async def restore_prompt() -> None:
        selected = str(historical_version_id.value or "")
        if not selected:
            prompt_status.set_text("请填写历史版本 ID")
            return
        result = await same_origin_api_request(
            f"/api/v1/prompts/{prompt_code.value}/versions/{selected}/restore",
            method="POST",
            payload={},
        )
        body = result.get("body", {})
        if result.get("ok") and isinstance(body, dict) and body.get("id"):
            prompt_version_id.value = str(body["id"])
            prompt_status.set_text("历史版本已恢复为新版本")
        else:
            prompt_status.set_text("提示词版本恢复失败")

    async def run_prompt_test() -> None:
        try:
            variables = json.loads(str(test_variables.value or "{}"))
        except json.JSONDecodeError:
            prompt_status.set_text("测试变量必须是 JSON 对象")
            return
        if not isinstance(variables, dict):
            prompt_status.set_text("测试变量必须是 JSON 对象")
            return
        accepted = await same_origin_api_request(
            f"/api/v1/prompts/{prompt_code.value}/tests",
            method="POST",
            payload={
                "version_id": prompt_version_id.value or "",
                "model_profile_id": prompt_profile_id.value or "",
                "variables": variables,
            },
            request_headers={"Idempotency-Key": f"web-prompt-test-{uuid4()}"},
        )
        body = accepted.get("body", {})
        job = body.get("job", {}) if isinstance(body, dict) else {}
        if not accepted.get("ok") or not isinstance(job, dict) or not job.get("id"):
            prompt_status.set_text("异步测试创建失败")
            return
        while should_poll(str(job.get("status", ""))):
            prompt_status.set_text(prompt_test_status(job).message)
            await asyncio.sleep(1.5)
            result = await same_origin_api_request(f"/api/v1/jobs/{job['id']}")
            job = result.get("body", {}) if result.get("ok") else {}
            if not isinstance(job, dict):
                job = {}
                break
        prompt_status.set_text(prompt_test_status(job).message)

    async def load_ai_prompt_settings() -> None:
        profiles = await same_origin_api_request(
            "/api/v1/settings/ai-model-profiles?page=1&page_size=20"
        )
        profile_body = profiles.get("body", {})
        if profiles.get("ok") and isinstance(profile_body, dict):
            items = profile_body.get("items", [])
            if isinstance(items, list) and items and isinstance(items[0], dict):
                first = items[0]
                profile_id[:] = [str(first.get("id", ""))]
                prompt_profile_id.value = profile_id[0]
                model_name.value = str(first.get("name", ""))
                api_base_url.value = str(first.get("api_base_url", ""))
                provider_model_name.value = str(first.get("model_name", ""))
                masked = first.get("api_key_masked")
                if isinstance(masked, str):
                    model_status.set_text(masked_api_key_text(masked))
        prompts = await same_origin_api_request("/api/v1/prompts?page=1&page_size=7")
        prompt_body = prompts.get("body", {})
        if prompts.get("ok") and isinstance(prompt_body, dict):
            items = prompt_body.get("items", [])
            if isinstance(items, list) and items and isinstance(items[0], dict):
                first_prompt = items[0]
                prompt_code.value = str(first_prompt.get("code", prompt_code.value))
                prompt_version_id.value = str(first_prompt.get("effective_version_id", ""))

    ui.button("保存模型档案", on_click=save_model_profile)
    ui.button("启用模型", on_click=enable_model_profile)
    ui.button("保存提示词草稿", on_click=save_prompt_draft)
    ui.button("发布新版本", on_click=publish_prompt)
    ui.label("历史版本")
    ui.button("恢复为新版本", on_click=restore_prompt)
    ui.button("运行异步测试", on_click=run_prompt_test)
    ui.timer(0.1, load_ai_prompt_settings, once=True)


def register_settings_pages() -> None:
    @ui.page("/settings")
    def settings_page() -> None:
        ui.label("系统设置").classes("text-h5")
        ui.label("幼儿园信息").classes("text-h6")
        kindergarten_name = ui.input("幼儿园名称")
        kindergarten_status = ui.label("")

        ui.label("学期管理").classes("text-h6")
        semester_name = ui.input("学期名称")
        semester_start = ui.input("开始日期").props("type=date")
        semester_end = ui.input("结束日期").props("type=date")
        semester_status = ui.label("")
        created_semester_id: list[str] = []

        ui.label("用户与班级").classes("text-h6")
        class_name = ui.input("班级名称")
        ui.html(
            """
            <label for="m3-age-group">年龄段</label>
            <select id="m3-age-group" aria-label="年龄段">
              <option value="toddler">托班</option>
              <option value="small" selected>小班</option>
              <option value="middle">中班</option>
              <option value="large">大班</option>
            </select>
            """
        )
        teacher_id = ui.input("任课教师 ID")
        ui.html(
            """
            <label for="m3-lead-teacher">
              <input id="m3-lead-teacher" type="checkbox" aria-label="主班教师">
              主班教师
            </label>
            """
        )
        class_status = ui.label("")
        class_results = ui.column()
        age_group_ids: dict[str, str] = {}

        build_ai_prompt_settings_section()

        async def save_kindergarten() -> None:
            result = await same_origin_api_request(
                "/api/v1/settings/kindergarten",
                method="PATCH",
                payload={"name": kindergarten_name.value or ""},
            )
            kindergarten_status.set_text(
                "园所信息已保存" if result.get("ok") else "园所信息保存失败"
            )

        async def create_semester() -> None:
            result = await same_origin_api_request(
                "/api/v1/settings/semesters",
                method="POST",
                payload={
                    "name": semester_name.value or "",
                    "start_date": semester_start.value or "",
                    "end_date": semester_end.value or "",
                    "is_active": True,
                },
            )
            body = result.get("body", {})
            if result.get("ok") and isinstance(body, dict) and body.get("id"):
                created_semester_id[:] = [str(body["id"])]
                semester_status.set_text("学期已创建")
            else:
                semester_status.set_text("创建学期失败")

        async def make_current() -> None:
            for _attempt in range(20):
                if created_semester_id:
                    break
                await asyncio.sleep(0.05)
            if not created_semester_id:
                semester_status.set_text("请先创建学期")
                return
            result = await same_origin_api_request(
                f"/api/v1/settings/semesters/{created_semester_id[0]}/make-current",
                method="POST",
                payload={},
            )
            semester_status.set_text("当前学期已更新" if result.get("ok") else "当前学期更新失败")

        def render_class_actions(class_id: str) -> None:
            with class_results:
                ui.label(class_id).props('data-testid="created-class-id"')

                async def unlink(target: str = class_id) -> None:
                    result = await same_origin_api_request(
                        f"/api/v1/settings/classes/{target}/teachers",
                        method="PUT",
                        payload={"teachers": []},
                    )
                    class_status.set_text(
                        "教师关系已清空" if result.get("ok") else "教师关系清空失败"
                    )

                ui.button("清空教师关系", on_click=unlink).props(
                    f'data-testid="unlink-teachers-{class_id}"'
                )

        async def create_class() -> None:
            selected_code = str(
                await ui.run_javascript(
                    "return document.getElementById('m3-age-group').value",
                    timeout=5.0,
                )
                or ""
            )
            selected_id = age_group_ids.get(selected_code)
            if selected_id is None:
                class_status.set_text("年龄段尚未加载")
                return
            result = await same_origin_api_request(
                "/api/v1/settings/classes",
                method="POST",
                payload={
                    "name": class_name.value or "",
                    "age_group_id": selected_id,
                    "is_active": True,
                },
            )
            body = result.get("body", {})
            if not result.get("ok") or not isinstance(body, dict) or not body.get("id"):
                class_status.set_text("创建班级失败")
                return
            class_id = str(body["id"])
            teacher_value = str(teacher_id.value or "").strip()
            if teacher_value:
                is_lead_teacher = bool(
                    await ui.run_javascript(
                        "return document.getElementById('m3-lead-teacher').checked",
                        timeout=5.0,
                    )
                )
                relationship = await same_origin_api_request(
                    f"/api/v1/settings/classes/{class_id}/teachers",
                    method="PUT",
                    payload={
                        "teachers": [
                            {
                                "user_id": teacher_value,
                                "is_lead_teacher": is_lead_teacher,
                            }
                        ]
                    },
                )
                if not relationship.get("ok"):
                    class_status.set_text("班级已创建，但保存教师关系失败")
                    render_class_actions(class_id)
                    return
            render_class_actions(class_id)
            class_status.set_text("班级已创建，区域尚未配置")

        async def load() -> None:
            kindergarten = await same_origin_api_request("/api/v1/settings/kindergarten")
            kindergarten_body = kindergarten.get("body", {})
            if kindergarten.get("ok") and isinstance(kindergarten_body, dict):
                kindergarten_name.value = str(kindergarten_body.get("name", ""))

            groups = await same_origin_api_request("/api/v1/settings/age-groups")
            groups_body = groups.get("body", [])
            if groups.get("ok") and isinstance(groups_body, list):
                age_group_ids.clear()
                for item in groups_body:
                    if isinstance(item, dict) and item.get("code") and item.get("id"):
                        age_group_ids[str(item["code"])] = str(item["id"])

            classes = await same_origin_api_request("/api/v1/settings/classes?page=1&page_size=100")
            classes_body = classes.get("body", {})
            if classes.get("ok") and isinstance(classes_body, dict):
                for item in classes_body.get("items", []):
                    if isinstance(item, dict) and item.get("id"):
                        render_class_actions(str(item["id"]))

        ui.button("保存园所名称", on_click=save_kindergarten)
        ui.button("创建学期", on_click=create_semester)
        ui.button("设为当前学期", on_click=make_current)
        ui.button("创建班级", on_click=create_class)
        ui.label("保存教师关系")
        ui.label("区域尚未配置")
        ui.timer(0.1, load, once=True)
