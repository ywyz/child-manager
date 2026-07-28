import json
from hashlib import sha256
from importlib import import_module
from uuid import UUID, uuid4

import psycopg
from fastapi.testclient import TestClient

from tests.api.passkey_helpers import csrf_headers


def provision_enabled_ai_model(client: TestClient) -> str:
    created = client.post(
        "/api/v1/settings/ai-model-profiles",
        json={
            "name": "M6 API 测试模型",
            "api_base_url": "https://ai.example.test/v1",
            "model_name": "structured-test-model",
            "api_key": "test-secret-value",
            "capability_codes": ["text", "structured_output"],
            "max_concurrency": 2,
            "rate_limit_per_minute": None,
            "is_default": True,
        },
        headers=csrf_headers(client),
    )
    assert created.status_code == 201
    profile_id = str(created.json()["id"])
    enabled = client.post(
        f"/api/v1/settings/ai-model-profiles/{profile_id}/enable",
        json={"confirm_external_data_risk": True},
        headers=csrf_headers(client),
    )
    assert enabled.status_code == 200
    return profile_id


def create_completed_ai_preview(
    client: TestClient,
    *,
    database_url: str,
    kindergarten_id: UUID,
    plan_id: str,
    task_code: str,
    teacher_context: str,
    output_content: dict[str, object],
) -> tuple[str, int]:
    plan = client.get(f"/api/v1/plans/{plan_id}")
    assert plan.status_code == 200
    expected_version = int(plan.json()["version"])
    accepted = client.post(
        f"/api/v1/plans/{plan_id}/ai/generations",
        json={
            "task_code": task_code,
            "expected_version": expected_version,
            "teacher_context": teacher_context,
        },
        headers=csrf_headers(client) | {"Idempotency-Key": str(uuid4())},
    )
    assert accepted.status_code == 202
    job_id = UUID(accepted.json()["job"]["id"])
    output_sha256 = sha256(
        json.dumps(
            output_content,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()
    repository_type = import_module("packages.backend.jobs.ai_results").AiGenerationResultRepository
    native_url = database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        repository = repository_type(connection)
        assert repository.complete_pending(
            kindergarten_id,
            job_id,
            output_content=output_content,
            output_sha256=output_sha256,
        )
        connection.execute(
            """UPDATE background_jobs SET execution_status='awaiting_confirmation'
            WHERE kindergarten_id=%s AND id=%s""",
            (kindergarten_id, job_id),
        )
    return str(job_id), expected_version
