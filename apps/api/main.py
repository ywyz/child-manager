import argparse
from ipaddress import ip_address

import uvicorn

from apps.api.app import create_app

app = create_app()


def _validate_bind_host(host: str) -> None:
    """进程只能绑定回环地址，包括开发环境。"""
    try:
        if ip_address(host).is_loopback:
            return
    except ValueError:
        pass
    if host == "localhost":
        return
    raise ValueError(f"API 只能绑定回环地址,当前值: {host}")


def main() -> None:
    parser = argparse.ArgumentParser(description="启动 Child Manager API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=28000, type=int)
    args = parser.parse_args()

    _validate_bind_host(args.host)

    uvicorn.run(
        "apps.api.main:app",
        host=args.host,
        port=args.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
