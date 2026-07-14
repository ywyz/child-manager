from typing import Any

import httpx
from nicegui import ui

from packages.backend.bootstrap.config import settings

api_client = httpx.AsyncClient(base_url=f"http://{settings.api_host}:{settings.api_port}")


async def fetch_api(endpoint: str, method: str = "GET", **kwargs: Any) -> dict[str, Any]:
    async with api_client as client:
        response = await client.request(method, endpoint, **kwargs)
        response.raise_for_status()
        return response.json()


@ui.page("/")
async def index():
    with ui.header():
        ui.label("幼儿园教育管理系统").classes("text-xl font-bold")

    with ui.card():
        ui.label("欢迎使用一日活动计划系统")
        ui.separator()

        async def check_health():
            try:
                result = await fetch_api("/health/live")
                ui.notify(f"API 状态: {result['status']}", type="positive")
            except Exception as e:
                ui.notify(f"API 连接失败: {e!s}", type="negative")

        ui.button("检查 API 状态", on_click=check_health)


if __name__ == "__main__":
    ui.run(
        title="幼儿园教育管理系统",
        host=settings.web_host,
        port=settings.web_port,
        reload=False,
    )
