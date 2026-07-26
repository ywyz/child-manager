from importlib import import_module
from typing import Any

import pytest


def _module() -> Any:
    try:
        return import_module("packages.backend.prompts.renderer")
    except ModuleNotFoundError:
        pytest.fail("T081 尚未提供唯一提示词渲染器", pytrace=False)


@pytest.mark.parametrize(
    ("template", "expected"),
    [
        ("日期：{{plan_date}}", "日期：2026-07-26"),
        ("日期：{{ plan_date }}", "日期：2026-07-26"),
        ("日期：{{\tplan_date\t}}", "日期：2026-07-26"),
    ],
)
def test_renderer_accepts_only_the_frozen_ascii_placeholder_grammar(
    template: str,
    expected: str,
) -> None:
    module = _module()
    assert module.render_prompt(template, {"plan_date": "2026-07-26"}, {"plan_date"}) == expected


@pytest.mark.parametrize(
    "template",
    [
        "{{\nplan_date}}",
        "{{\u00a0plan_date}}",
        "{{PlanDate}}",
        "{{_plan_date}}",
        "{{plan.date}}",
        "{{plan[date]}}",
        "{{plan_date|upper}}",
        "{{plan_date + 1}}",
        "{% for item in items %}",
        "{{unknown}}",
        "{{plan_date",
    ],
)
def test_renderer_rejects_every_non_frozen_placeholder_form(template: str) -> None:
    module = _module()
    with pytest.raises(module.PromptTemplateError):
        module.validate_prompt_template(template, {"plan_date"})


def test_renderer_uses_stable_json_and_never_recursively_renders_values() -> None:
    module = _module()
    rendered = module.render_prompt(
        "{{text}}|{{empty}}|{{flag}}|{{items}}|{{mapping}}",
        {
            "text": "{{nested}}",
            "empty": None,
            "flag": True,
            "items": ["二", "一"],
            "mapping": {"z": 1, "a": "先"},
        },
        {"text", "empty", "flag", "items", "mapping"},
    )

    assert rendered == '{{nested}}|null|true|["二","一"]|{"a":"先","z":1}'


def test_renderer_fails_for_missing_variable_before_external_call() -> None:
    module = _module()
    with pytest.raises(module.PromptTemplateError) as captured:
        module.render_prompt(
            "{{plan_date}} {{class_name}}", {"plan_date": "2026-07-26"}, {"plan_date", "class_name"}
        )
    assert captured.value.code == "prompt.missing_variable"
