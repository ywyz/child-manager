"""桌面应用唯一 composition root。"""

from __future__ import annotations

import json
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, cast
from uuid import UUID

from PySide6.QtWidgets import QWidget

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
from kindergarten_manager.application.lesson_plans import LessonPlanService
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
from kindergarten_manager.infrastructure.ai.client import AiClientError, ProviderNeutralAiClient
from kindergarten_manager.infrastructure.ai.prompts import load_default_prompt
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


def _shutdown(runtime: _AiRuntimeAdapter) -> None:
    runtime.shutdown()


@dataclass(frozen=True, slots=True)
class _SectionOutcome:
    section_code: str
    result_json: str | None
    error_code: str | None


@dataclass(frozen=True, slots=True)
class _BatchOutcome:
    operation_id: UUID
    outcomes: tuple[_SectionOutcome, ...]


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
        self._bridge.submit(operation_id, self._run, work)

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
        if not isinstance(frozen_input, GenerationWork):
            return CommandResult.failure(
                "ai.input_invalid",
                message="AI 生成输入无效",
            )
        configuration = self._repository.get_configuration()
        if (
            configuration is None
            or not configuration.enabled
            or not configuration.base_url
            or not configuration.model_name
            or self._credential_store is None
        ):
            return CommandResult.success(
                _BatchOutcome(
                    operation_id=self._operation_id_for(frozen_input),
                    outcomes=tuple(
                        _SectionOutcome(section, None, "ai.configuration_incomplete")
                        for section in frozen_input.sections
                    ),
                ),
                message="AI 未配置",
            )
        try:
            api_key = self._credential_store.require("ai.current")
        except CredentialError as error:
            return CommandResult.success(
                _BatchOutcome(
                    operation_id=self._operation_id_for(frozen_input),
                    outcomes=tuple(
                        _SectionOutcome(section, None, error.code)
                        for section in frozen_input.sections
                    ),
                ),
                message="AI 凭据不可用",
            )

        operation_id = frozen_input.operation_id
        outcomes: list[_SectionOutcome] = []
        total = len(frozen_input.frozen_inputs)
        for index, section_input in enumerate(frozen_input.frozen_inputs, start=1):
            if cancellation.cancel_requested:
                return CommandResult.failure(
                    "operation.cancelled",
                    message="AI 生成已取消",
                )
            progress("generating", index - 1, total, "AI 正在生成，请稍候")
            prompt = self._repository.get_prompt_override(section_input.section_code)
            if prompt is None:
                prompt = load_default_prompt(section_input.section_code)
            prompt = f"{prompt}\n\n冻结输入 JSON：{section_input.payload_json}"
            outcome = self._generate_section(
                section_code=section_input.section_code,
                base_url=configuration.base_url,
                model_name=configuration.model_name,
                api_key=api_key,
                prompt=prompt,
            )
            outcomes.append(outcome)
            progress("generating", index, total, "AI 栏目处理完成")
        return CommandResult.success(
            _BatchOutcome(operation_id=operation_id, outcomes=tuple(outcomes)),
            message="AI 生成已完成",
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

    def _operation_id_for(self, work: GenerationWork) -> UUID:
        return work.operation_id

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
    ) -> None:
        self._workspace = workspace
        self._ai_settings = ai_settings
        self._coordinator = coordinator

    @property
    def setup_complete(self) -> bool:
        return self._workspace.setup_complete

    def complete_setup(self, values: dict[str, str]) -> None:
        self._workspace.complete_setup(values)

    def load_plan_context(self) -> DailyPlanContext:
        return self._workspace.load_plan_context()

    def select_plan_context(self, class_id: int, plan_date: date) -> DailyPlanContext:
        self._coordinator.clear_view()
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

    def adopt_ai_preview(self, preview_id: int) -> object:
        return self._coordinator.adopt(preview_id)

    def reject_ai_preview(self, preview_id: int) -> PreviewView:
        return self._coordinator.reject(preview_id)

    def cancel_ai_generation(self, operation_id: UUID) -> CommandResult[None]:
        return self._coordinator.cancel(operation_id)


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
    credential_store: CredentialStore | None = None
    if sys.platform == "win32":
        try:
            credential_store = create_credential_store()
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
    services = _DesktopServiceFacade(workspace, ai_settings, coordinator)
    return DesktopMainWindow(
        cast(DesktopServices, services),
        on_close=lambda: _shutdown(runtime),
    )
