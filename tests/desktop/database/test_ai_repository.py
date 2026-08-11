from __future__ import annotations

import json
import sqlite3
from copy import deepcopy
from pathlib import Path
from uuid import UUID

import pytest
from sqlalchemy.exc import IntegrityError

from kindergarten_manager.application.ai_generation import AiGenerationCoordinator, PreviewView
from kindergarten_manager.domain.content import PlanContentV1
from kindergarten_manager.infrastructure.database.repositories import (
    AiRepository,
)
from kindergarten_manager.infrastructure.database.upgrade import upgrade_database
from tests.desktop.helpers import implemented


def _repository(database: Path) -> AiRepository:
    return AiRepository(database)


class NoopRuntime:
    def submit(self, operation_id: UUID, work: object) -> None:
        del operation_id, work

    def cancel(self, operation_id: UUID) -> bool:
        del operation_id
        return True


def _create_preview_through_application(
    repository: AiRepository,
    plan_id: int,
    result: dict[str, object],
) -> tuple[AiGenerationCoordinator, PreviewView]:
    coordinator = AiGenerationCoordinator(
        runtime=NoopRuntime(),
        store=repository,
        clock_utc_ms=lambda: 20,
    )
    operation = coordinator.start_single(plan_id, "morning_talk", "春季")
    preview = coordinator.accept_result(operation.operation_id, "morning_talk", result)
    assert preview is not None
    return coordinator, preview


def _seed_plan(database: Path) -> tuple[int, dict[str, object]]:
    implemented(lambda: upgrade_database(database))
    content = PlanContentV1.empty().model_dump(mode="json")
    with sqlite3.connect(database) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        class_id = connection.execute(
            "INSERT INTO class_groups(name, age_group, sort_order, is_active, "
            "created_at_utc_ms, updated_at_utc_ms) VALUES ('测试班', 'middle', 0, 1, 1, 1) "
            "RETURNING id"
        ).fetchone()[0]
        semester_id = connection.execute(
            "INSERT INTO semesters(name, start_date, end_date, is_current, "
            "created_at_utc_ms, updated_at_utc_ms) "
            "VALUES ('测试学期', '2026-09-01', '2027-01-31', 1, 1, 1) RETURNING id"
        ).fetchone()[0]
        plan_id = connection.execute(
            "INSERT INTO lesson_plans(class_id, semester_id, plan_date, author_name, "
            "content_schema_version, content_json, content_revision, "
            "created_at_utc_ms, updated_at_utc_ms) "
            "VALUES (?, ?, '2026-09-07', '测试教师', 1, ?, 1, 1, 1) RETURNING id",
            (class_id, semester_id, PlanContentV1.model_validate(content).canonical_json()),
        ).fetchone()[0]
    return int(plan_id), content


def test_ai_configuration_and_prompt_override_store_no_secret(tmp_path: Path) -> None:
    database = tmp_path / "desktop.sqlite3"
    implemented(lambda: upgrade_database(database))
    repository = _repository(database)

    saved = repository.save_configuration(
        base_url="https://ai.example.test/v1",
        model_name="fixture-model",
        credential_configured=True,
        enabled=True,
        now_utc_ms=10,
    )
    repository.set_prompt_override("morning_talk", "只返回结构化晨间谈话", now_utc_ms=11)

    assert saved.base_url == "https://ai.example.test/v1"
    assert saved.model_name == "fixture-model"
    assert saved.credential_configured is True
    assert repository.get_prompt_override("morning_talk") == "只返回结构化晨间谈话"
    repository.delete_prompt_override("morning_talk")
    assert repository.get_prompt_override("morning_talk") is None
    assert "fixture-api-key" not in database.read_bytes().decode("utf-8", errors="ignore")


def test_preview_adoption_snapshots_and_updates_content_in_one_transaction(tmp_path: Path) -> None:
    database = tmp_path / "desktop.sqlite3"
    plan_id, _content = _seed_plan(database)
    repository = _repository(database)
    result = {"topic": "春天", "questions": ["你看到了什么？"]}
    coordinator, preview = _create_preview_through_application(repository, plan_id, result)

    stored_preview = repository.get_preview(preview.preview_id)
    assert stored_preview is not None
    assert stored_preview.result["schema_version"] == 1

    adopted = coordinator.adopt(preview.preview_id)

    assert adopted.content_revision == 2
    assert adopted.content["morning_talk"] == result
    with sqlite3.connect(database) as connection:
        assert connection.execute(
            "SELECT reason, source_revision FROM lesson_plan_versions"
        ).fetchall() == [("pre_ai_adopt", 1)]
        assert connection.execute(
            "SELECT state, decided_at_utc_ms FROM ai_previews WHERE id = ?", (preview.preview_id,)
        ).fetchone() == ("adopted", 20)


def test_stale_preview_is_invalidated_without_snapshot_or_content_write(tmp_path: Path) -> None:
    database = tmp_path / "desktop.sqlite3"
    plan_id, content = _seed_plan(database)
    repository = _repository(database)
    coordinator, preview = _create_preview_through_application(
        repository,
        plan_id,
        {"topic": "AI 结果", "questions": ["为什么？"]},
    )
    changed = deepcopy(content)
    changed["morning_talk"] = {"topic": "教师已修改", "questions": []}
    changed_json = PlanContentV1.model_validate(changed).canonical_json()
    with sqlite3.connect(database) as connection:
        connection.execute(
            "UPDATE lesson_plans SET content_json = ?, content_revision = 2 WHERE id = ?",
            (changed_json, plan_id),
        )

    with pytest.raises(Exception) as captured:
        coordinator.adopt(preview.preview_id)

    assert getattr(captured.value, "code", None) == "ai.preview_stale"
    with sqlite3.connect(database) as connection:
        stored = json.loads(
            connection.execute(
                "SELECT content_json FROM lesson_plans WHERE id = ?", (plan_id,)
            ).fetchone()[0]
        )
        assert stored["morning_talk"]["topic"] == "教师已修改"
        assert connection.execute("SELECT COUNT(*) FROM lesson_plan_versions").fetchone() == (0,)
        assert connection.execute(
            "SELECT state, decided_at_utc_ms FROM ai_previews WHERE id = ?", (preview.preview_id,)
        ).fetchone() == ("invalidated", 20)


def test_ai_settings_aggregate_rolls_back_configuration_and_prompts_together(
    tmp_path: Path,
) -> None:
    database = tmp_path / "desktop.sqlite3"
    implemented(lambda: upgrade_database(database))
    repository = _repository(database)

    with pytest.raises(IntegrityError), repository.settings_transaction(10) as transaction:
        transaction.save_configuration(
            base_url="https://ai.example.test/v1",
            model_name="fixture-model",
            credential_configured=True,
            enabled=True,
        )
        transaction.set_prompt_override("not_allowed", "越界提示词")

    assert repository.get_configuration() is None
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM prompt_overrides").fetchone() == (0,)
