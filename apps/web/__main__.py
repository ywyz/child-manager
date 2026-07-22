"""仅绑定回环地址的 NiceGUI Web 入口。"""

import argparse
import os
from ipaddress import ip_address
from urllib.parse import urlsplit

from nicegui import ui

from apps.web.app import register_web
from apps.web.observability import configure_logging


def _require_loopback(value: str, label: str) -> None:
    try:
        allowed = ip_address(value).is_loopback
    except ValueError:
        allowed = False
    if not allowed:
        raise ValueError(f"{label}必须使用回环地址")


def _validate_cookie_security(*, environment: str, bind_host: str, cookie_secure: bool) -> None:
    if cookie_secure:
        return
    if environment != "development":
        raise ValueError("非开发环境必须启用 Cookie Secure")
    _require_loopback(bind_host, "关闭 Cookie Secure 时的 Web 绑定地址")


def main() -> None:
    configure_logging()
    parser = argparse.ArgumentParser(description="启动 Child Manager Web BFF")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8080, type=int)
    parser.add_argument("--api-base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()

    _require_loopback(args.host, "Web 绑定地址")
    cookie_secure_value = os.environ.get("CHILD_MANAGER_COOKIE_SECURE", "true").lower()
    if cookie_secure_value not in {"true", "false"}:
        parser.error("CHILD_MANAGER_COOKIE_SECURE 必须为 true 或 false")
    _validate_cookie_security(
        environment=os.environ.get("CHILD_MANAGER_ENV", "production"),
        bind_host=args.host,
        cookie_secure=cookie_secure_value == "true",
    )
    api_host = urlsplit(args.api_base_url).hostname or ""
    _require_loopback(api_host, "API 地址")
    register_web(api_base_url=args.api_base_url)
    ui.run(host=args.host, port=args.port, show=False, reload=False, proxy_headers=False)


if __name__ == "__main__":
    main()
