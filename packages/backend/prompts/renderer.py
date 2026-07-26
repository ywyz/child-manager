"""仅支持固定白名单纯替换词法的提示词渲染器。"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Set
from typing import Any

PLACEHOLDER = re.compile(r"\{\{[ \t]*([a-z][a-z0-9_]*)[ \t]*\}\}")


class PromptTemplateError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _variables(template: str) -> list[str]:
    matches = list(PLACEHOLDER.finditer(template))
    remainder = PLACEHOLDER.sub("", template)
    if "{{" in remainder or "}}" in remainder or "{%" in remainder or "%}" in remainder:
        raise PromptTemplateError("prompt.invalid_template", "提示词占位符格式无效。")
    return [match.group(1) for match in matches]


def validate_prompt_template(template: str, whitelist: Set[str]) -> tuple[str, ...]:
    if not template.strip():
        raise PromptTemplateError("prompt.invalid_template", "提示词正文不能为空。")
    variables = _variables(template)
    if any(variable not in whitelist for variable in variables):
        raise PromptTemplateError("prompt.invalid_template", "提示词包含未允许的变量。")
    return tuple(variables)


def _render_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def render_prompt(
    template: str,
    values: Mapping[str, Any],
    whitelist: Set[str],
) -> str:
    referenced = validate_prompt_template(template, whitelist)
    missing = sorted(set(referenced) - set(values))
    if missing:
        raise PromptTemplateError("prompt.missing_variable", "提示词缺少必需变量。")
    return PLACEHOLDER.sub(lambda match: _render_value(values[match.group(1)]), template)
