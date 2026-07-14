import sys
from importlib import import_module


def test_web_does_not_import_orm_models():
    """Web 层不得导入 ORM 模型, 确保依赖方向正确"""
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
                    f"Web 模块 {module_name} 导入了禁止的模块 {forbidden} "
                    f"(通过 {attr_name})"
                )


def test_web_uses_api_client():
    """Web 层应该通过 API 客户端访问业务能力"""
    from apps.web import main

    assert hasattr(main, "api_client"), "Web 层应该有 api_client"
    assert hasattr(main, "fetch_api"), "Web 层应该有 fetch_api 函数"


def test_bff_client_configured_with_api_base_url():
    """BFF 客户端应该配置正确的 API 基础 URL"""
    from apps.web import main

    assert main.api_client.base_url.host == "127.0.0.1"
    assert str(main.api_client.base_url.port) == "28000"
