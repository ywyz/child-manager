import sys
from importlib import import_module


def test_web_does_not_import_orm_models():
    web_modules = [
        "apps.web.main",
        "apps.web.components",
        "apps.web.pages",
    ]

    forbidden_modules = [
        "sqlalchemy",
        "packages.backend.database.models",
        "packages.backend.database.session",
        "packages.backend.repository",
    ]

    for module_name in web_modules:
        if module_name not in sys.modules:
            import_module(module_name)

        module = sys.modules[module_name]
        for attr_name in dir(module):
            attr = getattr(module, attr_name, None)
            if attr is None:
                continue

            attr_module = getattr(attr, "__module__", "")
            for forbidden in forbidden_modules:
                assert forbidden not in attr_module, (
                    f"Web 模块 {module_name} 导入了禁止的模块 {forbidden} (通过 {attr_name})"
                )


def test_web_uses_api_client():
    from apps.web import main

    assert hasattr(main, "ApiClient"), "Web 层应该有 ApiClient 类"
    assert hasattr(main, "proxy_request"), "Web 层应该有 proxy_request 函数"


def test_bff_client_configured_with_api_base_url():
    from apps.web import main

    default_url = "http://127.0.0.1:28000"
    client = main.ApiClient(default_url)
    assert client.base_url == default_url
