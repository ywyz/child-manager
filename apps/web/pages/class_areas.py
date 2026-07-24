"""关联教师维护室内/户外班级区域的页面。"""

from nicegui import ui

from apps.web.api_client import same_origin_api_request


def class_areas_page_text() -> tuple[str, ...]:
    return (
        "班级区域",
        "室内区域",
        "户外区域",
        "添加区域",
        "整体保存",
        "允许暂时留空",
        "没有维护该班区域的权限",
    )


def register_class_area_pages() -> None:
    @ui.page("/class-areas/{class_id}")
    def class_areas_page(class_id: str) -> None:
        ui.label("班级区域").classes("text-h5")
        ui.label("每行一个区域，允许暂时留空。")
        indoor = ui.textarea("室内区域")
        outdoor = ui.textarea("户外区域")
        status = ui.label("")

        async def load_type(area_type: str, target: object) -> bool:
            result = await same_origin_api_request(
                f"/api/v1/settings/classes/{class_id}/areas/{area_type}?page=1&page_size=100"
            )
            if result.get("status") == 403:
                status.set_text("没有维护该班区域的权限")
                return False
            body = result.get("body", {})
            if not result.get("ok") or not isinstance(body, dict):
                status.set_text("区域读取失败")
                return False
            names = [
                str(item["name"])
                for item in body.get("items", [])
                if isinstance(item, dict) and item.get("name")
            ]
            target.value = "\n".join(names)  # type: ignore[attr-defined]
            return True

        async def load() -> None:
            if not await load_type("indoor", indoor):
                return
            await load_type("outdoor", outdoor)

        async def save(area_type: str, value: str, success_message: str) -> None:
            names = [line.strip() for line in value.splitlines() if line.strip()]
            result = await same_origin_api_request(
                f"/api/v1/settings/classes/{class_id}/areas/{area_type}",
                method="PUT",
                payload={
                    "areas": [
                        {"name": name, "sort_order": index, "is_active": True}
                        for index, name in enumerate(names)
                    ]
                },
            )
            if result.get("status") == 403:
                status.set_text("没有维护该班区域的权限")
            else:
                status.set_text(success_message if result.get("ok") else "区域保存失败")

        async def save_indoor() -> None:
            await save("indoor", str(indoor.value or ""), "室内区域已保存")

        async def save_outdoor() -> None:
            await save("outdoor", str(outdoor.value or ""), "户外区域已保存")

        ui.button("整体保存室内区域", on_click=save_indoor)
        ui.button("整体保存户外区域", on_click=save_outdoor)
        ui.button("刷新区域", on_click=load)
        ui.label("添加区域")
        ui.timer(0.1, load, once=True)
