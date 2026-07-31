# ruff: noqa: F811

"""T121 集体活动来源 Repository RED。"""

from hashlib import sha256
from importlib import import_module
from typing import Any
from uuid import uuid4

import psycopg
import pytest
from fastapi.testclient import TestClient

from tests.api.passkey_helpers import (  # noqa: F401
    ActorFixture,
    admin_client,
    passkey_client,
)
from tests.api.plan_helpers import provision_editable_plan_context

SOURCE_TEXT = "教师确认的集体活动原文。"


def _repository_type() -> type[Any]:
    try:
        module = import_module("packages.backend.lesson_plans.sources")
    except ModuleNotFoundError:
        pytest.fail("T121 集体活动来源 Repository 尚未实现")
    candidate = getattr(module, "LessonPlanSourceRepository", None)
    if candidate is None:
        pytest.fail("T121 集体活动来源 Repository 尚未实现：LessonPlanSourceRepository")
    return candidate


def test_repository_appends_confirmations_hashes_text_and_pages_history(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = admin_client
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        repository = _repository_type()(connection)
        first = repository.confirm_text(
            kindergarten_id=actor.kindergarten_id,
            plan_id=plan_id,
            uploaded_by=actor.user_id,
            text=SOURCE_TEXT,
        )
        second = repository.confirm_text(
            kindergarten_id=actor.kindergarten_id,
            plan_id=plan_id,
            uploaded_by=actor.user_id,
            text=SOURCE_TEXT,
        )
        first_page, first_total = repository.list_history(
            actor.kindergarten_id,
            plan_id,
            page=1,
            page_size=1,
        )
        second_page, second_total = repository.list_history(
            actor.kindergarten_id,
            plan_id,
            page=2,
            page_size=1,
        )
        stored = connection.execute(
            """SELECT extracted_text FROM lesson_plan_sources
            WHERE kindergarten_id=%s AND id=%s""",
            (actor.kindergarten_id, first.id),
        ).fetchone()
        confirmed_text = repository.get_confirmed_text(
            kindergarten_id=actor.kindergarten_id,
            source_id=first.id,
        )
        with pytest.raises(LookupError):
            repository.get_confirmed_text(kindergarten_id=uuid4(), source_id=first.id)

    assert first.id != second.id
    assert first.source_sha256 == sha256(SOURCE_TEXT.encode()).hexdigest()
    assert first.extracted_character_count == len(SOURCE_TEXT)
    assert first_total == second_total == 2
    assert {record.id for record in first_page}.isdisjoint({record.id for record in second_page})
    assert {record.id for record in first_page + second_page} == {first.id, second.id}
    assert stored is not None
    assert stored[0] == SOURCE_TEXT
    assert confirmed_text == SOURCE_TEXT
    assert not hasattr(first, "binary_content")
    assert not hasattr(first, "absolute_path")


def test_repository_cannot_write_current_plan_through_another_kindergarten_scope(
    admin_client: tuple[TestClient, ActorFixture],
    isolated_database_url: str,
) -> None:
    client, actor = admin_client
    _class_id, plan_id = provision_editable_plan_context(client, actor)
    native_url = isolated_database_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(native_url) as connection:
        repository = _repository_type()(connection)
        with pytest.raises(LookupError):
            repository.confirm_text(
                kindergarten_id=uuid4(),
                plan_id=plan_id,
                uploaded_by=actor.user_id,
                text=SOURCE_TEXT,
            )
