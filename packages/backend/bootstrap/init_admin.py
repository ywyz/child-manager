"""初始化管理员 CLI。"""

import getpass
import sys
from collections.abc import Callable

from packages.backend.database.session import SessionLocal
from packages.backend.identity.models import User
from packages.backend.identity.passwords import validate_password
from packages.backend.identity.service import IdentityService


def _has_initial_admin() -> bool:
    session = SessionLocal()
    try:
        return session.query(User).first() is not None
    finally:
        session.close()


def _default_password_input(prompt: str) -> str:
    """交互式终端使用 getpass 避免回显；非 TTY 环境回退到 input 以支持自动化测试。"""
    if sys.stdin.isatty():
        return getpass.getpass(prompt)
    return input(prompt)


def _read_password(
    prompt: str,
    password_func: Callable[[str], str],
) -> str:
    while True:
        value = password_func(prompt)
        try:
            validate_password(value)
        except ValueError as exc:
            print(f"密码不符合要求: {exc}")
            continue
        return value


def run_init_admin(
    *,
    input_func: Callable[[str], str] = input,
    password_func: Callable[[str], str] = _default_password_input,
) -> str:
    """交互式初始化首位管理员。"""
    if _has_initial_admin():
        print("系统已初始化")
        return "系统已初始化"

    kg_name = input_func("幼儿园名称: ")
    admin_username = input_func("管理员用户名: ")
    password = _read_password("管理员密码: ", password_func)
    confirm = password_func("确认密码: ")
    if password != confirm:
        print("两次输入的密码不一致")
        return "两次输入的密码不一致"

    session = SessionLocal()
    try:
        IdentityService(session).init_admin(
            kg_name=kg_name or "默认幼儿园",
            admin_username=admin_username,
            password=password,
        )
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

    print("管理员初始化成功")
    return "管理员初始化成功"
