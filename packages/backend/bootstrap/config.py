from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = "development"
    api_host: str = "127.0.0.1"
    api_port: int = 28000
    web_host: str = "127.0.0.1"
    web_port: int = 28080

    postgres_host: str = "localhost"
    postgres_port: int = 25432
    database_name: str = "child_manager_trae"
    database_user: str = "admin"
    database_password: str = "dev_password"
    database_url: str = ""

    redis_host: str = "localhost"
    redis_port: int = 26379
    redis_url: str = ""

    jwt_secret_key: str = ""
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    encryption_key_path: str = ""

    ai_api_timeout_seconds: int = 60

    allowed_hosts: list[str] = ["localhost", "127.0.0.1"]

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return (
            f"postgresql+psycopg://{self.database_user}:{self.database_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.database_name}"
        )

    @property
    def resolved_redis_url(self) -> str:
        if self.redis_url:
            return self.redis_url
        return f"redis://{self.redis_host}:{self.redis_port}/0"


settings = Settings()
