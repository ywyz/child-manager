"""教案保存状态的文字与样式契约。"""

from dataclasses import dataclass
from typing import Literal

SaveState = Literal["idle", "saving", "saved", "failed", "conflict"]


@dataclass(frozen=True, slots=True)
class SaveStatus:
    text: str
    css_class: str


def save_status(state: SaveState) -> SaveStatus:
    return {
        "idle": SaveStatus("尚未保存", "text-grey-8"),
        "saving": SaveStatus("保存中", "text-blue-9"),
        "saved": SaveStatus("已保存", "text-positive"),
        "failed": SaveStatus("保存失败", "text-negative"),
        "conflict": SaveStatus("内容已被他人修改，请刷新", "text-negative"),
    }[state]
