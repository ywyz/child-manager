"""桌面应用唯一 composition root。"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from hashlib import sha256
from pathlib import Path
from typing import Any, cast
from uuid import UUID, uuid4

from PySide6.QtWidgets import QWidget

from kindergarten_manager.application.agent_context import (
    minimize_current_plan_result,
    project_plan_content_for_intent,
)
from kindergarten_manager.application.agent_runtime import (
    ActiveScope,
    AgentContext,
    AgentRuntime,
    AgentTurnOutcome,
    ContextFact,
    EntityRevision,
    Permission,
    ProviderToolCall,
    ProviderTurnRequest,
    ProviderTurnResult,
    ToolResult,
)
from kindergarten_manager.application.agent_tools import (
    REGISTERED_PLAN_FIELD_PATHS,
    build_read_draft_registry,
)
from kindergarten_manager.application.ai_generation import (
    AiGenerationCoordinator,
    CoordinatorState,
    GenerationWork,
    PreviewView,
)
from kindergarten_manager.application.ai_settings import AiSettingsService, AiSettingsView
from kindergarten_manager.application.bootstrap import BootstrapService
from kindergarten_manager.application.dto import (
    CancellationToken,
    CommandResult,
    OperationAccepted,
)
from kindergarten_manager.application.lesson_plans import LessonPlanEditorState, LessonPlanService
from kindergarten_manager.application.settings import SettingsService
from kindergarten_manager.application.workspace import (
    DailyPlanContext,
    DailyPlanWorkspace,
    DesktopSettingsContext,
)
from kindergarten_manager.domain.ai import (
    AiOutputValidationError,
    canonical_json,
    validate_section_output,
)
from kindergarten_manager.infrastructure.ai.agent_provider import OpenAICompatibleAgentProvider
from kindergarten_manager.infrastructure.ai.client import AiClientError, ProviderNeutralAiClient
from kindergarten_manager.infrastructure.ai.prompts import resolve_prompt
from kindergarten_manager.infrastructure.credentials import (
    CredentialError,
    CredentialStore,
    create_credential_store,
)
from kindergarten_manager.infrastructure.database.engine import create_session_factory
from kindergarten_manager.infrastructure.database.repositories import (
    AiRepository,
    LessonPlanRepository,
    SettingsRepository,
    WorkspaceRepository,
)
from kindergarten_manager.infrastructure.exports.teacherplan_renderer import TeacherplanRenderer
from kindergarten_manager.infrastructure.paths import DesktopPaths
from kindergarten_manager.ui.main_window import DesktopMainWindow
from kindergarten_manager.ui.ports import DesktopServices
from kindergarten_manager.ui.runtime import ProgressReporter, RuntimeBridge

TEMPLATE_SHA256 = "72ee26e7cb8f510a11bc303b7a967c2a375fe436b5c8a72822ee9ccbfe235043"


def _now_utc_ms() -> int:
    return time.time_ns() // 1_000_000


def _shutdown(
    ai_runtime: _AiRuntimeAdapter, agent_runtime: AgentRuntime, bridge: RuntimeBridge
) -> None:
    agent_runtime._invalidate()
    bridge.shutdown(5_000)
    ai_runtime.shutdown()


@dataclass(frozen=True, slots=True)
class _SectionOutcome:
    section_code: str
    result_json: str | None
    error_code: str | None


@dataclass(frozen=True, slots=True)
class _BatchOutcome:
    operation_id: UUID
    outcomes: tuple[_SectionOutcome, ...]


@dataclass(frozen=True, slots=True)
class _FrozenProviderSection:
    section_code: str
    prompt: str


@dataclass(frozen=True, slots=True)
class _FrozenProviderConfiguration:
    base_url: str
    model_name: str
    api_key: str = field(repr=False)
    sections: tuple[_FrozenProviderSection, ...] = ()


@dataclass(frozen=True, slots=True)
class _PreparedGenerationWork:
    work: GenerationWork
    provider: _FrozenProviderConfiguration | None
    preparation_error_code: str | None = None


class _AiRuntimeAdapter:
    """把冻结生成请求放入 Qt 线程池，并只在 UI 线程回送不可变结果。"""

    def __init__(
        self,
        *,
        bridge: RuntimeBridge,
        repository: AiRepository,
        credential_store: CredentialStore | None,
        client: ProviderNeutralAiClient,
    ) -> None:
        self._bridge = bridge
        self._repository = repository
        self._credential_store = credential_store
        self._client = client
        self._coordinator: AiGenerationCoordinator | None = None
        self._pending: dict[UUID, tuple[str, ...]] = {}
        self._delivered: set[UUID] = set()
        bridge.succeeded.connect(self._on_succeeded)
        bridge.finished.connect(self._on_finished)

    def bind(self, coordinator: AiGenerationCoordinator) -> None:
        self._coordinator = coordinator

    def submit(self, operation_id: UUID, work: object) -> None:
        if not isinstance(work, GenerationWork):
            raise TypeError("AI 后台任务输入类型无效")
        self._pending[operation_id] = work.sections
        self._bridge.submit(operation_id, self._run, self._prepare(work))

    def cancel(self, operation_id: UUID) -> bool:
        return self._bridge.cancel(operation_id)

    def shutdown(self) -> bool:
        if self._coordinator is not None:
            self._coordinator.close()
        return self._bridge.shutdown(5_000)

    def _run(
        self,
        frozen_input: object,
        cancellation: CancellationToken,
        progress: ProgressReporter,
    ) -> CommandResult[object]:
        if not isinstance(frozen_input, _PreparedGenerationWork):
            return CommandResult.failure(
                "ai.input_invalid",
                message="AI 生成输入无效",
            )
        work = frozen_input.work
        provider = frozen_input.provider
        if provider is None:
            return CommandResult.success(
                _BatchOutcome(
                    operation_id=work.operation_id,
                    outcomes=tuple(
                        _SectionOutcome(
                            section,
                            None,
                            frozen_input.preparation_error_code or "ai.configuration_incomplete",
                        )
                        for section in work.sections
                    ),
                ),
                message="AI 未配置",
            )

        operation_id = work.operation_id
        outcomes: list[_SectionOutcome] = []
        total = len(provider.sections)
        for index, section_input in enumerate(provider.sections, start=1):
            if cancellation.cancel_requested:
                return CommandResult.failure(
                    "operation.cancelled",
                    message="AI 生成已取消",
                )
            progress("generating", index - 1, total, "AI 正在生成，请稍候")
            outcome = self._generate_section(
                section_code=section_input.section_code,
                base_url=provider.base_url,
                model_name=provider.model_name,
                api_key=provider.api_key,
                prompt=section_input.prompt,
            )
            outcomes.append(outcome)
            progress("generating", index, total, "AI 栏目处理完成")
        return CommandResult.success(
            _BatchOutcome(operation_id=operation_id, outcomes=tuple(outcomes)),
            message="AI 生成已完成",
        )

    def _prepare(self, work: GenerationWork) -> _PreparedGenerationWork:
        configuration = self._repository.get_configuration()
        if (
            configuration is None
            or not configuration.enabled
            or not configuration.base_url
            or not configuration.model_name
            or self._credential_store is None
        ):
            return _PreparedGenerationWork(work, None, "ai.configuration_incomplete")
        try:
            api_key = self._credential_store.require("ai.current")
        except CredentialError as error:
            return _PreparedGenerationWork(work, None, error.code)
        sections: list[_FrozenProviderSection] = []
        for section_input in work.frozen_inputs:
            prompt = resolve_prompt(
                section_input.section_code,
                self._repository.get_prompt_override(section_input.section_code),
            )
            sections.append(
                _FrozenProviderSection(
                    section_code=section_input.section_code,
                    prompt=f"{prompt}\n\n冻结输入 JSON：{section_input.payload_json}",
                )
            )
        return _PreparedGenerationWork(
            work,
            _FrozenProviderConfiguration(
                base_url=configuration.base_url,
                model_name=configuration.model_name,
                api_key=api_key,
                sections=tuple(sections),
            ),
        )

    def _generate_section(
        self,
        *,
        section_code: str,
        base_url: str,
        model_name: str,
        api_key: str,
        prompt: str,
    ) -> _SectionOutcome:
        last_validation_category = "wrong_type"

        def validate(raw: dict[str, Any]) -> dict[str, Any]:
            nonlocal last_validation_category
            try:
                return validate_section_output(section_code, raw)
            except AiOutputValidationError as error:
                last_validation_category = error.category
                raise AiClientError(
                    f"ai.invalid_output.{error.category}",
                    "AI 返回内容不符合预期结构",
                    retryable=True,
                ) from None

        try:
            validated = self._client.generate_structured(
                base_url=base_url,
                api_key=api_key,
                model_name=model_name,
                prompt=prompt,
                validator=validate,
            )
        except AiClientError as error:
            if error.code.startswith("ai.invalid_output."):
                return _SectionOutcome(
                    section_code,
                    None,
                    f"ai.invalid_output.{last_validation_category}",
                )
            return _SectionOutcome(section_code, None, error.code)
        return _SectionOutcome(section_code, canonical_json(validated), None)

    def _on_succeeded(self, result: CommandResult[object]) -> None:
        outcome = result.value
        if not isinstance(outcome, _BatchOutcome) or self._coordinator is None:
            return
        self._delivered.add(outcome.operation_id)
        for section in outcome.outcomes:
            if section.result_json is not None:
                try:
                    self._coordinator.accept_result(
                        outcome.operation_id,
                        section.section_code,
                        json.loads(section.result_json),
                    )
                except Exception:
                    self._coordinator.accept_failure(
                        outcome.operation_id,
                        section.section_code,
                        "ai.preview_persistence_failed",
                    )
            else:
                self._coordinator.accept_failure(
                    outcome.operation_id,
                    section.section_code,
                    section.error_code or "ai.generation_failed",
                )

    def _on_finished(self, operation_id: UUID) -> None:
        sections = self._pending.pop(operation_id, ())
        if operation_id not in self._delivered and self._coordinator is not None:
            for section in sections:
                self._coordinator.accept_failure(
                    operation_id,
                    section,
                    "ai.generation_failed",
                )
        self._delivered.discard(operation_id)


class _DesktopServiceFacade:
    def __init__(
        self,
        workspace: DailyPlanWorkspace,
        ai_settings: AiSettingsService,
        coordinator: AiGenerationCoordinator,
        agent_runtime: AgentRuntime,
        agent_bridge: RuntimeBridge,
    ) -> None:
        self._workspace = workspace
        self._ai_settings = ai_settings
        self._coordinator = coordinator
        self._agent_runtime = agent_runtime
        self._agent_state = _AgentUiState(None, "idle", "Agent 已就绪")
        agent_bridge.succeeded.connect(self._on_agent_succeeded)
        agent_bridge.failed.connect(self._on_agent_failed)
        agent_bridge.finished.connect(self._on_agent_finished)

    @property
    def setup_complete(self) -> bool:
        return self._workspace.setup_complete

    def complete_setup(self, values: dict[str, str]) -> None:
        self._workspace.complete_setup(values)

    def load_plan_context(self) -> DailyPlanContext:
        return self._workspace.load_plan_context()

    def select_plan_context(self, class_id: int, plan_date: date) -> DailyPlanContext:
        self._coordinator.clear_view()
        self._agent_runtime._invalidate()
        if self._agent_state.running_operation_id is not None:
            self._agent_runtime.cancel(self._agent_state.running_operation_id)
        return self._workspace.select_plan_context(class_id, plan_date)

    def load_current_plan(self) -> dict[str, Any]:
        return self._workspace.load_current_plan()

    def save_current_plan(self, content: dict[str, Any]) -> None:
        self._workspace.save_current_plan(content)

    def load_settings(self) -> DesktopSettingsContext:
        return self._workspace.load_settings()

    def update_settings(self, values: dict[str, str]) -> DesktopSettingsContext:
        return self._workspace.update_settings(values)

    def suggested_export_filename(self) -> str:
        return self._workspace.suggested_export_filename()

    def export_current_day(self, destination: Path) -> None:
        self._workspace.export_current_day(destination)

    def load_ai_settings(self) -> AiSettingsView:
        return self._ai_settings.load()

    def save_ai_settings(self, values: dict[str, object]) -> AiSettingsView:
        return self._ai_settings.save(values)

    def reset_ai_prompt(self, prompt_code: str) -> str:
        return self._ai_settings.reset_prompt(prompt_code)

    def load_ai_generation_state(self) -> CoordinatorState:
        return self._coordinator.state()

    def start_ai_generation(
        self,
        section_code: str,
        teacher_context: str,
    ) -> OperationAccepted:
        if section_code == "daily_reflection":
            return self._coordinator.start_reflection(
                self._workspace.current_plan_id(),
                teacher_context,
            )
        return self._coordinator.start_single(
            self._workspace.current_plan_id(),
            section_code,
            teacher_context,
        )

    def start_ai_batch(self, teacher_context: str) -> OperationAccepted:
        return self._coordinator.start_batch(
            self._workspace.current_plan_id(),
            teacher_context,
        )

    def adopt_ai_preview(self, preview_id: int) -> LessonPlanEditorState:
        adopted = self._coordinator.adopt(preview_id)
        return self._workspace.apply_ai_adoption(adopted)

    def reject_ai_preview(self, preview_id: int) -> PreviewView:
        return self._coordinator.reject(preview_id)

    def cancel_ai_generation(self, operation_id: UUID) -> CommandResult[None]:
        return self._coordinator.cancel(operation_id)

    def load_agent_state(self) -> _AgentUiState:
        return self._agent_state

    def load_agent_context_request(self) -> ActiveScope:
        plan = self._workspace.current_plan_state()
        return ActiveScope(
            class_id=plan.class_id,
            semester_id=plan.semester_id,
            lesson_plan_id=plan.id,
            plan_date=plan.plan_date,
        )

    def start_agent_turn(self, intent: str, context_request: object) -> OperationAccepted:
        if not isinstance(context_request, ActiveScope):
            raise TypeError("Agent Context 请求无效")
        if "直接修改" in intent or "总是允许" in intent:
            from kindergarten_manager.application.agent_runtime import AgentRuntimeError

            raise AgentRuntimeError("agent.tool_not_allowed", "当前阶段仅支持读取和草拟")
        accepted = self._agent_runtime.start_turn(intent, context_request)
        self._agent_state = _AgentUiState(
            accepted.operation_id,
            "running",
            "Agent 正在处理，请稍候",
        )
        return accepted

    def cancel_agent_turn(self, operation_id: UUID) -> ToolResult[None]:
        result = self._agent_runtime.cancel(operation_id)
        self._agent_state = _AgentUiState(None, "cancelled", result.message)
        return result

    def reject_agent_patch(self, patch_id: UUID) -> ToolResult[None]:
        result = self._agent_runtime.reject(patch_id)
        self._agent_state = _AgentUiState(None, "idle", result.message)
        return result

    def _on_agent_succeeded(self, result: CommandResult[object]) -> None:
        outcome = result.value
        if not isinstance(outcome, AgentTurnOutcome):
            return
        self._agent_state = _AgentUiState(
            None,
            "draft_ready" if outcome.patches else "succeeded",
            result.message,
            patches=outcome.patches,
            assistant_content=outcome.assistant_content,
        )

    def _on_agent_failed(self, result: CommandResult[object]) -> None:
        self._agent_state = _AgentUiState(None, "failed", result.message)

    def _on_agent_finished(self, operation_id: UUID) -> None:
        if self._agent_state.running_operation_id == operation_id:
            self._agent_state = _AgentUiState(None, "idle", "Agent 已就绪")


@dataclass(frozen=True, slots=True)
class _AgentUiState:
    running_operation_id: UUID | None
    status: str
    message: str
    patches: tuple[object, ...] = ()
    assistant_content: str | None = None


class _ConfiguredAgentProvider:
    def __init__(
        self,
        repository: AiRepository,
        credential_store: CredentialStore | None,
    ) -> None:
        self._repository = repository
        self._credential_store = credential_store

    def complete(self, request: ProviderTurnRequest) -> ProviderTurnResult:
        configuration = self._repository.get_configuration()
        if (
            configuration is None
            or not configuration.enabled
            or not configuration.base_url
            or not configuration.model_name
            or self._credential_store is None
        ):
            raise RuntimeError("Agent Provider 尚未配置")
        api_key = self._credential_store.require("ai.current")
        return OpenAICompatibleAgentProvider(
            base_url=configuration.base_url,
            api_key=api_key,
            model_name=configuration.model_name,
        ).complete(request)


def create_desktop_window(
    *,
    paths: DesktopPaths,
    template_path: Path,
    today: Callable[[], date] = date.today,
) -> QWidget:
    startup = BootstrapService(paths).start()
    session_factory = create_session_factory(paths.database)
    workspace_repository = WorkspaceRepository(session_factory)
    workspace = DailyPlanWorkspace(
        settings=SettingsService(
            SettingsRepository(session_factory),
            now_utc_ms=_now_utc_ms,
        ),
        plans=LessonPlanService(
            LessonPlanRepository(session_factory),
            now_utc_ms=_now_utc_ms,
            author_name=workspace_repository.get_author_name,
        ),
        repository=workspace_repository,
        renderer=TeacherplanRenderer(template_path, expected_sha256=TEMPLATE_SHA256),
        today=today,
        setup_complete=startup.setup_complete,
    )
    ai_repository = AiRepository(session_factory)
    try:
        credential_store: CredentialStore | None = create_credential_store()
    except CredentialError:
        credential_store = None
    ai_settings = AiSettingsService(
        ai_repository,
        credential_store,
        now_utc_ms=_now_utc_ms,
    )
    runtime = _AiRuntimeAdapter(
        bridge=RuntimeBridge(max_workers=1),
        repository=ai_repository,
        credential_store=credential_store,
        client=ProviderNeutralAiClient(),
    )
    coordinator = AiGenerationCoordinator(
        runtime=runtime,
        store=ai_repository,
        clock_utc_ms=_now_utc_ms,
    )
    runtime.bind(coordinator)
    agent_bridge = RuntimeBridge(max_workers=1)

    def context_loader(scope: ActiveScope, intent: str) -> AgentContext:
        plan = workspace.current_plan_state()
        if scope.lesson_plan_id != plan.id or scope.class_id != plan.class_id:
            raise ValueError("Agent Context 已失效")
        now = datetime.now(UTC)
        return AgentContext(
            context_id=uuid4(),
            session_id=uuid4(),
            turn_id=uuid4(),
            created_at_utc=now,
            expires_at_utc=now + timedelta(minutes=5),
            locale="zh-CN",
            active_scope=scope,
            entity_revisions=(EntityRevision("lesson_plan", plan.id, plan.content_revision),),
            facts=tuple(
                ContextFact(
                    source_tool="lesson_plan.read_context",
                    entity_type="lesson_plan",
                    entity_id=plan.id,
                    field_path=field_path,
                    value=value,
                )
                for field_path, value in project_plan_content_for_intent(plan.content, intent)
            ),
            allowed_permissions=frozenset({Permission.READ, Permission.DRAFT}),
        )

    def _result(
        call: ProviderToolCall,
        context: AgentContext,
        value: object,
    ) -> ToolResult[object]:
        return ToolResult(
            call_id=call.call_id,
            tool_name=call.tool_name,
            permission=call.permission,
            status="ok",
            value=value,
            error_code=None,
            message="工具执行完成",
            retryable=False,
            observed_revisions=context.entity_revisions,
            redactions=(),
        )

    def read_current(call: ProviderToolCall, context: AgentContext) -> ToolResult[object]:
        plan_id = context.active_scope.lesson_plan_id
        if plan_id is None or call.arguments.get("plan_id") != plan_id:
            raise ValueError("READ Tool 不得越过当前教案范围")
        record = workspace.read_agent_current(plan_id)
        return _result(call, context, minimize_current_plan_result(record, context))

    def read_context(call: ProviderToolCall, context: AgentContext) -> ToolResult[object]:
        plan_id = context.active_scope.lesson_plan_id
        if plan_id is None or call.arguments.get("plan_id") != plan_id:
            raise ValueError("READ Tool 不得越过当前教案范围")
        return _result(call, context, workspace.read_agent_context(plan_id))

    def read_calendar(call: ProviderToolCall, context: AgentContext) -> ToolResult[object]:
        plan_date = context.active_scope.plan_date
        semester_id = context.active_scope.semester_id
        if (
            plan_date is None
            or semester_id is None
            or call.arguments.get("plan_date") != plan_date.isoformat()
        ):
            raise ValueError("READ Tool 不得越过当前日期范围")
        return _result(call, context, workspace.read_agent_calendar(semester_id, plan_date))

    def read_class_areas(call: ProviderToolCall, context: AgentContext) -> ToolResult[object]:
        class_id = context.active_scope.class_id
        if class_id is None or call.arguments.get("class_id") != class_id:
            raise ValueError("READ Tool 不得越过当前班级范围")
        return _result(call, context, workspace.read_agent_class_areas(class_id))

    def draft_patch(call: ProviderToolCall, context: AgentContext) -> ToolResult[object]:
        field_path = str(call.arguments.get("field_path", ""))
        if field_path not in REGISTERED_PLAN_FIELD_PATHS:
            raise ValueError("DRAFT Tool 字段未注册")
        after_value = call.arguments.get("after_value")
        content_fact = next(
            (fact.value for fact in context.facts if fact.field_path == field_path),
            None,
        )
        if content_fact is None:
            raise ValueError("DRAFT Tool 字段不在当前意图 Context 中")
        before: object = json.loads(str(content_fact))
        return _result(
            call,
            context,
            {
                "schema_version": 1,
                "target": {
                    "entity_type": "lesson_plan",
                    "entity_id": context.active_scope.lesson_plan_id,
                },
                "base_revisions": tuple(
                    {
                        "entity_type": revision.entity_type,
                        "entity_id": revision.entity_id,
                        "revision": revision.revision,
                    }
                    for revision in context.entity_revisions
                ),
                "operations": (
                    {
                        "field_path": field_path,
                        "before_sha256": sha256(canonical_json(before).encode()).hexdigest(),
                        "before_display": str(before)[:2_000],
                        "after_value": after_value,
                        "after_display": str(after_value)[:2_000],
                    },
                ),
                "warnings": ("这只是草案，不会修改教案",),
            },
        )

    registry = build_read_draft_registry(
        {
            "lesson_plan.read_current": read_current,
            "lesson_plan.read_context": read_context,
            "calendar.read_evaluation": read_calendar,
            "settings.read_class_areas": read_class_areas,
            "lesson_plan.draft_section_patch": draft_patch,
            "lesson_plan.draft_reflection_patch": draft_patch,
        }
    )
    agent_runtime = AgentRuntime(
        provider=_ConfiguredAgentProvider(ai_repository, credential_store),
        registry=registry,
        context_loader=context_loader,
        runtime_bridge=agent_bridge,
        monotonic_seconds=time.monotonic,
        max_tool_calls=6,
        max_response_chars=8_000,
        max_turn_seconds=300.0,
    )
    services = _DesktopServiceFacade(
        workspace,
        ai_settings,
        coordinator,
        agent_runtime,
        agent_bridge,
    )
    return DesktopMainWindow(
        cast(DesktopServices, services),
        on_close=lambda: _shutdown(runtime, agent_runtime, agent_bridge),
    )
