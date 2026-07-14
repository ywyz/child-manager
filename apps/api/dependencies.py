"""API 装配所需健康检查依赖。"""

import os
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from importlib import import_module
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


async def _ai_unconfigured() -> bool:
    return False


async def _runtime_storage_unconfigured() -> bool:
    return False


async def _calendar_library_available() -> bool:
    try:
        calendar_module = import_module("chinese_calendar")
    except ImportError:
        return False
    return callable(getattr(calendar_module, "is_workday", None))


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
    runtime_root_value = os.environ.get("CHILD_MANAGER_RUNTIME_ROOT")
    export_storage = (
        _path_check(Path(runtime_root_value) / "exports", writable=True)
        if runtime_root_value
        else _runtime_storage_unconfigured
    )
    security_values = (
        os.environ.get("CHILD_MANAGER_JWT_SIGNING_KEY"),
        os.environ.get("CHILD_MANAGER_CSRF_SIGNING_KEY"),
    )
    return HealthDependencies(
        database=_database_check(os.environ.get("CHILD_MANAGER_DATABASE_URL")),
        redis=_redis_check(os.environ.get("CHILD_MANAGER_REDIS_URL")),
        ai=_ai_unconfigured,
        calendar=_calendar_library_available,
        template=_file_check(repository_root / "templates/teacherplan/teacherplan.docx"),
        export_storage=export_storage,
        security_ready=all(value is not None and bool(value.strip()) for value in security_values),
    )
