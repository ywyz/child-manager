from ipaddress import ip_address
from typing import Any, Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from packages.security.cookie import validate_cookie_security

Environment = Literal["production", "development", "test"]

# development/test 默认信任的回环 BFF peer；production 必须显式配置。
_LOOPBACK_BFF_PEERS = ["127.0.0.1", "::1", "localhost"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=None,
        extra="ignore",
        env_prefix="CHILD_MANAGER_",
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
    jwt_expire_minutes: int = 15

    encryption_key_path: str = ""

    ai_api_timeout_seconds: int = 60

    allowed_hosts: list[str] = ["localhost", "127.0.0.1"]

    # 可信 BFF peer 列表；只有直接 socket peer 命中该列表时才信任内部转发头。
    # 显式传入（含空列表）时完全尊重配置；未传入时按 environment 取默认值。
    trusted_bff_peers: list[str] = Field(default_factory=list)

    # Cookie Secure 标志。显式传入时尊重配置；未传入时按 environment 取默认值。
    cookie_secure: bool = True

    @model_validator(mode="before")
    @classmethod
    def _apply_environment_defaults(cls, data: Any) -> Any:
        """为 trusted_bff_peers 与 cookie_secure 应用环境感知默认值。

        只有当字段未被显式提供（既无 kwargs 也无环境变量）时才填默认值，
        显式传入空列表或 False 必须被尊重。
        """
        if not isinstance(data, dict):
            return data
        env = data.get("environment", "production")
        if "trusted_bff_peers" not in data:
            data["trusted_bff_peers"] = (
                list(_LOOPBACK_BFF_PEERS) if env in ("development", "test") else []
            )
        if "cookie_secure" not in data:
            data["cookie_secure"] = env != "development"
        return data

    @model_validator(mode="after")
    def _production_requires_secure_cookie(self) -> Settings:
        if self.environment == "production" and not self.cookie_secure:
            raise ValueError("production 环境必须启用 Cookie Secure")
        return self

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
