# ruff: noqa: F811

"""M6 显式反思预保存、完整性与冻结输入 RED 验收。"""

from copy import deepcopy
from uuid import uuid4

import psycopg
from fastapi.testclient import TestClient

from tests.api.ai_helpers import provision_enabled_ai_model
from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    csrf_headers,
    passkey_client,
)
from tests.api.plan_helpers import provision_editable_plan_context
from tests.api.test_ai_model_profiles import ai_admin_client  # noqa: F401


def _complete_content(content: dict[str, object]) -> dict[str, object]:
    result = deepcopy(content)
    statements = ["目标一。", "目标二。", "目标三。"]
    result["morning_activity"] = {
        "physical_cycle": "体能大循环",
        "group_game": "合作接力",
        "free_game": "自主器械",
        "focus_guidance": "关注合作",
        "objectives": statements,
        "guidance_points": ["指导一。", "指导二。", "指导三。"],
    }
    result["morning_talk"] = {
        "topic": "春天",
        "questions": ["看到什么？", "听到什么？", "想到什么？"],
    }
    result["group_activity"] = {
        "theme": "寻找春天",
        "objectives": ["观察季节变化"],
        "preparation": ["春景图片"],
        "focus": "完整表达",
        "difficulty": "连续描述",
        "process": [{"heading": "观察", "lines": ["观察春景"], "is_ai_added": False}],
    }
    for section, area in (
        ("indoor_area_game", "建构区"),
        ("afternoon_outdoor_game", "沙水区"),
    ):
        result[section] = {
            "areas": [area],
            "focus_guidance": area,
            "objectives": statements,
            "guidance_points": ["指导一。", "指导二。", "指导三。"],
            "support_strategies": ["支持一。", "支持二。", "支持三。"],
        }
    result["daily_reflection"] = {
        "highlights": "旧反思不得进入输入",
        "issues": "",
        "adjustments": "",
    }
    return result


def _headers(client: TestClient) -> dict[str, str]:
    return csrf_headers(client) | {"Idempotency-Key": str(uuid4())}


def test_purely_manual_complete_five_sections_can_create_one_reflection_job(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    before = client.get(f"/api/v1/plans/{plan_id}").json()
    content = _complete_content(before["content"])
    headers = _headers(client)
    body = {
        "task_code": "daily_reflection",
        "expected_version": before["version"],
        "content": content,
    }

    response = client.post(
        f"/api/v1/plans/{plan_id}/ai/generations",
        json=body,
        headers=headers,
    )
    replay = client.post(
        f"/api/v1/plans/{plan_id}/ai/generations",
        json=body,
        headers=headers,
    )

    assert response.status_code == replay.status_code == 202
    assert response.json()["job"]["id"] == replay.json()["job"]["id"]
    after = client.get(f"/api/v1/plans/{plan_id}").json()
    assert after["version"] == before["version"] + 1
    assert client.get(f"/api/v1/plans/{plan_id}/snapshots").json()["total"] == 0
    assert "group_activity.ai_step_missing" in {
        warning["code"] for warning in after["soft_warnings"]
    }
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        rows = connection.execute(
            """SELECT r.input_context,r.input_sha256,r.output_content,j.job_type
            FROM ai_generation_results r
            JOIN background_jobs j
              ON (j.kindergarten_id,j.id)=(r.kindergarten_id,r.job_id)
            WHERE r.kindergarten_id=%s AND r.plan_id=%s""",
            (actor.kindergarten_id, plan_id),
        ).fetchall()
    assert len(rows) == 1
    row = rows[0]
    assert "daily_reflection" not in row[0]["current_plan"]
    assert row[1] is not None
    assert row[2] is None
    assert row[3] == "ai.daily_reflection"


def test_incomplete_upstream_section_rolls_back_save_job_and_result(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    before = client.get(f"/api/v1/plans/{plan_id}").json()
    content = _complete_content(before["content"])
    content["morning_talk"] = {"topic": "", "questions": []}

    response = client.post(
        f"/api/v1/plans/{plan_id}/ai/generations",
        json={
            "task_code": "daily_reflection",
            "expected_version": before["version"],
            "content": content,
        },
        headers=_headers(client),
    )

    assert response.status_code == 409
    assert client.get(f"/api/v1/plans/{plan_id}").json()["version"] == before["version"]
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        assert connection.execute(
            """SELECT count(*) FROM background_jobs
            WHERE kindergarten_id=%s AND plan_id=%s
              AND job_type='ai.daily_reflection'""",
            (actor.kindergarten_id, plan_id),
        ).fetchone() == (0,)
        assert connection.execute(
            """SELECT count(*) FROM ai_generation_results
            WHERE kindergarten_id=%s AND plan_id=%s""",
            (actor.kindergarten_id, plan_id),
        ).fetchone() == (0,)


def test_failed_reflection_acceptance_does_not_consume_idempotency_key(
    ai_admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    before = client.get(f"/api/v1/plans/{plan_id}").json()
    incomplete = _complete_content(before["content"])
    incomplete["morning_talk"] = {"topic": "", "questions": []}
    headers = _headers(client)

    failed = client.post(
        f"/api/v1/plans/{plan_id}/ai/generations",
        json={
            "task_code": "daily_reflection",
            "expected_version": before["version"],
            "content": incomplete,
        },
        headers=headers,
    )
    accepted = client.post(
        f"/api/v1/plans/{plan_id}/ai/generations",
        json={
            "task_code": "daily_reflection",
            "expected_version": before["version"],
            "content": _complete_content(before["content"]),
        },
        headers=headers,
    )

    assert failed.status_code == 409
    assert accepted.status_code == 202


def test_reflection_request_rejects_teacher_context(
    ai_admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    before = client.get(f"/api/v1/plans/{plan_id}").json()

    response = client.post(
        f"/api/v1/plans/{plan_id}/ai/generations",
        json={
            "task_code": "daily_reflection",
            "expected_version": before["version"],
            "content": _complete_content(before["content"]),
            "teacher_context": "反思不得接收该字段",
        },
        headers=_headers(client),
    )

    assert response.status_code == 422


def test_reflection_request_normalizes_nfkc_at_200_codepoints_and_rejects_201(
    ai_admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    before = client.get(f"/api/v1/plans/{plan_id}").json()
    headers = _headers(client)
    too_long = _complete_content(before["content"])
    too_long["daily_reflection"] = {
        "highlights": "Ａ" * 199,
        "issues": "问",
        "adjustments": "调",
    }

    rejected = client.post(
        f"/api/v1/plans/{plan_id}/ai/generations",
        json={
            "task_code": "daily_reflection",
            "expected_version": before["version"],
            "content": too_long,
        },
        headers=headers,
    )
    boundary = _complete_content(before["content"])
    boundary["daily_reflection"] = {
        "highlights": "Ａ" * 198,
        "issues": "问",
        "adjustments": "调",
    }
    accepted = client.post(
        f"/api/v1/plans/{plan_id}/ai/generations",
        json={
            "task_code": "daily_reflection",
            "expected_version": before["version"],
            "content": boundary,
        },
        headers=headers,
    )

    assert rejected.status_code == 422
    assert accepted.status_code == 202
    saved = client.get(f"/api/v1/plans/{plan_id}").json()
    assert saved["content"]["daily_reflection"]["highlights"] == "A" * 198
