"""按 API capabilities 生成导航。"""


def navigation_for_capabilities(capabilities: list[str]) -> tuple[str, ...]:
    items = ["首页"]
    if "plans:view" in capabilities:
        items.append("教案")
    if "users:manage" in capabilities:
        items.append("账号管理")
    if "credentials:manage" in capabilities:
        items.append("通行密钥与会话")
    if "settings:manage" in capabilities:
        items.append("系统设置")
    if "class_areas:manage" in capabilities:
        items.append("班级区域")
    return tuple(items)
