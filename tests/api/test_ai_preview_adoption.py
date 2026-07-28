# ruff: noqa: F811

"""M6 预览双哈希、不可变上下文与采用事务 RED 验收。"""

from copy import deepcopy
from importlib import import_module
from uuid import UUID, uuid4

import psycopg
from fastapi.testclient import TestClient

from tests.api.ai_helpers import create_completed_ai_preview, provision_enabled_ai_model
from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    csrf_headers,
    passkey_client,
)
from tests.api.plan_helpers import provision_editable_plan_context
from tests.api.test_ai_model_profiles import ai_admin_client  # noqa: F401

MORNING_TALK_PREVIEW: dict[str, object] = {
    "topic": "春日观察",
    "questions": ["你看到了什么？", "你听到了什么？", "你想到了什么？"],
}


def _native_url(database_url: str) -> str:
    return database_url.replace("postgresql+psycopg://", "postgresql://", 1)


def _snapshot_count(
    database_url: str,
    *,
    kindergarten_id: UUID,
    plan_id: str,
) -> int:
    with psycopg.connect(_native_url(database_url)) as connection:
        row = connection.execute(
            """SELECT count(*) FROM daily_activity_plan_snapshots
            WHERE kindergarten_id=%s AND plan_id=%s AND reason_code='ai_adopted'""",
            (kindergarten_id, plan_id),
        ).fetchone()
    assert row is not None
    return int(row[0])


def test_adoption_body_rejects_teacher_context_even_before_job_lookup(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, _actor = admin_client

    response = client.post(
        f"/api/v1/jobs/{uuid4()}/adopt",
        json={"expected_version": 1, "teacher_context": "不得在采用时修改"},
        headers=csrf_headers(client),
    )

    assert response.status_code == 422


def test_section_hash_changes_only_with_target_section() -> None:
    fingerprints = import_module("packages.backend.lesson_plans.ai_fingerprints")
    section_sha256 = getattr(fingerprints, "section_sha256", None)
    assert callable(section_sha256), "M6 fingerprint missing: section_sha256"

    original = {"topic": "春天", "questions": ["变化？", "颜色？", "声音？"]}
    assert section_sha256(original) == section_sha256(dict(reversed(list(original.items()))))
    assert section_sha256(original) != section_sha256(original | {"topic": "夏天"})


def test_generation_input_hash_reuses_frozen_teacher_context_and_current_server_input() -> None:
    fingerprints = import_module("packages.backend.lesson_plans.ai_fingerprints")
    input_sha256 = getattr(fingerprints, "generation_input_sha256", None)
    assert callable(input_sha256), "M6 fingerprint missing: generation_input_sha256"
    server_input = {"class_name": "向日葵班", "areas": ["建构区"]}

    frozen = input_sha256(
        task_code="indoor_area_game",
        teacher_context="冻结补充",
        server_input=server_input,
    )
    assert frozen == input_sha256(
        task_code="indoor_area_game",
        teacher_context="冻结补充",
        server_input={"areas": ["建构区"], "class_name": "向日葵班"},
    )
    assert frozen != input_sha256(
        task_code="indoor_area_game",
        teacher_context="页面后来修改",
        server_input=server_input,
    )
    assert frozen != input_sha256(
        task_code="indoor_area_game",
        teacher_context="冻结补充",
        server_input=server_input | {"areas": ["建构区", "美工区"]},
    )


def test_preview_validity_ignores_unrelated_sections_but_rejects_related_changes() -> None:
    adoption = import_module("packages.backend.lesson_plans.ai_adoption")
    validator = getattr(adoption, "preview_is_current", None)
    assert callable(validator), "M6 adoption missing: preview_is_current"

    assert validator(
        frozen_section={"topic": "春天"},
        current_section={"topic": "春天"},
        frozen_server_input={"class_name": "向日葵班"},
        current_server_input={"class_name": "向日葵班"},
        teacher_context="冻结补充",
    )
    assert not validator(
        frozen_section={"topic": "春天"},
        current_section={"topic": "夏天"},
        frozen_server_input={"class_name": "向日葵班"},
        current_server_input={"class_name": "向日葵班"},
        teacher_context="冻结补充",
    )
    assert not validator(
        frozen_section={"topic": "春天"},
        current_section={"topic": "春天"},
        frozen_server_input={"class_name": "向日葵班"},
        current_server_input={"class_name": "毕业班"},
        teacher_context="冻结补充",
    )


def test_adopt_merges_preview_once_and_repeated_request_creates_no_second_snapshot(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    job_id, expected_version = create_completed_ai_preview(
        client,
        database_url=isolated_database_url,
        kindergarten_id=actor.kindergarten_id,
        plan_id=plan_id,
        task_code="morning_talk",
        teacher_context="围绕春日观察",
        output_content=MORNING_TALK_PREVIEW,
    )

    adopted = client.post(
        f"/api/v1/jobs/{job_id}/adopt",
        json={"expected_version": expected_version},
        headers=csrf_headers(client),
    )
    repeated = client.post(
        f"/api/v1/jobs/{job_id}/adopt",
        json={"expected_version": expected_version},
        headers=csrf_headers(client),
    )

    assert adopted.status_code == repeated.status_code == 200
    assert adopted.json()["content"]["morning_talk"] == MORNING_TALK_PREVIEW
    assert repeated.json()["version"] == adopted.json()["version"]
    assert (
        _snapshot_count(
            isolated_database_url,
            kindergarten_id=actor.kindergarten_id,
            plan_id=plan_id,
        )
        == 1
    )
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        row = connection.execute(
            """SELECT j.execution_status,r.adopted_by,r.adopted_at,r.rejected_at
            FROM background_jobs j
            JOIN ai_generation_results r
              ON r.kindergarten_id=j.kindergarten_id AND r.job_id=j.id
            WHERE j.kindergarten_id=%s AND j.id=%s""",
            (actor.kindergarten_id, job_id),
        ).fetchone()
    assert row is not None
    assert row[0] == "adopted"
    assert row[1] == actor.user_id
    assert row[2] is not None
    assert row[3] is None


def test_unrelated_edit_remains_adoptable_but_target_edit_makes_preview_stale(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    first_job_id, first_version = create_completed_ai_preview(
        client,
        database_url=isolated_database_url,
        kindergarten_id=actor.kindergarten_id,
        plan_id=plan_id,
        task_code="morning_talk",
        teacher_context="旧预览上下文",
        output_content=MORNING_TALK_PREVIEW,
    )
    before_unrelated = client.get(f"/api/v1/plans/{plan_id}").json()
    unrelated_content = deepcopy(before_unrelated["content"])
    unrelated_content["daily_reflection"] = {
        "highlights": "幼儿主动发现了春天。",
        "issues": "观察材料还可以更丰富。",
        "adjustments": "继续记录植物变化。",
    }
    saved_unrelated = client.put(
        f"/api/v1/plans/{plan_id}/autosave",
        json={
            "expected_version": before_unrelated["version"],
            "content": unrelated_content,
            "authors": [
                {"user_id": author["user_id"], "sort_order": author["sort_order"]}
                for author in before_unrelated["authors"]
            ],
        },
        headers=csrf_headers(client),
    )
    assert saved_unrelated.status_code == 200

    version_conflict = client.post(
        f"/api/v1/jobs/{first_job_id}/adopt",
        json={"expected_version": first_version},
        headers=csrf_headers(client),
    )
    adopted = client.post(
        f"/api/v1/jobs/{first_job_id}/adopt",
        json={"expected_version": saved_unrelated.json()["version"]},
        headers=csrf_headers(client),
    )
    assert version_conflict.status_code == 409
    assert version_conflict.json()["code"] == "lesson_plan.version_conflict"
    assert adopted.status_code == 200
    assert adopted.json()["content"]["daily_reflection"] == unrelated_content["daily_reflection"]

    second_job_id, _second_version = create_completed_ai_preview(
        client,
        database_url=isolated_database_url,
        kindergarten_id=actor.kindergarten_id,
        plan_id=plan_id,
        task_code="morning_talk",
        teacher_context="第二次生成上下文",
        output_content=MORNING_TALK_PREVIEW | {"topic": "第二个预览"},
    )
    before_target_edit = client.get(f"/api/v1/plans/{plan_id}").json()
    target_changed = deepcopy(before_target_edit["content"])
    target_changed["morning_talk"] = {
        "topic": "教师已经修改",
        "questions": ["保留哪个内容？", "为什么修改？", "下一步是什么？"],
    }
    saved_target = client.put(
        f"/api/v1/plans/{plan_id}/autosave",
        json={
            "expected_version": before_target_edit["version"],
            "content": target_changed,
            "authors": [
                {"user_id": author["user_id"], "sort_order": author["sort_order"]}
                for author in before_target_edit["authors"]
            ],
        },
        headers=csrf_headers(client),
    )
    assert saved_target.status_code == 200

    stale = client.post(
        f"/api/v1/jobs/{second_job_id}/adopt",
        json={"expected_version": saved_target.json()["version"]},
        headers=csrf_headers(client),
    )

    assert stale.status_code == 409
    assert stale.json()["code"] == "ai.preview_stale"
    current = client.get(f"/api/v1/plans/{plan_id}").json()
    assert current["content"]["morning_talk"] == target_changed["morning_talk"]


def test_adopt_rechecks_current_role_and_class_relationship_before_writing(
    ai_admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = ai_admin_client
    provision_enabled_ai_model(client)
    class_id, plan_id = provision_editable_plan_context(client, actor)
    job_id, expected_version = create_completed_ai_preview(
        client,
        database_url=isolated_database_url,
        kindergarten_id=actor.kindergarten_id,
        plan_id=plan_id,
        task_code="morning_talk",
        teacher_context="撤权前创建",
        output_content=MORNING_TALK_PREVIEW,
    )
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        connection.execute(
            """DELETE FROM user_roles AS ur USING roles AS r
            WHERE ur.role_id=r.id AND ur.kindergarten_id=%s AND ur.user_id=%s
              AND r.code='admin'""",
            (actor.kindergarten_id, actor.user_id),
        )
        connection.execute(
            """DELETE FROM class_teachers
            WHERE kindergarten_id=%s AND class_id=%s AND user_id=%s""",
            (actor.kindergarten_id, class_id, actor.user_id),
        )

    response = client.post(
        f"/api/v1/jobs/{job_id}/adopt",
        json={"expected_version": expected_version},
        headers=csrf_headers(client),
    )

    assert response.status_code == 403
    assert (
        _snapshot_count(
            isolated_database_url,
            kindergarten_id=actor.kindergarten_id,
            plan_id=plan_id,
        )
        == 0
    )
    current = client.get(f"/api/v1/plans/{plan_id}")
    assert current.status_code == 403
    with psycopg.connect(_native_url(isolated_database_url)) as connection:
        status = connection.execute(
            """SELECT execution_status FROM background_jobs
            WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, job_id),
        ).fetchone()
    assert status == ("awaiting_confirmation",)
