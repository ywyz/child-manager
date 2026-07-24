# ruff: noqa: F811

from fastapi.testclient import TestClient

from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    csrf_headers,
    passkey_client,
)


def test_admin_reads_and_updates_only_the_kindergarten_name(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, _actor = admin_client

    current = client.get("/api/v1/settings/kindergarten")
    updated = client.patch(
        "/api/v1/settings/kindergarten",
        json={"name": "更新后的测试园"},
        headers=csrf_headers(client),
    )
    rejected_timezone = client.patch(
        "/api/v1/settings/kindergarten",
        json={"name": "更新后的测试园", "timezone": "UTC"},
        headers=csrf_headers(client),
    )

    assert current.status_code == 200
    assert current.json()["timezone"] == "Asia/Shanghai"
    assert updated.status_code == 200
    assert updated.json()["name"] == "更新后的测试园"
    assert updated.json()["timezone"] == "Asia/Shanghai"
    assert rejected_timezone.status_code == 422


def test_admin_manages_non_overlapping_semesters_and_one_current_semester(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, _actor = admin_client
    headers = csrf_headers(client)

    spring = client.post(
        "/api/v1/settings/semesters",
        json={
            "name": "2026 春季学期",
            "start_date": "2026-02-01",
            "end_date": "2026-06-30",
            "is_active": True,
        },
        headers=headers,
    )
    autumn = client.post(
        "/api/v1/settings/semesters",
        json={
            "name": "2026 秋季学期",
            "start_date": "2026-09-01",
            "end_date": "2027-01-31",
            "is_active": True,
        },
        headers=headers,
    )

    assert spring.status_code == 201
    assert autumn.status_code == 201

    made_current = client.post(
        f"/api/v1/settings/semesters/{spring.json()['id']}/make-current",
        headers=csrf_headers(client),
    )
    overlapping = client.post(
        "/api/v1/settings/semesters",
        json={
            "name": "重叠学期",
            "start_date": "2026-06-30",
            "end_date": "2026-09-15",
            "is_active": True,
        },
        headers=csrf_headers(client),
    )
    listed = client.get("/api/v1/settings/semesters?page=1&page_size=20")

    assert made_current.status_code == 200
    assert made_current.json()["is_current"] is True
    assert overlapping.status_code == 409
    assert listed.status_code == 200
    assert listed.json()["total"] == 2
    assert [item["name"] for item in listed.json()["items"]] == [
        "2026 秋季学期",
        "2026 春季学期",
    ]


def test_admin_creates_an_empty_area_class_and_saves_teacher_relationships(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, actor = admin_client
    age_groups = client.get("/api/v1/settings/age-groups")

    assert age_groups.status_code == 200
    assert [item["code"] for item in age_groups.json()] == [
        "toddler",
        "small",
        "middle",
        "large",
    ]

    created = client.post(
        "/api/v1/settings/classes",
        json={
            "name": "向日葵班",
            "age_group_id": age_groups.json()[2]["id"],
            "is_active": True,
        },
        headers=csrf_headers(client),
    )

    assert created.status_code == 201
    assert created.json()["indoor_areas_configured"] is False
    assert created.json()["outdoor_areas_configured"] is False
    assert created.json()["teachers"] == []

    relationships = client.put(
        f"/api/v1/settings/classes/{created.json()['id']}/teachers",
        json={
            "teachers": [
                {
                    "user_id": str(actor.user_id),
                    "is_lead_teacher": True,
                }
            ]
        },
        headers=csrf_headers(client),
    )

    assert relationships.status_code == 200
    assert relationships.json()["teachers"] == [
        {
            "user_id": str(actor.user_id),
            "display_name": "测试管理员",
            "is_lead_teacher": True,
        }
    ]


def test_associated_admin_replaces_empty_and_paginated_ordered_areas(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, actor = admin_client
    age_groups = client.get("/api/v1/settings/age-groups")
    assert age_groups.status_code == 200
    created = client.post(
        "/api/v1/settings/classes",
        json={
            "name": "区域分页班",
            "age_group_id": age_groups.json()[1]["id"],
            "is_active": True,
        },
        headers=csrf_headers(client),
    )
    assert created.status_code == 201
    class_id = created.json()["id"]
    associated = client.put(
        f"/api/v1/settings/classes/{class_id}/teachers",
        json={
            "teachers": [
                {
                    "user_id": str(actor.user_id),
                    "is_lead_teacher": False,
                }
            ]
        },
        headers=csrf_headers(client),
    )
    assert associated.status_code == 200

    emptied = client.put(
        f"/api/v1/settings/classes/{class_id}/areas/indoor",
        json={"areas": []},
        headers=csrf_headers(client),
    )
    areas = [
        {
            "name": f"区域 {index:02d}",
            "sort_order": index,
            "is_active": True,
        }
        for index in range(25)
    ]
    saved = client.put(
        f"/api/v1/settings/classes/{class_id}/areas/indoor",
        json={"areas": areas},
        headers=csrf_headers(client),
    )
    first_page = client.get(f"/api/v1/settings/classes/{class_id}/areas/indoor")
    all_items = client.get(f"/api/v1/settings/classes/{class_id}/areas/indoor?page=1&page_size=100")

    assert emptied.status_code == 204
    assert emptied.content == b""
    assert saved.status_code == 204
    assert saved.content == b""
    assert first_page.status_code == 200
    assert first_page.json()["page"] == 1
    assert first_page.json()["page_size"] == 20
    assert first_page.json()["total"] == 25
    assert len(first_page.json()["items"]) == 20
    assert all_items.status_code == 200
    assert [item["name"] for item in all_items.json()["items"]] == [item["name"] for item in areas]
