"""Playwright 浏览器冒烟测试专用 Web 服务器启动脚本。

在子进程中启动 NiceGUI Web 服务器，绑定回环地址，避免与测试进程的
NiceGUI 全局状态冲突。通过环境变量配置：

- ``CHILD_MANAGER_TEST_API_BASE_URL``: API 服务器地址
- ``CHILD_MANAGER_TEST_WEB_PORT``: 监听端口

本脚本只在浏览器冒烟测试中以子进程方式运行，不参与普通单元测试。

调用方式：``python -m tests.web.browser_test_server``。必须以模块方式
运行，否则 ``apps`` 命名空间包无法在脚本直接执行模式下被正确解析。
"""

import os

from nicegui import ui

from apps.web.app import register_web

api_base_url = os.environ["CHILD_MANAGER_TEST_API_BASE_URL"]
port = int(os.environ["CHILD_MANAGER_TEST_WEB_PORT"])

register_web(api_base_url=api_base_url)
ui.run(host="127.0.0.1", port=port, reload=False, show=False, title="浏览器冒烟测试")
