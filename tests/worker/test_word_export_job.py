"""T131/T138 Word Worker 只读冻结输入与幂等落位 RED。"""

import json
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from hashlib import sha256
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from uuid import UUID, uuid4

import pytest
from dramatiq import Retry

from apps.worker.actors import register_actors
from apps.worker.broker import build_test_broker
from packages.contracts.lesson_plans import PlanContentV1


@dataclass(frozen=True)
class Stored:
    file_size: int
    file_sha256: str


class FakeStore:
    def __init__(self) -> None:
        self.claimed = False
        self.completed: list[tuple[UUID, UUID, int, str]] = []
        self.failed: list[tuple[UUID, UUID, str]] = []
        self.context = {
            "kindergarten_name": "冻结幼儿园",
            "class_name": "冻结班级",
            "age_group_name": "中班",
            "semester_name": "冻结学期",
            "semester_start_date": "2026-02-01",
            "semester_end_date": "2026-06-30",
            "activity_date_text": "周（一）3月2日",
            "season": "spring",
            "authors": [{"display_name_snapshot": "冻结教师"}],
        }
        self.content = PlanContentV1.empty().model_dump(mode="json")
        self.content["morning_talk"] = {"topic": "冻结话题", "questions": []}
        self.export_id = uuid4()
        self.storage_key = f"{uuid4()}.docx"
        self.retry_delay_seconds: int | None = None
        self.handled_errors: list[tuple[UUID, UUID, str, str]] = []

    def claim(self, kindergarten_id: UUID, job_id: UUID, *, worker_id: str) -> bool:
        del kindergarten_id, job_id, worker_id
        if self.claimed:
            return False
        self.claimed = True
        return True

    def load_for_job(self, kindergarten_id: UUID, job_id: UUID) -> Any:
        return SimpleNamespace(
            kindergarten_id=kindergarten_id,
            job_id=job_id,
            id=self.export_id,
            storage_key=self.storage_key,
            context_snapshot=self.context,
            content_snapshot=self.content,
            content_schema_version=1,
            content_sha256=sha256(
                json.dumps(
                    self.content,
                    ensure_ascii=False,
                    separators=(",", ":"),
                    sort_keys=True,
                ).encode()
            ).hexdigest(),
            template_code="daily_activity_plan.v1",
            template_filename="teacherplan.docx",
            template_sha256="72ee26e7cb8f510a11bc303b7a967c2a375fe436b5c8a72822ee9ccbfe235043",
        )

    def publish_succeeded(
        self,
        kindergarten_id: UUID,
        export_id: UUID,
        *,
        worker_id: str,
        publish: Callable[[], Any],
        cleanup: Callable[[], None],
    ) -> bool:
        del worker_id, cleanup
        stored = publish()
        self.completed.append((kindergarten_id, export_id, stored.file_size, stored.file_sha256))
        return True

    def mark_failed(
        self,
        kindergarten_id: UUID,
        export_id: UUID,
        *,
        worker_id: str,
        error_code: str,
        error_summary: str,
    ) -> bool:
        del worker_id, error_summary
        self.failed.append((kindergarten_id, export_id, error_code))
        return True

    def handle_error(
        self,
        kindergarten_id: UUID,
        export_id: UUID,
        *,
        worker_id: str,
        error_code: str,
        error_summary: str,
        retryable: bool,
    ) -> int | None:
        del error_summary
        self.handled_errors.append((kindergarten_id, export_id, worker_id, error_code))
        if retryable and self.retry_delay_seconds is not None:
            return self.retry_delay_seconds
        self.failed.append((kindergarten_id, export_id, error_code))
        return None


class FakeRenderer:
    def __init__(self) -> None:
        self.calls: list[tuple[Mapping[str, Any], Mapping[str, Any]]] = []

    def render(
        self,
        *,
        context_snapshot: Mapping[str, Any],
        content_snapshot: Mapping[str, Any],
    ) -> bytes:
        self.calls.append((context_snapshot, content_snapshot))
        return b"frozen-word"


class FailingRenderer(FakeRenderer):
    def render(
        self,
        *,
        context_snapshot: Mapping[str, Any],
        content_snapshot: Mapping[str, Any],
    ) -> bytes:
        super().render(
            context_snapshot=context_snapshot,
            content_snapshot=content_snapshot,
        )
        raise OSError("temporary renderer failure")


class FakeStorage:
    def __init__(self) -> None:
        self.writes: list[tuple[str, bytes]] = []
        self.deleted: list[str] = []
        self._existing: set[str] = set()

    def write_atomic(self, storage_key: str, chunks: Iterable[bytes]) -> Stored:
        if storage_key in self._existing:
            raise FileExistsError(storage_key)
        payload = b"".join(chunks)
        self.writes.append((storage_key, payload))
        self._existing.add(storage_key)
        return Stored(file_size=len(payload), file_sha256="2" * 64)

    def delete(self, storage_key: str) -> None:
        if storage_key in self._existing:
            self._existing.remove(storage_key)
            self.deleted.append(storage_key)


def _runner_type() -> type[Any]:
    try:
        module = import_module("packages.backend.exports.runner")
    except ModuleNotFoundError:
        pytest.fail("T138 WordExportRunner 尚未实现")
    runner = getattr(module, "WordExportRunner", None)
    if runner is None:
        pytest.fail("T138 WordExportRunner 尚未实现")
    return runner


def test_runner_uses_only_frozen_export_row_and_duplicate_delivery_is_noop() -> None:
    store = FakeStore()
    renderer = FakeRenderer()
    storage = FakeStorage()
    runner = _runner_type()(store=store, renderer=renderer, storage=storage)
    kindergarten_id, job_id = uuid4(), uuid4()

    runner.execute(kindergarten_id, job_id, worker_id="worker-1")
    runner.execute(kindergarten_id, job_id, worker_id="worker-2")

    assert renderer.calls == [(store.context, store.content)]
    assert len(storage.writes) == 1
    assert storage.writes[0][1] == b"frozen-word"
    assert len(store.completed) == 1
    assert store.failed == []


def test_transient_generation_failure_requests_authoritative_retry() -> None:
    module = import_module("packages.backend.exports.runner")
    store = FakeStore()
    store.retry_delay_seconds = 7
    runner = module.WordExportRunner(
        store=store,
        renderer=FailingRenderer(),
        storage=FakeStorage(),
    )

    with pytest.raises(module.WordExportRetry) as raised:
        runner.execute(uuid4(), uuid4(), worker_id="retry-worker")

    assert raised.value.delay_seconds == 7
    assert store.failed == []
    assert len(store.handled_errors) == 1


def test_invalid_frozen_hash_fails_without_rendering_or_storage_write() -> None:
    store = FakeStore()
    original_load = store.load_for_job

    def corrupt_load(kindergarten_id: UUID, job_id: UUID) -> Any:
        export = original_load(kindergarten_id, job_id)
        export.content_sha256 = "0" * 64
        return export

    store.load_for_job = corrupt_load  # type: ignore[method-assign]
    renderer = FakeRenderer()
    storage = FakeStorage()
    runner = _runner_type()(store=store, renderer=renderer, storage=storage)

    runner.execute(uuid4(), uuid4(), worker_id="integrity-worker")

    assert renderer.calls == []
    assert storage.writes == []
    assert store.failed[0][2] == "export.frozen_input_invalid"


def test_database_completion_failure_removes_already_placed_orphan() -> None:
    module = import_module("packages.backend.exports.runner")
    store = FakeStore()
    store.retry_delay_seconds = 5

    def fail_complete(
        *_args: object,
        publish: Callable[[], Any],
        cleanup: Callable[[], None],
        **_kwargs: object,
    ) -> bool:
        publish()
        cleanup()
        raise RuntimeError("database failed after atomic rename")

    store.publish_succeeded = fail_complete  # type: ignore[method-assign]
    renderer = FakeRenderer()
    storage = FakeStorage()
    runner = _runner_type()(store=store, renderer=renderer, storage=storage)

    with pytest.raises(module.WordExportRetry) as raised:
        runner.execute(uuid4(), uuid4(), worker_id="worker")

    assert raised.value.delay_seconds == 5
    assert len(storage.deleted) == 1


def test_stale_worker_cannot_delete_takeover_worker_success() -> None:
    store = FakeStore()
    storage = FakeStorage()
    runner = _runner_type()(store=store, renderer=FakeRenderer(), storage=storage)
    kindergarten_id, job_id = uuid4(), uuid4()
    completing_takeover = False

    def allow_both_workers(
        kindergarten_id: UUID,
        job_id: UUID,
        *,
        worker_id: str,
    ) -> bool:
        del kindergarten_id, job_id, worker_id
        return True

    def interleaved_completion(
        kindergarten_id: UUID,
        export_id: UUID,
        *,
        worker_id: str,
        publish: Callable[[], Any],
        cleanup: Callable[[], None],
    ) -> bool:
        nonlocal completing_takeover
        del cleanup
        if worker_id == "worker-a" and not completing_takeover:
            completing_takeover = True
            runner.execute(kindergarten_id, job_id, worker_id="worker-b")
            completing_takeover = False
            return False
        stored = publish()
        store.completed.append((kindergarten_id, export_id, stored.file_size, stored.file_sha256))
        return True

    store.claim = allow_both_workers  # type: ignore[method-assign]
    store.publish_succeeded = interleaved_completion  # type: ignore[method-assign]

    runner.execute(kindergarten_id, job_id, worker_id="worker-a")

    assert len(store.completed) == 1
    assert store.storage_key in storage._existing


def test_recovery_replaces_orphan_from_frozen_snapshot(tmp_path: Path) -> None:
    storage_module = import_module("packages.backend.integrations.files.export_storage")
    storage = storage_module.ExportStorage(
        tmp_path / "exports",
        temporary_root=tmp_path / "temporary",
    )
    store = FakeStore()
    storage.write_atomic(store.storage_key, [b"orphan-from-crashed-attempt"])
    runner = _runner_type()(
        store=store,
        renderer=FakeRenderer(),
        storage=storage,
    )

    runner.execute(uuid4(), uuid4(), worker_id="recovery-worker")

    assert storage.open_for_read(store.storage_key).read_bytes() == b"frozen-word"
    assert len(store.completed) == 1
    assert store.failed == []


def test_word_actor_accepts_only_job_id_and_resolves_tenant_before_running() -> None:
    broker = build_test_broker()
    kindergarten_id, job_id = uuid4(), uuid4()
    calls: list[tuple[UUID, UUID, str]] = []

    class ActorRunner:
        def execute(self, kindergarten_id: UUID, job_id: UUID, *, worker_id: str) -> None:
            calls.append((kindergarten_id, job_id, worker_id))

    class ActorResolver:
        def kindergarten_id_for_word_job(self, job_id: UUID) -> UUID | None:
            del job_id
            return kindergarten_id

    runner = ActorRunner()
    resolver = ActorResolver()

    actors = register_actors(
        broker,
        word_runner=runner,
        word_job_scope_resolver=resolver,
    )
    word_actor = next(actor for actor in actors if actor.actor_name == "word_export")
    result = word_actor.fn(str(job_id))

    assert result == str(job_id)
    assert len(calls) == 1
    assert calls[0][0:2] == (kindergarten_id, job_id)


def test_word_actor_translates_authoritative_retry_delay() -> None:
    module = import_module("packages.backend.exports.runner")
    broker = build_test_broker()
    kindergarten_id, job_id = uuid4(), uuid4()

    class RetryingRunner:
        def execute(self, kindergarten_id: UUID, job_id: UUID, *, worker_id: str) -> None:
            del kindergarten_id, job_id, worker_id
            raise module.WordExportRetry(11)

    class ActorResolver:
        def kindergarten_id_for_word_job(self, job_id: UUID) -> UUID | None:
            del job_id
            return kindergarten_id

    actors = register_actors(
        broker,
        word_runner=RetryingRunner(),
        word_job_scope_resolver=ActorResolver(),
    )
    word_actor = next(actor for actor in actors if actor.actor_name == "word_export")

    with pytest.raises(Retry) as raised:
        word_actor.fn(str(job_id))

    assert raised.value.delay == 11_000
