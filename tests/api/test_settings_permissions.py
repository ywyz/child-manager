# ruff: noqa: F811

from collections.abc import Iterator
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import cast
from uuid import UUID, uuid4

import psycopg
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from apps.api.dependencies import admin_session, current_session
from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    csrf_headers,
    passkey_client,
)


@pytest.fixture
def teacher_client(
    passkey_client: TestClient,
    isolated_database_url: str,
) -> Iterator[tuple[TestClient, ActorFixture]]:
    actor = ActorFixture(kindergarten_id=uuid4(), user_id=uuid4(), session_id=uuid4())
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        connection.execute(
            "INSERT INTO kindergartens (id, name) VALUES (%s, %s)",
            (actor.kindergarten_id, "教师权限测试园"),
        )
        connection.execute(
            """INSERT INTO users
            (id, kindergarten_id, username, username_normalized, display_name,
             webauthn_user_handle, status, activated_at)
            VALUES (%s,%s,%s,%s,%s,%s,'active',%s)""",
            (
                actor.user_id,
                actor.kindergarten_id,
                "teacher",
                "teacher",
                "权限测试教师",
                b"t" * 32,
                datetime.now(UTC),
            ),
        )
        teacher_role = connection.execute("SELECT id FROM roles WHERE code='teacher'").fetchone()
        assert teacher_role is not None
        connection.execute(
            """INSERT INTO user_roles
            (kindergarten_id, user_id, role_id, assigned_by, assigned_at)
            VALUES (%s,%s,%s,%s,%s)""",
            (
                actor.kindergarten_id,
                actor.user_id,
                teacher_role[0],
                actor.user_id,
                datetime.now(UTC),
            ),
        )

    session = SimpleNamespace(
        user=SimpleNamespace(
            id=actor.user_id,
            kindergarten_id=actor.kindergarten_id,
            username="teacher",
            display_name="权限测试教师",
            status="active",
            is_active=True,
        ),
        role_codes=["teacher"],
        token_family_id=actor.session_id,
        session_id=actor.session_id,
        last_reauthenticated_at=datetime.now(UTC),
    )
    application = cast(FastAPI, passkey_client.app)
    application.dependency_overrides[current_session] = lambda: session
    try:
        yield passkey_client, actor
    finally:
        application.dependency_overrides.clear()


def test_all_settings_routes_require_authentication(passkey_client: TestClient) -> None:
    class_id = UUID("00000000-0000-7000-8000-000000000001")

    responses = [
        passkey_client.get("/api/v1/settings/kindergarten"),
        passkey_client.get("/api/v1/settings/age-groups"),
        passkey_client.get("/api/v1/settings/semesters"),
        passkey_client.get("/api/v1/settings/classes"),
        passkey_client.get(f"/api/v1/settings/classes/{class_id}/areas/indoor"),
    ]

    assert [response.status_code for response in responses] == [401] * len(responses)


def test_teacher_cannot_use_admin_system_settings(
    teacher_client: tuple[TestClient, ActorFixture],
) -> None:
    client, _actor = teacher_client

    responses = [
        client.get("/api/v1/settings/kindergarten"),
        client.get("/api/v1/settings/age-groups"),
        client.get("/api/v1/settings/semesters"),
        client.get("/api/v1/settings/classes"),
    ]

    assert [response.status_code for response in responses] == [403] * len(responses)


def _provision_associated_teacher(
    client: TestClient,
    admin_actor: ActorFixture,
) -> tuple[str, str]:
    age_groups = client.get("/api/v1/settings/age-groups")
    assert age_groups.status_code == 200
    teacher = client.post(
        "/api/v1/users",
        json={
            "username": "area-teacher",
            "display_name": "区域教师",
            "role_codes": ["teacher"],
        },
        headers=csrf_headers(client),
    )
    assert teacher.status_code == 201
    class_response = client.post(
        "/api/v1/settings/classes",
        json={
            "name": "权限矩阵班",
            "age_group_id": age_groups.json()[1]["id"],
            "is_active": True,
        },
        headers=csrf_headers(client),
    )
    assert class_response.status_code == 201
    relationship = client.put(
        f"/api/v1/settings/classes/{class_response.json()['id']}/teachers",
        json={
            "teachers": [
                {
                    "user_id": teacher.json()["id"],
                    "is_lead_teacher": True,
                }
            ]
        },
        headers=csrf_headers(client),
    )
    assert relationship.status_code == 200
    assert str(admin_actor.user_id) != teacher.json()["id"]
    return class_response.json()["id"], teacher.json()["id"]


def _session_for(actor_id: str, kindergarten_id: UUID) -> SimpleNamespace:
    return SimpleNamespace(
        user=SimpleNamespace(
            id=UUID(actor_id),
            kindergarten_id=kindergarten_id,
            username="area-teacher",
            display_name="区域教师",
            status="pending_registration",
            is_active=True,
        ),
        role_codes=["teacher"],
        token_family_id=uuid4(),
        session_id=uuid4(),
        last_reauthenticated_at=datetime.now(UTC),
    )


def test_only_associated_teacher_can_read_and_replace_class_areas_and_unlink_is_immediate(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, admin_actor = admin_client
    application = cast(FastAPI, client.app)
    admin_current_override = application.dependency_overrides[current_session]
    admin_admin_override = application.dependency_overrides[admin_session]
    class_id, teacher_id = _provision_associated_teacher(client, admin_actor)
    teacher_session = _session_for(teacher_id, admin_actor.kindergarten_id)

    application.dependency_overrides[current_session] = lambda: teacher_session
    application.dependency_overrides.pop(admin_session, None)
    teacher_capabilities = client.get("/api/v1/auth/me")
    teacher_classes = client.get("/api/v1/settings/classes?page=1&page_size=20")
    teacher_class = client.get(f"/api/v1/settings/classes/{class_id}")
    saved = client.put(
        f"/api/v1/settings/classes/{class_id}/areas/outdoor",
        json={
            "areas": [
                {"name": "沙水区", "sort_order": 0, "is_active": True},
                {"name": "种植区", "sort_order": 1, "is_active": True},
            ]
        },
        headers=csrf_headers(client),
    )
    listed = client.get(f"/api/v1/settings/classes/{class_id}/areas/outdoor?page=1&page_size=20")

    assert teacher_capabilities.status_code == 200
    assert "class_areas:manage" in teacher_capabilities.json()["capabilities"]
    assert teacher_classes.status_code == 200
    assert [item["id"] for item in teacher_classes.json()["items"]] == [class_id]
    assert teacher_class.status_code == 200
    assert teacher_class.json()["id"] == class_id
    assert saved.status_code == 204
    assert listed.status_code == 200
    assert [item["name"] for item in listed.json()["items"]] == ["沙水区", "种植区"]

    application.dependency_overrides[current_session] = admin_current_override
    application.dependency_overrides[admin_session] = admin_admin_override
    unlinked = client.put(
        f"/api/v1/settings/classes/{class_id}/teachers",
        json={"teachers": []},
        headers=csrf_headers(client),
    )
    assert unlinked.status_code == 200

    application.dependency_overrides[current_session] = lambda: teacher_session
    application.dependency_overrides.pop(admin_session, None)
    after_unlink = client.get(
        f"/api/v1/settings/classes/{class_id}/areas/outdoor?page=1&page_size=20"
    )
    capabilities_after_unlink = client.get("/api/v1/auth/me")

    assert after_unlink.status_code == 403
    assert "class_areas:manage" not in capabilities_after_unlink.json()["capabilities"]


def test_deactivating_class_immediately_revokes_teacher_area_access(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, admin_actor = admin_client
    application = cast(FastAPI, client.app)
    admin_current_override = application.dependency_overrides[current_session]
    class_id, teacher_id = _provision_associated_teacher(client, admin_actor)
    class_record = client.get(f"/api/v1/settings/classes/{class_id}")
    assert class_record.status_code == 200
    deactivated = client.patch(
        f"/api/v1/settings/classes/{class_id}",
        json={
            "name": class_record.json()["name"],
            "age_group_id": class_record.json()["age_group_id"],
            "is_active": False,
        },
        headers=csrf_headers(client),
    )
    assert deactivated.status_code == 200

    application.dependency_overrides[current_session] = lambda: _session_for(
        teacher_id,
        admin_actor.kindergarten_id,
    )
    application.dependency_overrides.pop(admin_session, None)
    capabilities = client.get("/api/v1/auth/me")
    classes = client.get("/api/v1/settings/classes?page=1&page_size=20")
    class_response = client.get(f"/api/v1/settings/classes/{class_id}")
    areas = client.get(f"/api/v1/settings/classes/{class_id}/areas/indoor")
    saved = client.put(
        f"/api/v1/settings/classes/{class_id}/areas/indoor",
        json={"areas": [{"name": "阅读区", "sort_order": 0, "is_active": True}]},
        headers=csrf_headers(client),
    )

    assert "class_areas:manage" not in capabilities.json()["capabilities"]
    assert classes.status_code == 403
    assert class_response.status_code == 403
    assert areas.status_code == 403
    assert saved.status_code == 403

    application.dependency_overrides[current_session] = admin_current_override


def test_unassociated_admin_cannot_maintain_class_areas(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, _actor = admin_client
    age_groups = client.get("/api/v1/settings/age-groups")
    assert age_groups.status_code == 200
    created = client.post(
        "/api/v1/settings/classes",
        json={
            "name": "管理员未关联班",
            "age_group_id": age_groups.json()[0]["id"],
            "is_active": True,
        },
        headers=csrf_headers(client),
    )
    assert created.status_code == 201

    listed = client.get(f"/api/v1/settings/classes/{created.json()['id']}/areas/indoor")
    replaced = client.put(
        f"/api/v1/settings/classes/{created.json()['id']}/areas/indoor",
        json={"areas": []},
        headers=csrf_headers(client),
    )

    assert listed.status_code == 403
    assert replaced.status_code == 403
    current_user = client.get("/api/v1/auth/me")
    assert "settings:manage" in current_user.json()["capabilities"]
    assert "class_areas:manage" not in current_user.json()["capabilities"]
