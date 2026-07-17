import os
from collections.abc import Awaitable, Callable, Generator
from pathlib import Path
from typing import Annotated

import structlog
from fastapi import Depends, Request
from sqlalchemy.orm import Session

from packages.backend.database import session as session_module
from packages.backend.identity.exceptions import ForbiddenError, UnauthenticatedError
from packages.backend.identity.tokens import decode_access_token
from packages.contracts.identity import CurrentUser

LOGGER = structlog.get_logger(__name__)


async def _safe_check(name: str, check: Callable[[], Awaitable[bool]]) -> bool:
    try:
        return await check()
    except Exception as exc:
        LOGGER.warning("health_check_failed", component=name, error_type=type(exc).__name__)
        return False


class HealthDependencies:
    def __init__(
        self,
        database: Callable[[], Awaitable[bool]],
        redis: Callable[[], Awaitable[bool]],
        ai: Callable[[], Awaitable[bool]],
        calendar: Callable[[], Awaitable[bool]],
        template: Callable[[], Awaitable[bool]],
        export_storage: Callable[[], Awaitable[bool]],
        security_ready: bool,
    ) -> None:
        self.database = database
        self.redis = redis
        self.ai = ai
        self.calendar = calendar
        self.template = template
        self.export_storage = export_storage
        self.security_ready = security_ready


async def _ai_unconfigured() -> bool:
    return False


async def _runtime_storage_unconfigured() -> bool:
    return False


async def _calendar_library_available() -> bool:
    try:
        from importlib import import_module

        calendar_module = import_module("chinese_calendar")
    except ImportError:
        return False
    return callable(getattr(calendar_module, "is_workday", None))


def build_health_dependencies() -> HealthDependencies:
    import psycopg
    from redis.asyncio import Redis

    repository_root = Path(__file__).resolve().parents[2]
    runtime_root_value = os.environ.get("CHILD_MANAGER_RUNTIME_ROOT")

    async def database_check() -> bool:
        database_url = os.environ.get("CHILD_MANAGER_DATABASE_URL")
        if not database_url:
            return False
        native_url = database_url.replace("postgresql+psycopg://", "postgresql://", 1)
        connection = await psycopg.AsyncConnection.connect(native_url, connect_timeout=2)
        async with connection:
            await connection.execute("SELECT 1")
        return True

    async def redis_check() -> bool:
        redis_url = os.environ.get("CHILD_MANAGER_REDIS_URL")
        if not redis_url:
            return False
        # pyright: ignore[reportUnknownMemberType]
        client = Redis.from_url(redis_url, socket_connect_timeout=1, socket_timeout=1)
        try:
            # pyright: ignore[reportUnknownMemberType]
            return bool(await client.ping())
        finally:
            await client.aclose()

    async def path_check(path: Path, *, writable: bool = False) -> bool:
        return path.is_dir() and (not writable or os.access(path, os.W_OK))

    if runtime_root_value:

        async def export_storage_check() -> bool:
            return await path_check(Path(runtime_root_value) / "exports", writable=True)

    else:
        export_storage_check = _runtime_storage_unconfigured

    security_values = (
        os.environ.get("CHILD_MANAGER_JWT_SIGNING_KEY"),
        os.environ.get("CHILD_MANAGER_CSRF_SIGNING_KEY"),
    )

    async def template_check() -> bool:
        return (repository_root / "templates/teacherplan/teacherplan.docx").is_file()

    return HealthDependencies(
        database=database_check,
        redis=redis_check,
        ai=_ai_unconfigured,
        calendar=_calendar_library_available,
        template=template_check,
        export_storage=export_storage_check,
        security_ready=all(value is not None and bool(value.strip()) for value in security_values),
    )


def get_db() -> Generator[Session]:
    session = session_module.SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_current_user(
    request: Request,
    session: Annotated[Session, Depends(get_db)],
) -> CurrentUser:
    token = request.cookies.get("child_manager_access")
    if not token:
        raise UnauthenticatedError("未登录")

    from packages.backend.config import settings

    payload = decode_access_token(token, settings.jwt_signing_key)
    if payload is None:
        raise UnauthenticatedError("会话已失效")

    kindergarten_id = payload.get("kindergarten_id")
    if not kindergarten_id:
        raise UnauthenticatedError("会话已失效")

    from packages.backend.identity.service import IdentityService

    service = IdentityService(session)
    user = service.get_user_by_id(kindergarten_id, payload["sub"])
    if user is None or not user.is_active:
        raise UnauthenticatedError("会话已失效")

    return service.build_current_user(user)


def require_admin(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
) -> CurrentUser:
    if "admin" not in current_user.role_codes:
        raise ForbiddenError("需要管理员权限")
    return current_user
