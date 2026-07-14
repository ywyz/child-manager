"""API 装配所需健康检查依赖。"""

import os
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path

import psycopg
from redis.asyncio import Redis

HealthCheck = Callable[[], Awaitable[bool]]


@dataclass(frozen=True, slots=True)
class HealthDependencies:
    database: HealthCheck
    redis: HealthCheck
    ai: HealthCheck
    calendar: HealthCheck
    template: HealthCheck
    export_storage: HealthCheck
    security_ready: bool


async def _disabled() -> bool:
    return False


async def _available() -> bool:
    return True


def _database_check(database_url: str | None) -> HealthCheck:
    async def check() -> bool:
        if not database_url:
            return False
        native_url = database_url.replace("postgresql+psycopg://", "postgresql://", 1)
        connection = await psycopg.AsyncConnection.connect(native_url, connect_timeout=2)
        async with connection:
            await connection.execute("SELECT 1")
        return True

    return check


def _redis_check(redis_url: str | None) -> HealthCheck:
    async def check() -> bool:
        if not redis_url:
            return False
        client = Redis.from_url(redis_url, socket_connect_timeout=1, socket_timeout=1)
        try:
            return bool(await client.ping())
        finally:
            await client.aclose()

    return check


def _path_check(path: Path, *, writable: bool = False) -> HealthCheck:
    async def check() -> bool:
        return path.is_dir() and (not writable or os.access(path, os.W_OK))

    return check


def _file_check(path: Path) -> HealthCheck:
    async def check() -> bool:
        return path.is_file()

    return check


def build_health_dependencies() -> HealthDependencies:
    """从进程环境构造真实、无副作用的本地就绪检查。"""

    repository_root = Path(__file__).resolve().parents[2]
    runtime_root = Path(os.environ.get("CHILD_MANAGER_RUNTIME_ROOT", "runtime"))
    return HealthDependencies(
        database=_database_check(os.environ.get("CHILD_MANAGER_DATABASE_URL")),
        redis=_redis_check(os.environ.get("CHILD_MANAGER_REDIS_URL")),
        ai=_disabled,
        calendar=_available,
        template=_file_check(repository_root / "templates/teacherplan/teacherplan.docx"),
        export_storage=_path_check(runtime_root / "exports", writable=True),
        security_ready=all(
            os.environ.get(name)
            for name in ("CHILD_MANAGER_JWT_SIGNING_KEY", "CHILD_MANAGER_CSRF_SIGNING_KEY")
        ),
    )
