# ruff: noqa: F811

import pytest
from fastapi.testclient import TestClient

from packages.backend.lesson_plans.service import LessonPlanService
from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    csrf_headers,
    passkey_client,
)
from tests.api.plan_helpers import provision_editable_plan_context


def test_open_is_idempotent_and_list_get_save_archive_history_restore_work(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, actor = admin_client
    class_id, plan_id = provision_editable_plan_context(client, actor)
    reopened = client.post(
        "/api/v1/plans/open",
        json={"class_id": class_id, "plan_date": "2026-03-02"},
        headers=csrf_headers(client),
    )
    assert reopened.status_code == 200
    assert reopened.json()["id"] == plan_id

    plan = reopened.json()
    content = plan["content"]
    content["morning_talk"] = {
        "topic": "爱护植物",
        "questions": ["为什么要浇水？", "怎样保护叶片？", "发现枯叶怎么办？"],
    }
    saved = client.put(
        f"/api/v1/plans/{plan_id}/save",
        json={
            "expected_version": plan["version"],
            "content": content,
            "authors": [{"user_id": str(actor.user_id), "sort_order": 0}],
        },
        headers=csrf_headers(client),
    )
    assert saved.status_code == 200
    listed = client.get(
        f"/api/v1/plans?class_id={class_id}&date_from=2026-03-01&date_to=2026-03-31"
    )
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    snapshots = client.get(f"/api/v1/plans/{plan_id}/snapshots")
    assert snapshots.status_code == 200
    assert [item["reason_code"] for item in snapshots.json()["items"]] == ["manual_save"]

    archived = client.post(
        f"/api/v1/plans/{plan_id}/archive",
        json={"expected_version": saved.json()["version"]},
        headers=csrf_headers(client),
    )
    assert archived.status_code == 200
    rejected_save = client.put(
        f"/api/v1/plans/{plan_id}/autosave",
        json={
            "expected_version": archived.json()["version"],
            "content": content,
            "authors": [{"user_id": str(actor.user_id), "sort_order": 0}],
        },
        headers=csrf_headers(client),
    )
    assert rejected_save.status_code == 409

    unarchived = client.post(
        f"/api/v1/plans/{plan_id}/unarchive",
        json={"expected_version": archived.json()["version"]},
        headers=csrf_headers(client),
    )
    assert unarchived.status_code == 200
    restored = client.post(
        f"/api/v1/plans/{plan_id}/snapshots/{snapshots.json()['items'][0]['id']}/restore",
        json={"expected_version": unarchived.json()["version"]},
        headers=csrf_headers(client),
    )
    assert restored.status_code == 200
    reasons = [
        item["reason_code"]
        for item in client.get(f"/api/v1/plans/{plan_id}/snapshots").json()["items"]
    ]
    assert reasons == [
        "restored",
        "before_restore",
        "unarchive",
        "archive",
        "manual_save",
    ]


def test_plan_writes_reject_ownership_fields(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, actor = admin_client
    class_id, plan_id = provision_editable_plan_context(client, actor)
    plan = client.get(f"/api/v1/plans/{plan_id}").json()

    response = client.put(
        f"/api/v1/plans/{plan_id}/save",
        json={
            "expected_version": plan["version"],
            "content": plan["content"],
            "authors": [{"user_id": str(actor.user_id), "sort_order": 0}],
            "kindergarten_id": str(actor.kindergarten_id),
            "class_id": class_id,
            "plan_date": "2026-03-03",
        },
        headers=csrf_headers(client),
    )

    assert response.status_code == 422


def test_plan_list_batches_response_context_without_per_item_connections(
    admin_client: tuple[TestClient, ActorFixture],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client, actor = admin_client
    provision_editable_plan_context(client, actor)
    second = client.post(
        "/api/v1/plans/open",
        json={
            "class_id": client.get("/api/v1/plans").json()["items"][0]["class_id"],
            "plan_date": "2026-03-03",
        },
        headers=csrf_headers(client),
    )
    assert second.status_code == 201

    connection_count = 0
    original_connect = LessonPlanService._connect

    def counting_connect(self: LessonPlanService):
        nonlocal connection_count
        connection_count += 1
        return original_connect(self)

    monkeypatch.setattr(LessonPlanService, "_connect", counting_connect)

    listed = client.get("/api/v1/plans?page=1&page_size=100")

    assert listed.status_code == 200
    assert listed.json()["total"] == 2
    assert connection_count == 2
