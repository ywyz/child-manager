"""T037 可收集测试所需的设置 Repository 签名骨架。"""

from collections.abc import Sequence
from uuid import UUID


class SettingsRepository:
    """园所范围设置 Repository 的最小公共签名。"""

    def __init__(self, connection: object) -> None:
        self._connection = connection

    def list_semesters(self, kindergarten_id: UUID) -> list[object]:
        _ = kindergarten_id
        return []

    def list_classes(self, kindergarten_id: UUID) -> list[object]:
        _ = kindergarten_id
        return []

    def list_class_areas(
        self,
        kindergarten_id: UUID,
        class_id: UUID,
        area_type: str,
    ) -> list[object]:
        _ = (kindergarten_id, class_id, area_type)
        return []

    def replace_class_areas(
        self,
        kindergarten_id: UUID,
        class_id: UUID,
        area_type: str,
        names: Sequence[str],
        actor_id: UUID,
    ) -> None:
        _ = (kindergarten_id, class_id, area_type, names, actor_id)
