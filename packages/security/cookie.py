"""Cookie 安全配置校验（Web 与 API 共享）。"""

from ipaddress import ip_address


def validate_cookie_security(
    *,
    environment: str,
    bind_host: str,
    cookie_secure: bool,
) -> None:
    """校验 Cookie Secure 与绑定地址的组合是否合法。

    Codex M2 Final Contract Freeze M2-F03：test 默认并强制 Secure=true；
    development 仅显式回环本地调试允许 false；production 强制 true。
    因此只有 development 在绑定回环地址时允许关闭 Secure。
    """
    if cookie_secure:
        return
    if environment != "development":
        raise ValueError("非开发环境必须启用 Cookie Secure")
    try:
        is_loopback = ip_address(bind_host).is_loopback
    except ValueError:
        is_loopback = bind_host == "localhost"
    if not is_loopback:
        raise ValueError("关闭 Cookie Secure 时只能绑定回环地址")
