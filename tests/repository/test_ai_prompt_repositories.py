from __future__ import annotations

import inspect
from collections.abc import Sequence
from importlib import import_module
from typing import Any
from uuid import uuid4

import pytest


class RecordingConnection:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[object, ...]]] = []

    def execute(
        self,
        statement: object,
        params: Sequence[object] = (),
    ) -> None:
        self.calls.append((str(statement), tuple(params)))


def _modules() -> tuple[Any, Any, Any]:
    try:
        settings = import_module("packages.backend.settings.repository")
        prompts = import_module("packages.backend.prompts.repository")
        jobs = import_module("packages.backend.jobs.repository")
    except ModuleNotFoundError:
        pytest.fail("T080 尚未提供 M4 Repository", pytrace=False)
    return settings, prompts, jobs


def test_all_public_repository_methods_require_explicit_kindergarten_id() -> None:
    settings, prompts, jobs = _modules()
    for repository_class in (
        settings.AiModelProfileRepository,
        prompts.PromptRepository,
        jobs.JobRepository,
    ):
        methods = {
            name: member
            for name, member in inspect.getmembers(repository_class, inspect.isfunction)
            if not name.startswith("_")
        }
        assert methods
        for name, method in methods.items():
            assert "kindergarten_id" in inspect.signature(method).parameters, (
                repository_class.__name__,
                name,
            )


def test_model_reads_and_writes_are_tenant_scoped() -> None:
    settings, _prompts, _jobs = _modules()
    connection = RecordingConnection()
    kindergarten_id = uuid4()
    profile_id = uuid4()
    repository = settings.AiModelProfileRepository(connection)

    repository.get(kindergarten_id, profile_id)

    assert connection.calls
    for statement, params in connection.calls:
        assert "kindergarten_id" in statement.lower()
        assert kindergarten_id in params
        assert profile_id in params


def test_call_configuration_change_set_matches_the_frozen_revision_rules() -> None:
    settings, _prompts, _jobs = _modules()
    assert frozenset({"api_base_url", "model_name", "capability_codes", "api_key"}) == (
        settings.CALL_CONFIG_FIELDS
    )
    assert (
        settings.call_configuration_changed(
            {"name": "旧名称", "api_base_url": "https://a.example/v1"},
            {"name": "新名称", "api_base_url": "https://a.example/v1"},
        )
        is False
    )
    assert (
        settings.call_configuration_changed(
            {"api_base_url": "https://a.example/v1"},
            {"api_base_url": "https://b.example/v1"},
        )
        is True
    )


def test_prompt_test_summary_contains_only_sorted_names_and_redaction_flag() -> None:
    _settings, prompts, _jobs = _modules()
    summary = prompts.prompt_test_input_summary(
        {"teacher_context": {"notes": "秘密"}, "class_name": "向日葵班", "plan_date": "2026-07-26"}
    )
    assert summary == {
        "provided_variable_names": ["class_name", "plan_date", "teacher_context"],
        "all_values_redacted": True,
    }
    assert "向日葵班" not in str(summary)
    assert "秘密" not in str(summary)


def test_prompt_run_frozen_fields_cannot_be_updated() -> None:
    _settings, prompts, _jobs = _modules()
    assert frozenset(
        {
            "input_context",
            "input_sha256",
            "prompt_content",
            "prompt_content_sha256",
            "result_schema_code",
            "result_schema_version",
            "model_call_snapshot",
            "input_summary",
            "prompt_definition_id",
            "prompt_version_id",
            "model_profile_id",
            "job_id",
        }
    ) == prompts.FROZEN_PROMPT_RUN_FIELDS
    connection = RecordingConnection()
    repository = prompts.PromptRepository(connection)
    with pytest.raises(ValueError):
        repository.update_prompt_test_run(
            uuid4(),
            uuid4(),
            changes={"prompt_content": "不可修改"},
        )


def test_idempotency_lookup_is_an_explicit_read_seam_before_retention_cleanup() -> None:
    _settings, _prompts, jobs = _modules()
    connection = RecordingConnection()
    repository = jobs.JobRepository(connection)
    kindergarten_id = uuid4()
    requested_by = uuid4()

    repository.find_idempotent(
        kindergarten_id,
        requested_by=requested_by,
        scope="POST /api/v1/prompts/{code}/tests",
        key="same-key",
    )

    statement, params = connection.calls[0]
    assert "kindergarten_id" in statement.lower()
    assert "idempotency_scope" in statement.lower()
    assert kindergarten_id in params
    assert requested_by in params
