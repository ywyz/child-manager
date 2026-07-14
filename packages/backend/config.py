"""应用分级配置的公开接缝。"""

from ipaddress import ip_address
from typing import Literal

from pydantic import BaseModel, SecretStr


class AppSettings(BaseModel):
    environment: Literal["development", "test", "production"] = "production"
    bind_host: str = "127.0.0.1"
    cookie_secure: bool = True
    database_url: SecretStr
    redis_url: SecretStr | None = None
    jwt_signing_key: SecretStr | None = None
    csrf_signing_key: SecretStr | None = None

    def validate_security(self) -> None:
        """拒绝在非开发环境或非回环地址关闭 Cookie Secure。"""

        validate_cookie_security(
            environment=self.environment,
            bind_host=self.bind_host,
            cookie_secure=self.cookie_secure,
        )


def validate_cookie_security(*, environment: str, bind_host: str, cookie_secure: bool) -> None:
    """验证进程启动时的 Cookie 与监听地址组合。"""

    if cookie_secure:
        return
    if environment != "development":
        raise ValueError("非开发环境必须启用 Cookie Secure")
    try:
        is_loopback = ip_address(bind_host).is_loopback
    except ValueError:
        is_loopback = False
    if not is_loopback:
        raise ValueError("关闭 Cookie Secure 时只能绑定回环地址")


def global_security_ready(settings: AppSettings) -> bool:
    """JWT 和 CSRF 签名密钥同时存在时全局安全配置才可用。"""

    return all(
        secret is not None and bool(secret.get_secret_value())
        for secret in (settings.jwt_signing_key, settings.csrf_signing_key)
    )
