"""关联教师维护室内/户外班级区域的页面。"""

from nicegui import ui

from apps.web.api_client import same_origin_api_request


async def load_all_class_areas(
    class_id: str,
    area_type: str,
) -> tuple[list[dict[str, object]], int | None]:
    items: list[dict[str, object]] = []
    page = 1
    while True:
        result = await same_origin_api_request(
            f"/api/v1/settings/classes/{class_id}/areas/{area_type}?page={page}&page_size=100"
        )
        body = result.get("body", {})
        if not result.get("ok") or not isinstance(body, dict):
            status = result.get("status")
            return [], int(status) if isinstance(status, int) else 0
        page_items = [item for item in body.get("items", []) if isinstance(item, dict)]
        items.extend(page_items)
        total = body.get("total")
        if not isinstance(total, int) or len(items) >= total:
            return items, None
        if not page_items:
            return [], 0
        page += 1


def class_areas_page_text() -> tuple[str, ...]:
    return (
        "我的班级区域",
        "班级区域",
        "室内区域",
        "户外区域",
        "添加区域",
        "整体保存",
        "允许暂时留空",
        "没有维护该班区域的权限",
    )


def register_class_area_pages() -> None:
    @ui.page("/class-areas")
    def class_areas_index_page() -> None:
        ui.label("我的班级区域").classes("text-h5")
        class_links = ui.column()
        status = ui.label("")

        async def load_classes() -> None:
            result = await same_origin_api_request("/api/v1/settings/classes?page=1&page_size=100")
            body = result.get("body", {})
            if result.get("status") == 403:
                status.set_text("当前账号未关联任何班级")
                return
            if not result.get("ok") or not isinstance(body, dict):
                status.set_text("班级读取失败")
                return
            items = [item for item in body.get("items", []) if isinstance(item, dict)]
            if not items:
                status.set_text("当前账号未关联任何班级")
                return
            with class_links:
                for item in items:
                    class_id = item.get("id")
                    name = item.get("name")
                    if class_id and name:
                        ui.link(str(name), f"/class-areas/{class_id}")

        ui.timer(0.1, load_classes, once=True)

    @ui.page("/class-areas/{class_id}")
    def class_areas_page(class_id: str) -> None:
        ui.label("班级区域").classes("text-h5")
        ui.label("每行一个区域，允许暂时留空。")
        indoor = ui.textarea("室内区域")
        outdoor = ui.textarea("户外区域")
        status = ui.label("")

        async def load_type(area_type: str, target: object) -> bool:
            items, error_status = await load_all_class_areas(class_id, area_type)
            if error_status == 403:
                status.set_text("没有维护该班区域的权限")
                return False
            if error_status is not None:
                status.set_text("区域读取失败")
                return False
            names = [
                str(item["name"]) for item in items if item.get("name") and item.get("is_active")
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
