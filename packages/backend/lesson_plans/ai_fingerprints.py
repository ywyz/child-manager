"""AI 预览使用的规范化栏目与输入指纹。"""

from __future__ import annotations

import json
from collections.abc import Mapping
from hashlib import sha256

from packages.contracts.lesson_plans import AiTaskCode

type JsonScalar = str | int | float | bool | None
type JsonValue = JsonScalar | list[JsonValue] | dict[str, JsonValue]


def canonical_json_sha256(value: JsonValue) -> str:
    """对 JSON 值进行稳定序列化并计算 SHA-256。"""

    payload = json.dumps(
        value,
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return sha256(payload).hexdigest()


def section_sha256(section: Mapping[str, JsonValue]) -> str:
    """计算单个目标栏目的规范化内容哈希。"""

    return canonical_json_sha256(dict(section))


def generation_input_sha256(
    *,
    task_code: AiTaskCode,
    teacher_context: str | None,
    server_input: Mapping[str, JsonValue],
) -> str:
    """计算逐任务实际输入哈希。

    ``server_input`` 只应包含该任务白名单内的服务端输入。采用预览时，调用方必须复用任务
    创建时冻结的 ``teacher_context``，并重新读取其余可变服务端输入。
    """

    return canonical_json_sha256(
        {
            "server_input": dict(server_input),
            "task_code": task_code,
            "teacher_context": teacher_context,
        }
    )


__all__ = [
    "JsonScalar",
    "JsonValue",
    "canonical_json_sha256",
    "generation_input_sha256",
    "section_sha256",
]
