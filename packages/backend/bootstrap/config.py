from ipaddress import ip_address
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["production", "development", "test"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=None,
        extra="ignore",
    )

    environment: Environment = "production"
    api_host: str = "127.0.0.1"
    api_port: int = 28000
    web_host: str = "127.0.0.1"
    web_port: int = 28080

    database_url: str = ""
    redis_url: str = ""

    jwt_signing_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    encryption_key_path: str = ""

    ai_api_timeout_seconds: int = 60

    allowed_hosts: list[str] = ["localhost", "127.0.0.1"]

    @field_validator("api_host", "web_host")
    @classmethod
    def validate_loopback_host(cls, v: str) -> str:
        try:
            if not ip_address(v).is_loopback:
                raise ValueError(f"必须使用回环地址,当前值: {v}")
        except ValueError as err:
            if v != "localhost":
                raise ValueError(f"必须使用回环地址,当前值: {v}") from err
        return v

    def validate_cookie_security(self, bind_host: str, cookie_secure: bool) -> None:
        if cookie_secure:
            return
        if self.environment != "development":
            raise ValueError("非开发环境必须启用 Cookie Secure")
        try:
            is_loopback = ip_address(bind_host).is_loopback
        except ValueError:
            is_loopback = bind_host == "localhost"
        if not is_loopback:
            raise ValueError("关闭 Cookie Secure 时只能绑定回环地址")


settings = Settings()
