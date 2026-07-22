"""维护者交互式通行密钥初始化 CLI。"""

import argparse
import os
from uuid import UUID

from packages.backend.bootstrap.init_admin import (
    activate_initialization,
    migrate_passkeys,
    start_initialization,
)


def _database_url() -> str | None:
    value = os.environ.get("CHILD_MANAGER_DATABASE_URL")
    if not value:
        print("未配置当前档位数据库。")
    return value


def _start() -> int:
    database_url = _database_url()
    if database_url is None:
        return 2
    try:
        result = start_initialization(
            database_url=database_url,
            kindergarten_name=input("幼儿园名称：").strip(),
            username=input("管理员用户名：").strip(),
            display_name=input("管理员显示名称：").strip(),
            owner_reference=input("园所负责人预登记标识：").strip(),
            operator_reference=input("独立运维/安全责任人预登记标识：").strip(),
        )
    except ValueError as exc:
        print(str(exc))
        return 2
    if result is None:
        print("系统已初始化。")
        return 0
    bootstrap_id, secret = result
    print(f"初始化记录：{bootstrap_id}")
    print(f"初始化凭据：{secret}")
    print("请在 15 分钟内登记通行密钥；登记不会建立登录会话。")
    return 0


def _activate(bootstrap_id: str) -> int:
    database_url = _database_url()
    if database_url is None:
        return 2
    try:
        owner_reference = input("园所负责人核验标识：").strip()
        operator_reference = input("独立运维/安全责任人核验标识：").strip()
        activate_initialization(
            database_url=database_url,
            bootstrap_id=UUID(bootstrap_id),
            owner_reference=owner_reference,
            operator_reference=operator_reference,
        )
    except EOFError:
        print("必须由预登记园所负责人和独立运维/安全责任人双人核验。")
        return 2
    except ValueError as exc:
        print(str(exc))
        return 2
    print("首位管理员已激活。")
    return 0


def _migrate_passkeys() -> int:
    database_url = _database_url()
    if database_url is None:
        return 2
    try:
        issued = migrate_passkeys(database_url=database_url)
    except ValueError as exc:
        print(str(exc))
        return 2
    if not issued:
        print("没有待迁移账号。")
        return 0
    for username, secret in issued:
        print(f"账号：{username} 迁移邀请凭据：{secret}")
    print("迁移邀请凭据仅显示一次，有效期 24 小时；请通过既定带外渠道分别交付。")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="child-manager-bootstrap")
    root = parser.add_subparsers(dest="command", required=True)
    init_admin = root.add_parser("init-admin", help="首位管理员初始化")
    init_commands = init_admin.add_subparsers(dest="init_command", required=True)
    init_commands.add_parser("start", help="签发一次性初始化凭据")
    activate = init_commands.add_parser("activate", help="完成双人核验激活")
    activate.add_argument("--bootstrap-id", required=True)
    root.add_parser("migrate-passkeys", help="列出现有账号通行密钥迁移命令")
    arguments = parser.parse_args(argv)
    if arguments.command == "migrate-passkeys":
        return _migrate_passkeys()
    if arguments.init_command == "start":
        return _start()
    return _activate(arguments.bootstrap_id)


if __name__ == "__main__":
    raise SystemExit(main())
