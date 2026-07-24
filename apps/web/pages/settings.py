"""管理员首期必要设置页面。"""

import asyncio

from nicegui import ui

from apps.web.api_client import same_origin_api_request


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
    )


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
