"""FastAPI 应用装配、统一异常转换与健康端点。"""

import os
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from uuid import UUID

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from redis import Redis as SyncRedis
from starlette.exceptions import HTTPException

from apps.api.dependencies import HealthDependencies, build_health_dependencies
from apps.api.middleware import RequestContextMiddleware
from apps.api.openapi import configure_openapi
from apps.api.routers.auth import router as auth_router
from apps.api.routers.users import router as users_router
from packages.backend.identity.auth_throttle import MemoryAuthThrottle, RedisAuthThrottle
from packages.backend.identity.client_ip import parse_trusted_bff_peers
from packages.backend.identity.service import IdentityError
from packages.contracts.common import (
    CONFIGURATION_UNAVAILABLE,
    DATABASE_UNAVAILABLE,
    ErrorResponse,
    FieldError,
)

LOGGER = structlog.get_logger(__name__)


def _auth_throttle() -> MemoryAuthThrottle | RedisAuthThrottle | None:
    backend = os.environ.get("CHILD_MANAGER_AUTH_THROTTLE_BACKEND", "redis")
    failure_limit = int(os.environ.get("CHILD_MANAGER_AUTH_THROTTLE_FAILURE_LIMIT", "5"))
    subject_failure_limit = int(
        os.environ.get("CHILD_MANAGER_AUTH_THROTTLE_SUBJECT_FAILURE_LIMIT", "10")
    )
    global_failure_limit = int(
        os.environ.get("CHILD_MANAGER_AUTH_THROTTLE_GLOBAL_FAILURE_LIMIT", "100")
    )
    window = timedelta(minutes=1)
    redis_url = os.environ.get("CHILD_MANAGER_REDIS_URL")
    if backend == "memory":
        return MemoryAuthThrottle(
            failure_limit=failure_limit,
            subject_failure_limit=subject_failure_limit,
            global_failure_limit=global_failure_limit,
            window=window,
        )
    if backend != "redis":
        raise ValueError("CHILD_MANAGER_AUTH_THROTTLE_BACKEND 必须为 redis 或 memory")
    if redis_url:
        return RedisAuthThrottle(
            SyncRedis.from_url(redis_url),
            failure_limit=failure_limit,
            subject_failure_limit=subject_failure_limit,
            global_failure_limit=global_failure_limit,
            window=window,
        )
    # Redis 未配置时不得静默退化为进程内计数
    return None


def _request_id(request: Request) -> UUID:
    return UUID(str(request.state.request_id))


def _error_response(request: Request, *, status_code: int, code: str, message: str) -> JSONResponse:
    request_id = _request_id(request)
    payload = ErrorResponse(
        code=code,
        message=message,
        request_id=request_id,
    )
    return JSONResponse(
        status_code=status_code,
        content=payload.model_dump(mode="json"),
        headers={"X-Request-ID": str(request_id)},
    )


async def _safe_check(name: str, check: Callable[[], Awaitable[bool]]) -> bool:
    try:
        return await check()
    except Exception as exc:
        LOGGER.warning("health_check_failed", component=name, error_type=type(exc).__name__)
        return False


def create_app(dependencies: HealthDependencies | None = None) -> FastAPI:
    """装配无业务路由的 M1 API 基础。"""

    health = dependencies or build_health_dependencies()
    application = FastAPI(title="Child Manager API")
    application.add_middleware(RequestContextMiddleware)
    application.state.auth_throttle = _auth_throttle()
    application.state.trusted_bff_peers = parse_trusted_bff_peers(
        os.environ.get("CHILD_MANAGER_TRUSTED_BFF_PEERS")
    )
    application.state.clock = lambda: datetime.now(UTC)
    application.include_router(auth_router)
    application.include_router(users_router)

    @application.get("/health/live")
    async def live() -> dict[str, object]:
        return {"status": "ok", "checks": {}}

    @application.get("/health/ready")
    async def ready(request: Request) -> JSONResponse:
        database_ready = await _safe_check("database", health.database)
        if not database_ready:
            return _error_response(
                request,
                status_code=503,
                code=DATABASE_UNAVAILABLE,
                message="数据库暂不可用，请稍后重试。",
            )
        if not health.security_ready:
            return _error_response(
                request,
                status_code=503,
                code=CONFIGURATION_UNAVAILABLE,
                message="服务端安全配置不可用。",
            )

        checks = {
            "database": "ok",
            "security": "ok",
            "redis": "ok" if await _safe_check("redis", health.redis) else "degraded",
            "ai": "ok" if await _safe_check("ai", health.ai) else "degraded",
            "calendar": "ok" if await _safe_check("calendar", health.calendar) else "degraded",
            "template": "ok" if await _safe_check("template", health.template) else "degraded",
            "export_storage": (
                "ok" if await _safe_check("export_storage", health.export_storage) else "degraded"
            ),
        }
        status = "ok" if all(value == "ok" for value in checks.values()) else "degraded"
        return JSONResponse(content={"status": status, "checks": checks})

    @application.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        field_errors = [
            FieldError(
                field=".".join(str(part) for part in error["loc"] if part != "body"),
                code=str(error["type"]),
                message="请求字段无效。",
            )
            for error in exc.errors()
        ]
        payload = ErrorResponse(
            code="request.validation_failed",
            message="请求参数无效，请检查后重试。",
            request_id=_request_id(request),
            field_errors=field_errors,
        )
        return JSONResponse(status_code=422, content=payload.model_dump(mode="json"))

    @application.exception_handler(IdentityError)
    async def identity_error(request: Request, exc: IdentityError) -> JSONResponse:
        response = _error_response(
            request,
            status_code=exc.status_code,
            code=exc.code,
            message=exc.message,
        )
        if exc.status_code == 429:
            response.headers["Retry-After"] = "60"
        return response

    @application.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException) -> JSONResponse:
        return _error_response(
            request,
            status_code=exc.status_code,
            code="request.http_error",
            message="请求处理失败，请稍后重试。",
        )

    @application.exception_handler(Exception)
    async def unhandled_error(request: Request, exc: Exception) -> JSONResponse:
        LOGGER.error("unhandled_exception", error_type=type(exc).__name__)
        return _error_response(
            request,
            status_code=500,
            code="server.internal_error",
            message="服务暂时不可用，请稍后重试。",
        )

    application.openapi = configure_openapi(application)
    return application


app = create_app()
