"""NiceGUI 页面级冒烟测试入口。

该文件仅用于测试，注册 Web 页面与 BFF 路由；API 调用在测试中被
JavaScript 规则拦截，因此 api_base_url 只需占位即可。
"""

import os

from nicegui import ui

from apps.web.app import register_web

_API_BASE_URL = os.environ.get("CHILD_MANAGER_TEST_API_BASE_URL", "http://testserver")
register_web(api_base_url=_API_BASE_URL)
ui.run()
