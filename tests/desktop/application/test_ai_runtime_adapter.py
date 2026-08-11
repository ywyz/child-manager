from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from types import SimpleNamespace
from typing import Any, cast
from uuid import UUID

from kindergarten_manager.app import _AiRuntimeAdapter, _DesktopServiceFacade
from kindergarten_manager.application.ai_generation import (
    AdoptedContent,
    FrozenGenerationInput,
    GenerationWork,
)
from kindergarten_manager.application.dto import CancellationToken
from kindergarten_manager.application.lesson_plans import LessonPlanEditorState, SaveResult
from kindergarten_manager.application.workspace import DailyPlanWorkspace
from kindergarten_manager.domain.content import PlanContentV1
from kindergarten_manager.ui.runtime import RuntimeBridge


class SignalStub:
    def connect(self, _slot: object) -> None:
        return None


@dataclass
class CapturingBridge:
    succeeded: SignalStub = field(default_factory=SignalStub)
    finished: SignalStub = field(default_factory=SignalStub)
    submitted: tuple[object, object] | None = None

    def submit(self, operation_id: UUID, task: object, frozen_input: object) -> None:
        del operation_id
        self.submitted = (task, frozen_input)

    def cancel(self, operation_id: UUID) -> bool:
        del operation_id
        return True


@dataclass
class MutableProviderRepository:
    base_url: str = "https://first.example.test/v1"
    model_name: str = "first-model"
    prompt: str = "first-prompt"
    reads: list[str] = field(default_factory=list)

    def get_configuration(self) -> object:
        self.reads.append("configuration")
        return SimpleNamespace(
            enabled=True,
            base_url=self.base_url,
            model_name=self.model_name,
        )

    def get_prompt_override(self, section_code: str) -> str:
        self.reads.append(f"prompt:{section_code}")
        return self.prompt


@dataclass
class MutableCredentials:
    secret: str = "first-secret"
    reads: int = 0

    def require(self, account: str) -> str:
        assert account == "ai.current"
        self.reads += 1
        return self.secret


@dataclass
class CapturingClient:
    calls: list[dict[str, object]] = field(default_factory=list)

    def generate_structured(self, **values: Any) -> object:
        self.calls.append(dict(values))
        validator = values["validator"]
        return validator({"topic": "春天", "questions": []})


def test_submit_freezes_configuration_credential_and_prompt_before_background_work() -> None:
    bridge = CapturingBridge()
    repository = MutableProviderRepository()
    credentials = MutableCredentials()
    client = CapturingClient()
    adapter = _AiRuntimeAdapter(
        bridge=cast(RuntimeBridge, bridge),
        repository=cast(Any, repository),
        credential_store=cast(Any, credentials),
        client=cast(Any, client),
    )
    work = GenerationWork(
        operation_id=UUID(int=1),
        plan_id=1,
        sections=("morning_talk",),
        frozen_inputs=(FrozenGenerationInput("morning_talk", '{"schema_code":"morning_talk"}'),),
    )

    adapter.submit(work.operation_id, work)
    assert bridge.submitted is not None
    task, frozen = bridge.submitted
    assert "first-secret" not in repr(frozen)
    reads_after_submit = list(repository.reads)
    credential_reads_after_submit = credentials.reads
    repository.base_url = "https://changed.example.test/v1"
    repository.model_name = "changed-model"
    repository.prompt = "changed-prompt"
    credentials.secret = "changed-secret"

    task_callable = cast(Callable[..., Any], task)
    result = task_callable(
        frozen,
        CancellationToken(),
        lambda _phase, _completed, _total, _message: None,
    )

    assert result.ok
    assert repository.reads == reads_after_submit
    assert credentials.reads == credential_reads_after_submit
    call = client.calls[0]
    assert call["base_url"] == "https://first.example.test/v1"
    assert call["model_name"] == "first-model"
    assert call["api_key"] == "first-secret"
    assert str(call["prompt"]).startswith("first-prompt")


@dataclass
class SavingPlans:
    base_revisions: list[int] = field(default_factory=list)

    def save_version(
        self,
        plan_id: int,
        base_revision: int,
        content: PlanContentV1,
        description: str | None = None,
    ) -> SaveResult:
        del content, description
        self.base_revisions.append(base_revision)
        return SaveResult(plan_id, base_revision + 1, 10)


@dataclass
class AdoptingCoordinator:
    adopted: AdoptedContent

    def adopt(self, preview_id: int) -> AdoptedContent:
        assert preview_id == 7
        return self.adopted


def test_facade_syncs_adopted_content_into_workspace_cache_and_revision() -> None:
    plans = SavingPlans()
    workspace = DailyPlanWorkspace(
        settings=cast(Any, object()),
        plans=cast(Any, plans),
        repository=cast(Any, object()),
        renderer=cast(Any, object()),
        today=lambda: date(2026, 9, 7),
        setup_complete=True,
    )
    workspace._current_plan = LessonPlanEditorState(
        id=1,
        class_id=2,
        semester_id=3,
        plan_date=date(2026, 9, 7),
        author_name="测试教师",
        content_revision=2,
        content=PlanContentV1(),
    )
    adopted_content = PlanContentV1.model_validate(
        {"morning_talk": {"topic": "AI 春天", "questions": []}}
    ).model_dump()
    coordinator = AdoptingCoordinator(AdoptedContent(adopted_content, 3))
    facade = _DesktopServiceFacade(
        workspace,
        cast(Any, object()),
        cast(Any, coordinator),
    )

    editor = facade.adopt_ai_preview(7)

    assert isinstance(editor, LessonPlanEditorState)
    assert workspace.load_current_plan()["morning_talk"]["topic"] == "AI 春天"
    workspace.save_current_plan(adopted_content)
    assert plans.base_revisions == [3]
