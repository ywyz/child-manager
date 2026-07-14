"""M1 包边界的最小可收集验证。"""

from importlib import import_module


def test_public_contract_and_backend_modules_are_importable() -> None:
    module_names = (
        "packages.contracts.common",
        "packages.contracts.identity",
        "packages.contracts.settings",
        "packages.contracts.lesson_plans",
        "packages.contracts.prompts",
        "packages.contracts.jobs",
        "packages.contracts.exports",
        "packages.contracts.audit",
        "packages.backend.ports",
    )

    assert all(import_module(module_name) for module_name in module_names)
