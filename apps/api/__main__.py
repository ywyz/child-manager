"""本地回环 API 入口。"""

import argparse
import os

import uvicorn

from packages.backend.config import validate_cookie_security
from packages.backend.observability import configure_logging


def main() -> None:
    configure_logging()
    parser = argparse.ArgumentParser(description="启动 Child Manager API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    args = parser.parse_args()
    cookie_secure_value = os.environ.get("CHILD_MANAGER_COOKIE_SECURE", "true").lower()
    if cookie_secure_value not in {"true", "false"}:
        parser.error("CHILD_MANAGER_COOKIE_SECURE 必须为 true 或 false")
    validate_cookie_security(
        environment=os.environ.get("CHILD_MANAGER_ENV", "production"),
        bind_host=args.host,
        cookie_secure=cookie_secure_value == "true",
    )
    uvicorn.run("apps.api.app:app", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
