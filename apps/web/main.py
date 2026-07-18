import argparse
import logging
import os
import sys
from ipaddress import ip_address
from urllib.parse import urlsplit

import structlog
from nicegui import ui

from apps.web.app import register_web
from packages.security.cookie import validate_cookie_security
from packages.security.redaction import redaction_processor

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        redaction_processor,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.dev.ConsoleRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)
logging.basicConfig(level=logging.INFO, format="%(message)s")


def _require_loopback(value: str, label: str) -> None:
    try:
        allowed = ip_address(value).is_loopback
    except ValueError:
        allowed = False
    if not allowed:
        raise ValueError(f"{label}必须使用回环地址")


def main() -> None:
    parser = argparse.ArgumentParser(description="启动 Child Manager Web BFF")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=28080, type=int)
    parser.add_argument("--api-base-url", default="http://127.0.0.1:28000")
    # NiceGUI testing 通过 runpy 加载本文件并继承 pytest 的 sys.argv，
    # 因此测试上下文中使用空参数列表，避免 argparse 解析 pytest 参数失败。
    if "pytest" in sys.modules:
        args = parser.parse_args([])
    else:
        args = parser.parse_args()

    _require_loopback(args.host, "Web 绑定地址")
    api_host = urlsplit(args.api_base_url).hostname or "127.0.0.1"
    _require_loopback(api_host, "API 地址")

    environment = os.environ.get("ENVIRONMENT", "production")
    validate_cookie_security(
        environment=environment,
        bind_host=args.host,
        cookie_secure=environment == "production",
    )

    register_web(api_base_url=args.api_base_url)
    # pyright: ignore[reportUnknownMemberType]
    ui.run(
        title="幼儿园教育管理系统",
        host=args.host,
        port=args.port,
        reload=False,
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
