"""Cookie 安全配置校验（Web 与 API 共享）。"""

from ipaddress import ip_address


def validate_cookie_security(
    *,
    environment: str,
    bind_host: str,
    cookie_secure: bool,
) -> None:
    """校验 Cookie Secure 与绑定地址的组合是否合法。

    仅非生产环境（development/test）允许关闭 Secure；关闭 Secure 时进程必须绑定回环地址。
    Codex 第十九轮审阅 HARD：Web 从裸 ENVIRONMENT 改为 CHILD_MANAGER_ENVIRONMENT 后，
    测试环境为 ``test``，必须在回环绑定下允许关闭 Secure（与 API 的 secure=False 一致）。
    """
    if cookie_secure:
        return
    if environment not in {"development", "test"}:
        raise ValueError("非开发环境必须启用 Cookie Secure")
    try:
        is_loopback = ip_address(bind_host).is_loopback
    except ValueError:
        is_loopback = bind_host == "localhost"
    if not is_loopback:
        raise ValueError("关闭 Cookie Secure 时只能绑定回环地址")
