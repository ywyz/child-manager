from pathlib import Path
from typing import Any

import yaml

from apps.api.app import create_app

FROZEN: dict[str, Any] = yaml.safe_load(
    Path("specs/001-daily-activity-plan/contracts/openapi.yaml").read_text(encoding="utf-8")
)
M4_PATHS = {
    "/api/v1/settings/ai-model-profiles",
    "/api/v1/settings/ai-model-profiles/{profile_id}",
    "/api/v1/settings/ai-model-profiles/{profile_id}/enable",
    "/api/v1/settings/ai-model-profiles/{profile_id}/disable",
    "/api/v1/prompts",
    "/api/v1/prompts/{code}",
    "/api/v1/prompts/{code}/draft",
    "/api/v1/prompts/{code}/publish",
    "/api/v1/prompts/{code}/versions",
    "/api/v1/prompts/{code}/versions/{version_id}",
    "/api/v1/prompts/{code}/versions/{version_id}/restore",
    "/api/v1/prompts/{code}/tests",
    "/api/v1/prompts/{code}/tests/{run_id}",
    "/api/v1/jobs/{job_id}",
}


def _schema(document: dict[str, Any], name: str) -> dict[str, Any]:
    value = document["components"]["schemas"][name]
    assert isinstance(value, dict)
    return value


def test_runtime_exposes_the_complete_frozen_m4_route_surface() -> None:
    runtime = create_app().openapi()
    assert set(FROZEN["paths"]) >= M4_PATHS
    assert set(runtime["paths"]) >= M4_PATHS
    for path in M4_PATHS:
        assert set(runtime["paths"][path]) == set(FROZEN["paths"][path]), path


def test_model_and_job_contracts_freeze_revision_and_stable_errors() -> None:
    runtime = create_app().openapi()
    profile = _schema(runtime, "AiModelProfile")
    assert "call_config_revision" in profile["required"]
    assert profile["properties"]["call_config_revision"]["minimum"] == 1
    assert "api_key" not in profile["properties"]
    assert profile["properties"]["api_key_masked"]["readOnly"] is True

    run = _schema(runtime, "PromptTestRun")
    assert set(run["properties"]) == {
        "id",
        "job_id",
        "prompt_code",
        "input_summary",
        "status",
        "output_content",
        "elapsed_ms",
        "error_code",
        "error_summary",
        "created_at",
    }
    assert (
        "prompt.configuration_changed"
        in FROZEN["components"]["schemas"]["PromptTestRun"]["properties"]["error_code"][
            "description"
        ]
    )


def test_prompt_test_contract_exposes_only_redacted_input_summary() -> None:
    runtime = create_app().openapi()
    summary = _schema(runtime, "PromptTestInputSummary")
    assert summary["additionalProperties"] is False
    assert set(summary["required"]) == {"provided_variable_names", "all_values_redacted"}
    assert summary["properties"]["all_values_redacted"]["const"] is True
    assert summary["properties"]["provided_variable_names"]["description"].startswith(
        "按 ASCII 字典序排列"
    )


def test_prompt_test_acceptance_contract_distinguishes_precommit_503_from_postcommit_202() -> None:
    operation = FROZEN["paths"]["/api/v1/prompts/{code}/tests"]["post"]
    assert set(operation["responses"]) >= {"202", "409", "503"}
    description = operation["description"]
    assert "事务提交后 Redis 投递失败仍返回 `202 pending_dispatch`" in description
    assert "`database.unavailable`" in description
    assert "`configuration.unavailable`" in description


def test_prompt_test_fingerprint_changes_across_prompt_codes() -> None:
    from packages.contracts.common import canonical_request_fingerprint

    body = {
        "version_id": "01900000-0000-7000-8000-000000000001",
        "model_profile_id": "01900000-0000-7000-8000-000000000002",
        "variables": {"plan_date": "2026-07-26"},
    }
    morning = canonical_request_fingerprint(
        method="POST",
        route_template="/api/v1/prompts/{code}/tests",
        path_params={"code": "daily_activity_plan.morning_activity"},
        query_params=[],
        body=body,
    )
    talk = canonical_request_fingerprint(
        method="POST",
        route_template="/api/v1/prompts/{code}/tests",
        path_params={"code": "daily_activity_plan.morning_talk"},
        query_params=[],
        body=body,
    )
    assert morning != talk
