---
type: "query"
date: "2026-08-10T13:15:14.089868+00:00"
question: "通过人工测试，后台 PS C:\\Users\\admin\\code\\child-manager> uv run python -m kindergarten_manager 输出 QFont::setPointSize: Point size <= 0 (-1), must be greater than 0"
contributor: "graphify"
outcome: "useful"
source_nodes: ["desktop_stylesheet()", "theme.py", "main_window.py"]
---

# Q: 通过人工测试，后台 PS C:\Users\admin\code\child-manager> uv run python -m kindergarten_manager 输出 QFont::setPointSize: Point size <= 0 (-1), must be greater than 0

## Answer

Expanded from original query via graph vocab: [font, point, application, startup, stylesheet, theme, window, windows]. 当前桌面样式表以 px 设置全局及标签字号，使 QFont 成为像素字体且 pointSize() 返回 -1；Windows 原生样式复制点大小时触发警告。将 14/21/16/12px 等比例改为 10.5/15.75/12/9pt 后，真实主窗口全部控件恢复有效点大小，精确警告复现消失。

## Outcome

- Signal: useful

## Source Nodes

- desktop_stylesheet()
- theme.py
- main_window.py