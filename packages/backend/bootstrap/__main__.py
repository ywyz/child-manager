"""维护者交互式初始化 CLI。"""

import argparse
import os
from getpass import getpass

from packages.backend.bootstrap.init_admin import initialize_admin


def _init_admin() -> int:
    database_url = os.environ.get("CHILD_MANAGER_DATABASE_URL")
    if not database_url:
        print("未配置当前档位数据库。")
        return 2
    kindergarten_name = input("幼儿园名称：").strip()
    username = input("管理员用户名：").strip()
    display_name = input("管理员显示名称：").strip()
    password = getpass("管理员密码：")
    confirmation = getpass("再次输入管理员密码：")
    if password != confirmation:
        print("两次输入的密码不一致。")
        return 2
    try:
        created = initialize_admin(
            database_url=database_url,
            kindergarten_name=kindergarten_name,
            username=username,
            display_name=display_name,
            password=password,
        )
    except ValueError as exc:
        print(str(exc))
        return 2
    print("首位管理员初始化完成。" if created else "系统已初始化。")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="child-manager-bootstrap")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("init-admin", help="交互式创建首位管理员")
    arguments = parser.parse_args(argv)
    return _init_admin() if arguments.command == "init-admin" else 2


if __name__ == "__main__":
    raise SystemExit(main())
