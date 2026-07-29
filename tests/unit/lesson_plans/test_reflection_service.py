# ruff: noqa: F811

"""T106 显式反思预保存与任务受理的直连事务门禁。"""

from copy import deepcopy
from uuid import UUID, uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient

from packages.backend.identity.repository import IdentityRepository
from packages.backend.identity.service import IdentityError, SessionUser
from packages.backend.lesson_plans.reflection import ReflectionGenerationService
from packages.contracts.lesson_plans import AiGenerationRequest, PlanContentV1
from tests.api.ai_helpers import provision_enabled_ai_model
from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    passkey_client,
)
from tests.api.plan_helpers import provision_editable_plan_context
from tests.api.test_ai_model_profiles import ai_admin_client  # noqa: F401


def _native_url(value: str) -> str:
    return value.replace("postgresql+psycopg://", "postgresql://", 1)


def _session(database_url: str, actor: ActorFixture) -> SessionUser:
    with psycopg.connect(_native_url(database_url)) as connection:
        user = IdentityRepository(connection, actor.kindergarten_id).get_user(actor.user_id)
    assert user is not None
    return SessionUser(
        user=user,
        role_codes=["admin", "teacher"],
        token_family_id=actor.session_id,
        session_id=actor.session_id,
        last_reauthenticated_at=None,
    )


def _complete_content(content: dict[str, object]) -> PlanContentV1:
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
    return PlanContentV1.model_validate(result)


def _service(database_url: str) -> ReflectionGenerationService:
    return ReflectionGenerationService(database_url=database_url)


def test_reflection_acceptance_saves_once_without_snapshot_and_replays(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    _class_id, plan_id_text = provision_editable_plan_context(client, actor)
    before = client.get(f"/api/v1/plans/{plan_id_text}").json()
    body = AiGenerationRequest(
        task_code="daily_reflection",
        expected_version=before["version"],
        content=_complete_content(before["content"]),
    )
    key = str(uuid4())
    service = _service(isolated_database_url)

    accepted = service.create(
        _session(isolated_database_url, actor),
        UUID(plan_id_text),
        body,
        idempotency_key=key,
        request_id=None,
    )
    replay = service.create(
        _session(isolated_database_url, actor),
        UUID(plan_id_text),
        body,
        idempotency_key=key,
        request_id=None,
    )

    assert accepted.job.id == replay.job.id
    assert replay.replayed
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        plan_row = connection.execute(
            """SELECT version FROM daily_activity_plans
            WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, plan_id_text),
        ).fetchone()
        result_row = connection.execute(
            """SELECT input_context,output_content,target_section
            FROM ai_generation_results
            WHERE kindergarten_id=%s AND job_id=%s""",
            (actor.kindergarten_id, accepted.job.id),
        ).fetchone()
        snapshots = connection.execute(
            """SELECT count(*) FROM daily_activity_plan_snapshots
            WHERE kindergarten_id=%s AND plan_id=%s""",
            (actor.kindergarten_id, plan_id_text),
        ).fetchone()
    assert plan_row == (before["version"] + 1,)
    assert result_row is not None
    assert "daily_reflection" not in result_row[0]["current_plan"]
    assert result_row[1:] == (None, "daily_reflection")
    assert snapshots == (0,)


def test_incomplete_reflection_acceptance_rolls_back_and_key_remains_available(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    _class_id, plan_id_text = provision_editable_plan_context(client, actor)
    before = client.get(f"/api/v1/plans/{plan_id_text}").json()
    incomplete = _complete_content(before["content"])
    incomplete.morning_talk.topic = ""
    incomplete.morning_talk.questions = []
    key = str(uuid4())
    service = _service(isolated_database_url)
    session = _session(isolated_database_url, actor)

    with pytest.raises(IdentityError) as caught:
        service.create(
            session,
            UUID(plan_id_text),
            AiGenerationRequest(
                task_code="daily_reflection",
                expected_version=before["version"],
                content=incomplete,
            ),
            idempotency_key=key,
            request_id=None,
        )
    assert caught.value.code == "ai.reflection_incomplete"

    accepted = service.create(
        session,
        UUID(plan_id_text),
        AiGenerationRequest(
            task_code="daily_reflection",
            expected_version=before["version"],
            content=_complete_content(before["content"]),
        ),
        idempotency_key=key,
        request_id=None,
    )
    assert accepted.job.job_type == "ai.daily_reflection"
