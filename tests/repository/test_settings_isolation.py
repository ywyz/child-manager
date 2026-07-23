from __future__ import annotations

import inspect
from collections.abc import Sequence
from uuid import UUID, uuid4

import pytest

from packages.backend.settings.repository import SettingsRepository


class RecordingConnection:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[object, ...]]] = []

    def execute(
        self,
        statement: object,
        params: Sequence[object] = (),
    ) -> None:
        self.calls.append((str(statement), tuple(params)))


def _assert_queries_are_tenant_scoped(
    connection: RecordingConnection,
    kindergarten_id: UUID,
    *resource_ids: UUID,
) -> None:
    assert connection.calls, "Repository 必须执行带园所条件的查询"
    for statement, params in connection.calls:
        assert "kindergarten_id" in statement.lower()
        assert kindergarten_id in params
        for resource_id in resource_ids:
            assert resource_id in params


def test_all_public_repository_methods_require_explicit_kindergarten_id() -> None:
    methods = {
        name: member
        for name, member in inspect.getmembers(SettingsRepository, inspect.isfunction)
        if not name.startswith("_")
    }
    assert methods
    for name, method in methods.items():
        assert "kindergarten_id" in inspect.signature(method).parameters, name


@pytest.mark.parametrize("method_name", ["list_semesters", "list_classes"])
def test_top_level_setting_reads_filter_by_kindergarten(method_name: str) -> None:
    connection = RecordingConnection()
    kindergarten_id = uuid4()
    repository = SettingsRepository(connection)

    getattr(repository, method_name)(kindergarten_id)

    _assert_queries_are_tenant_scoped(connection, kindergarten_id)


def test_class_area_reads_filter_by_kindergarten_and_class() -> None:
    connection = RecordingConnection()
    kindergarten_id = uuid4()
    class_id = uuid4()
    repository = SettingsRepository(connection)

    repository.list_class_areas(kindergarten_id, class_id, "indoor")

    _assert_queries_are_tenant_scoped(connection, kindergarten_id, class_id)


def test_class_area_writes_filter_by_kindergarten_and_class() -> None:
    connection = RecordingConnection()
    kindergarten_id = uuid4()
    class_id = uuid4()
    repository = SettingsRepository(connection)

    repository.replace_class_areas(
        kindergarten_id,
        class_id,
        "outdoor",
        ["沙水区", "种植区"],
        uuid4(),
    )

    _assert_queries_are_tenant_scoped(connection, kindergarten_id, class_id)
