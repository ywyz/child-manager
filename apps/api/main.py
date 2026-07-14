import json
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from starlette.responses import JSONResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title="幼儿园教育管理系统 API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
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
                                "message": {
                                    "type": "string",
                                    "nullable": True,
                                },
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
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/ErrorResponse",
                        },
                    },
                },
            },
        },
    }
    app.openapi_schema = openapi_schema
    return openapi_schema


app.openapi = custom_openapi

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    elapsed = time.time() - start_time
    response.headers["X-Response-Time"] = f"{elapsed:.3f}s"
    return response


@app.get("/health/live")
async def health_live(request: Request):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    return {
        "status": "healthy",
        "component": "api",
        "request_id": request_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/health/ready")
async def health_ready(request: Request):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    return {
        "status": "healthy",
        "component": "api",
        "request_id": request_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    return JSONResponse(
            status_code=422,
            content={
                "code": "VALIDATION_ERROR",
                "message": "请求参数验证失败",
                "detail": str(exc),
                "request_id": request_id,
            },
        )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_ERROR",
            "message": "服务器内部错误",
            "detail": str(exc),
            "request_id": request_id,
        },
    )


def main():
    import uvicorn

    from packages.backend.bootstrap.config import settings

    uvicorn.run(
        "apps.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )


if __name__ == "__main__":
    main()
