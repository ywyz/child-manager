from ipaddress import ip_address
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from packages.security.cookie import validate_cookie_security

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
    csrf_signing_key: str = ""
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
                msg = f"必须使用回环地址,当前值: {v}"
                raise ValueError(msg)
        except ValueError as err:
            if v != "localhost":
                msg = f"必须使用回环地址,当前值: {v}"
                raise ValueError(msg) from err
        return v

    def validate_cookie_security(
        self,
        bind_host: str,
        cookie_secure: bool,
    ) -> None:
        validate_cookie_security(
            environment=self.environment,
            bind_host=bind_host,
            cookie_secure=cookie_secure,
        )


settings = Settings()
