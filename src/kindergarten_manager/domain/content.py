"""结构化教案内容公共接口；行为在 Slice 1 GREEN 实现。"""

from __future__ import annotations

from typing import Any, Self


class PlanContentV1:
    @classmethod
    def empty(cls) -> Self:
        raise NotImplementedError("T020 尚未实现空教案内容")

    @classmethod
    def model_validate(cls, value: Any) -> Self:
        raise NotImplementedError("T020 尚未实现教案内容校验")

    def model_dump(self, *, mode: str = "python") -> dict[str, Any]:
        raise NotImplementedError("T020 尚未实现教案内容序列化")

    def canonical_json(self) -> str:
        raise NotImplementedError("T020 尚未实现规范 JSON")
