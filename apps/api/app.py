"""FastAPI 应用装配、统一异常转换与健康端点。"""

from collections.abc import Awaitable, Callable
from uuid import UUID

import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from apps.api.dependencies import HealthDependencies, build_health_dependencies
from apps.api.middleware import RequestContextMiddleware
from packages.contracts.common import (
    CONFIGURATION_UNAVAILABLE,
    DATABASE_UNAVAILABLE,
    ErrorResponse,
    FieldError,
)

LOGGER = structlog.get_logger(__name__)


def _request_id(request: Request) -> UUID:
    return UUID(str(request.state.request_id))


def _error_response(request: Request, *, status_code: int, code: str, message: str) -> JSONResponse:
    payload = ErrorResponse(
        code=code,
        message=message,
        request_id=_request_id(request),
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump(mode="json"))


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
            code="request.validation_error",
            message="请求参数无效，请检查后重试。",
            request_id=_request_id(request),
            field_errors=field_errors,
        )
        return JSONResponse(status_code=422, content=payload.model_dump(mode="json"))

    @application.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException) -> JSONResponse:
        return _error_response(
            request,
            status_code=exc.status_code,
            code="request.http_error",
            message=str(exc.detail),
        )

    return application


app = create_app()
