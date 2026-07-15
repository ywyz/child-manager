import os
from collections.abc import Awaitable, Callable
from datetime import UTC
from uuid import uuid7

import structlog
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

LOGGER = structlog.get_logger(__name__)


def _request_id(request: Request) -> str:
    return str(request.state.request_id)


def _error_response(request: Request, *, status_code: int, code: str, message: str) -> JSONResponse:
    payload = {
        "code": code,
        "message": message,
        "request_id": _request_id(request),
    }
    return JSONResponse(status_code=status_code, content=payload)


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
    from pathlib import Path

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
        client = Redis.from_url(redis_url, socket_connect_timeout=1, socket_timeout=1)
        try:
            return bool(await client.ping())
        finally:
            await client.aclose()

    async def path_check(path: Path, *, writable: bool = False) -> bool:
        return path.is_dir() and (not writable or os.access(path, os.W_OK))

    async def file_check(path: Path) -> bool:
        return path.is_file()

    export_storage = (
        path_check(Path(runtime_root_value) / "exports", writable=True)
        if runtime_root_value
        else _runtime_storage_unconfigured
    )
    security_values = (
        os.environ.get("CHILD_MANAGER_JWT_SIGNING_KEY"),
        os.environ.get("CHILD_MANAGER_CSRF_SIGNING_KEY"),
    )

    return HealthDependencies(
        database=database_check,
        redis=redis_check,
        ai=_ai_unconfigured,
        calendar=_calendar_library_available,
        template=file_check(repository_root / "templates/teacherplan/teacherplan.docx"),
        export_storage=export_storage,
        security_ready=all(value is not None and bool(value.strip()) for value in security_values),
    )


def custom_openapi(application: FastAPI) -> dict[str, object]:
    if application.openapi_schema:
        return application.openapi_schema
    from fastapi.openapi.utils import get_openapi

    openapi_schema = get_openapi(
        title=application.title,
        version=application.version,
        routes=application.routes,
    )
    openapi_schema["components"] = {
        "schemas": {
            "ErrorResponse": {
                "type": "object",
                "properties": {
                    "code": {"type": "string"},
                    "message": {"type": "string"},
                    "detail": {"type": "string", "nullable": True},
                    "request_id": {"type": "string", "nullable": True},
                },
                "required": ["code", "message"],
            },
            "HealthResponse": {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "checks": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "status": {"type": "string"},
                                "message": {"type": "string", "nullable": True},
                            },
                        },
                    },
                    "timestamp": {"type": "string"},
                },
                "required": ["status", "checks", "timestamp"],
            },
        },
        "responses": {
            "ErrorResponse": {
                "description": "错误响应",
                "content": {
                    "application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}},
                },
            },
        },
    }
    application.openapi_schema = openapi_schema
    return openapi_schema


def create_app(dependencies: HealthDependencies | None = None) -> FastAPI:
    health = dependencies or build_health_dependencies()
    application = FastAPI(title="Child Manager API")
    application.openapi = lambda: custom_openapi(application)

    @application.middleware("http")
    async def request_context_middleware(request: Request, call_next) -> JSONResponse:
        import re

        request_id_pattern = re.compile(r"^[A-Za-z0-9._-]{1,128}$")
        headers = request.headers
        supplied_request_id = headers.get("x-request-id", "")
        if supplied_request_id and len(supplied_request_id) <= 128:
            request_id = supplied_request_id
        else:
            request_id = str(uuid7())
        supplied_trace_id = headers.get("x-trace-id", "")
        trace_id = (
            supplied_trace_id if request_id_pattern.fullmatch(supplied_trace_id) else request_id
        )
        state = request.state
        state.request_id = request_id
        state.trace_id = trace_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    @application.get("/health/live")
    async def live(request: Request) -> dict[str, object]:
        from datetime import datetime

        return {
            "status": "healthy",
            "component": "api",
            "request_id": request.state.request_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "checks": {},
        }

    @application.get("/health/ready")
    async def ready(request: Request) -> JSONResponse:
        from datetime import datetime

        database_ready = await _safe_check("database", health.database)
        if not database_ready:
            return _error_response(
                request,
                status_code=503,
                code="database.unavailable",
                message="数据库暂不可用,请稍后重试。",
            )
        if not health.security_ready:
            return _error_response(
                request,
                status_code=503,
                code="configuration.unavailable",
                message="服务端安全配置不可用。",
            )

        checks = {
            "database": "healthy",
            "security": "healthy",
            "redis": "healthy"
            if await _safe_check("redis", health.redis)
            else "degraded",
            "ai": "healthy"
            if await _safe_check("ai", health.ai)
            else "degraded",
            "calendar": "healthy"
            if await _safe_check("calendar", health.calendar)
            else "degraded",
            "template": "healthy"
            if await _safe_check("template", health.template)
            else "degraded",
            "export_storage": (
                "healthy"
                if await _safe_check("export_storage", health.export_storage)
                else "degraded"
            ),
        }
        status = (
            "healthy"
            if all(value == "healthy" for value in checks.values())
            else "degraded"
        )
        return JSONResponse(
            content={
                "status": status,
                "component": "api",
                "request_id": request.state.request_id,
                "timestamp": datetime.now(UTC).isoformat(),
                "checks": checks,
            }
        )

    @application.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        field_errors = []
        for error in exc.errors():
            field = ".".join(str(part) for part in error["loc"] if part != "body")
            field_errors.append(
                {
                    "field": field,
                    "code": str(error["type"]),
                    "message": "请求字段无效。",
                }
            )
        payload = {
            "code": "request.validation_error",
            "message": "请求参数无效,请检查后重试。",
            "request_id": _request_id(request),
            "field_errors": field_errors,
        }
        return JSONResponse(status_code=422, content=payload)

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


def main() -> None:
    import argparse

    import uvicorn

    parser = argparse.ArgumentParser(description="启动 Child Manager API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=28000, type=int)
    args = parser.parse_args()

    uvicorn.run(
        "apps.api.main:app",
        host=args.host,
        port=args.port,
        reload=False,
    )


if __name__ == "__main__":
    main()
