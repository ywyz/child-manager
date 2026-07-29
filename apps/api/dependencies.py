"""API 装配所需健康检查依赖。"""

import os
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path
from typing import Annotated

import psycopg
from fastapi import Cookie, Depends
from redis.asyncio import Redis

from packages.backend.identity.service import IdentityError, IdentityService, SessionUser
from packages.backend.jobs.ai_retry import AiRetryService
from packages.backend.jobs.query_service import JobQueryService
from packages.backend.lesson_plans.ai_adoption import AiAdoptionService
from packages.backend.lesson_plans.ai_generation import AiGenerationService
from packages.backend.lesson_plans.reflection import ReflectionGenerationService
from packages.backend.lesson_plans.service import LessonPlanService
from packages.backend.prompts.service import PromptService
from packages.backend.settings.ai_models import AiModelService
from packages.backend.settings.service import SettingsService

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


def identity_service() -> IdentityService:
    return IdentityService.from_environment()


IdentityServiceDependency = Annotated[IdentityService, Depends(identity_service)]


def settings_service() -> SettingsService:
    return SettingsService.from_environment()


SettingsServiceDependency = Annotated[SettingsService, Depends(settings_service)]


def lesson_plan_service() -> LessonPlanService:
    return LessonPlanService.from_environment()


LessonPlanServiceDependency = Annotated[LessonPlanService, Depends(lesson_plan_service)]


def ai_generation_service() -> AiGenerationService:
    return AiGenerationService.from_environment()


AiGenerationServiceDependency = Annotated[
    AiGenerationService,
    Depends(ai_generation_service),
]


def reflection_generation_service() -> ReflectionGenerationService:
    return ReflectionGenerationService.from_environment()


ReflectionGenerationServiceDependency = Annotated[
    ReflectionGenerationService,
    Depends(reflection_generation_service),
]


def ai_adoption_service() -> AiAdoptionService:
    return AiAdoptionService.from_environment()


AiAdoptionServiceDependency = Annotated[
    AiAdoptionService,
    Depends(ai_adoption_service),
]


def ai_retry_service() -> AiRetryService:
    return AiRetryService.from_environment()


AiRetryServiceDependency = Annotated[AiRetryService, Depends(ai_retry_service)]


def ai_model_service() -> AiModelService:
    return AiModelService.from_environment()


AiModelServiceDependency = Annotated[AiModelService, Depends(ai_model_service)]


def prompt_service() -> PromptService:
    return PromptService.from_environment()


PromptServiceDependency = Annotated[PromptService, Depends(prompt_service)]


def job_query_service() -> JobQueryService:
    return JobQueryService.from_environment()


JobQueryServiceDependency = Annotated[JobQueryService, Depends(job_query_service)]


def authenticated_session(
    service: IdentityServiceDependency,
    child_manager_access: Annotated[str | None, Cookie()] = None,
) -> SessionUser:
    if not child_manager_access:
        raise IdentityError(401, "auth.unauthenticated", "请先登录。")
    return service.authenticate_access(child_manager_access)


AuthenticatedSessionDependency = Annotated[SessionUser, Depends(authenticated_session)]


def current_session(session: AuthenticatedSessionDependency) -> SessionUser:
    IdentityService.require_business_access(session)
    return session


CurrentSessionDependency = Annotated[SessionUser, Depends(current_session)]


def admin_session(session: CurrentSessionDependency) -> SessionUser:
    IdentityService.require_admin(session)
    return session


AdminSessionDependency = Annotated[SessionUser, Depends(admin_session)]
