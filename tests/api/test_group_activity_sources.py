# ruff: noqa: F811

"""US5 集体活动来源路由 RED。"""

from uuid import UUID, uuid4

import psycopg
from fastapi.testclient import TestClient

from tests.api.passkey_helpers import (
    ActorFixture,
    admin_client,  # noqa: F401
    csrf_headers,
    passkey_client,  # noqa: F401
)
from tests.api.plan_helpers import provision_editable_plan_context
from tests.fixtures.docx_factory import make_valid_docx


def _source_url(plan_id: str, suffix: str = "") -> str:
    return f"/api/v1/plans/{plan_id}/group-activity-sources{suffix}"


def _source_history_total(client: TestClient, plan_id: str) -> int:
    response = client.get(_source_url(plan_id))
    assert response.status_code == 200
    return int(response.json()["total"])


def _insert_other_kindergarten_plan(
    database_url: str,
    *,
    source_kindergarten_id: UUID,
    source_plan_id: str,
) -> str:
    other_kindergarten_id = uuid4()
    other_user_id = uuid4()
    other_age_group_id = uuid4()
    other_class_id = uuid4()
    other_semester_id = uuid4()
    other_plan_id = uuid4()
    native_url = database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        connection.execute(
            "INSERT INTO kindergartens (id,name,timezone,is_active) VALUES (%s,%s,%s,true)",
            (other_kindergarten_id, "不可见测试园", "Asia/Shanghai"),
        )
        connection.execute(
            """INSERT INTO users
            (id,kindergarten_id,username,username_normalized,display_name,
             webauthn_user_handle,status,backup_auth_version)
            VALUES (%s,%s,%s,%s,%s,%s,'active',1)""",
            (
                other_user_id,
                other_kindergarten_id,
                "other-source-owner",
                "other-source-owner",
                "其他园教师",
                uuid4().bytes + uuid4().bytes,
            ),
        )
        connection.execute(
            """INSERT INTO age_groups (id,kindergarten_id,code,name,sort_order,is_active)
            VALUES (%s,%s,'large','大班',0,true)""",
            (other_age_group_id, other_kindergarten_id),
        )
        connection.execute(
            """INSERT INTO classes
            (id,kindergarten_id,name,name_normalized,age_group_id,is_active,created_by,updated_by)
            VALUES (%s,%s,'其他园班','其他园班',%s,true,%s,%s)""",
            (
                other_class_id,
                other_kindergarten_id,
                other_age_group_id,
                other_user_id,
                other_user_id,
            ),
        )
        connection.execute(
            """INSERT INTO semesters
            (id,kindergarten_id,name,start_date,end_date,is_current,is_active,created_by,updated_by)
            VALUES (%s,%s,'其他园学期','2026-02-04','2026-06-30',true,true,%s,%s)""",
            (other_semester_id, other_kindergarten_id, other_user_id, other_user_id),
        )
        connection.execute(
            """INSERT INTO daily_activity_plans
            (id,kindergarten_id,class_id,semester_id,plan_date,kindergarten_name_snapshot,
             class_name_snapshot,age_group_name_snapshot,semester_name_snapshot,
             semester_start_date_snapshot,semester_end_date_snapshot,teaching_week_number,
             teaching_week_text,activity_date_text,season_code,content,content_schema_version,
             version,archived_at,archived_by,created_by,updated_by)
            SELECT %s,%s,%s,%s,plan_date,'不可见测试园','其他园班','大班','其他园学期',
                   semester_start_date_snapshot,semester_end_date_snapshot,teaching_week_number,
                   teaching_week_text,activity_date_text,season_code,content,content_schema_version,
                   version,archived_at,archived_by,%s,%s
            FROM daily_activity_plans WHERE kindergarten_id=%s AND id=%s""",
            (
                other_plan_id,
                other_kindergarten_id,
                other_class_id,
                other_semester_id,
                other_user_id,
                other_user_id,
                source_kindergarten_id,
                UUID(source_plan_id),
            ),
        )
    return str(other_plan_id)


def test_confirmed_text_creates_metadata_only_and_each_confirmation_is_retained(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, actor = admin_client
    _class_id, plan_id = provision_editable_plan_context(client, actor)

    first = client.post(
        _source_url(plan_id, "/text"),
        json={"text": "教师确认的集体活动原文。"},
        headers=csrf_headers(client),
    )
    second = client.post(
        _source_url(plan_id, "/text"),
        json={"text": "教师再次确认的集体活动原文。"},
        headers=csrf_headers(client),
    )
    history = client.get(_source_url(plan_id))

    assert first.status_code == second.status_code == 201
    assert first.json()["id"] != second.json()["id"]
    assert first.json()["source_type"] == "pasted_text"
    assert "text" not in first.json()
    assert "attachment" not in first.json()
    assert history.status_code == 200
    assert history.json()["total"] == 2


def test_docx_confirmation_sanitizes_filename_and_persists_only_extracted_metadata(
    admin_client: tuple[TestClient, ActorFixture],
) -> None:
    client, actor = admin_client
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    upload = make_valid_docx()

    response = client.post(
        _source_url(plan_id, "/docx"),
        files={"file": ("../班级\\原始?教案.docx", upload.payload, upload.content_type)},
        headers=csrf_headers(client),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["source_type"] == "docx"
    assert body["original_filename"].endswith(".docx")
    assert "/" not in body["original_filename"]
    assert "\\" not in body["original_filename"]
    assert "text" not in body
    assert "attachment" not in body


def test_text_limit_and_live_class_authorization_are_rejected_before_source_write(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = admin_client
    class_id, plan_id = provision_editable_plan_context(client, actor)
    assert _source_history_total(client, plan_id) == 0

    over_limit = client.post(
        _source_url(plan_id, "/text"),
        json={"text": "字" * 200_001},
        headers=csrf_headers(client),
    )
    assert over_limit.status_code == 422
    assert _source_history_total(client, plan_id) == 0

    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        connection.execute(
            """DELETE FROM class_teachers
            WHERE kindergarten_id=%s AND class_id=%s AND user_id=%s""",
            (actor.kindergarten_id, class_id, actor.user_id),
        )
        connection.commit()
    unauthorized = client.post(
        _source_url(plan_id, "/text"),
        json={"text": "实时授权必须在写入前复核。"},
        headers=csrf_headers(client),
    )

    assert unauthorized.status_code == 403
    assert _source_history_total(client, plan_id) == 0


def test_cross_kindergarten_plan_identifier_is_not_accepted_as_a_source_target(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = admin_client
    _class_id, source_plan_id = provision_editable_plan_context(client, actor)
    other_plan_id = _insert_other_kindergarten_plan(
        isolated_database_url,
        source_kindergarten_id=actor.kindergarten_id,
        source_plan_id=source_plan_id,
    )

    own_source = client.post(
        _source_url(source_plan_id, "/text"),
        json={"text": "当前园来源必须先确认。"},
        headers=csrf_headers(client),
    )
    assert own_source.status_code == 201
    response = client.post(
        _source_url(other_plan_id, "/text"),
        json={"text": "不可跨园写入。"},
        headers=csrf_headers(client),
    )

    assert response.status_code == 404
