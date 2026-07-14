import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware


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
async def health_live():
    return {"status": "healthy", "component": "api"}


@app.get("/health/ready")
async def health_ready():
    return {"status": "healthy", "component": "api"}


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
