"""桌面端浅色主题的语义视觉令牌。"""

from __future__ import annotations

COLORS = {
    "canvas": "#f3f6f7",
    "surface": "#ffffff",
    "surface_alt": "#edf4f3",
    "border": "#d8e3e3",
    "text": "#183033",
    "muted": "#66797c",
    "primary": "#177d77",
    "primary_hover": "#126963",
    "primary_soft": "#dff2ef",
    "warning": "#8d570d",
    "warning_soft": "#fff2d8",
}


def desktop_stylesheet() -> str:
    """Return the shared Qt stylesheet derived from semantic tokens."""

    return f"""
    QWidget#desktop_shell, QWidget#first_run_page, QWidget#daily_plan_page {{
        background: {COLORS["canvas"]};
        color: {COLORS["text"]};
        font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
        font-size: 14px;
    }}
    QLabel {{ background: transparent; }}
    QLabel[role="pageTitle"] {{ font-size: 21px; font-weight: 700; }}
    QLabel[role="sectionTitle"] {{ font-size: 16px; font-weight: 700; }}
    QLabel[role="fieldLabel"] {{ color: {COLORS["muted"]}; font-size: 12px; font-weight: 700; }}
    QLabel[role="muted"] {{ color: {COLORS["muted"]}; font-size: 12px; }}
    QLabel[tone="status"] {{
        color: {COLORS["primary"]}; background: {COLORS["primary_soft"]};
        border-radius: 10px; padding: 5px 10px;
    }}
    QLabel[tone="warning"] {{
        color: {COLORS["warning"]}; background: {COLORS["warning_soft"]};
        border-radius: 6px; padding: 5px 9px;
    }}
    QFrame#top_context, QFrame#week_strip, QFrame#section_navigation,
    QFrame#setup_card {{
        background: {COLORS["surface"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 10px;
    }}
    QFrame#field_card {{
        background: {COLORS["surface"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
    }}
    QScrollArea, QScrollArea > QWidget > QWidget, QStackedWidget {{
        background: {COLORS["canvas"]}; border: 0;
    }}
    QPushButton {{
        min-height: 32px; padding: 0 12px;
        background: {COLORS["surface"]};
        border: 1px solid {COLORS["border"]}; border-radius: 6px;
    }}
    QPushButton:hover {{ border-color: {COLORS["primary"]}; }}
    QPushButton[kind="primary"] {{
        color: white; background: {COLORS["primary"]};
        border-color: {COLORS["primary"]}; font-weight: 700;
    }}
    QPushButton[kind="primary"]:hover {{ background: {COLORS["primary_hover"]}; }}
    QPushButton[sectionActive="true"], QPushButton[weekActive="true"] {{
        color: #0e5d58; background: {COLORS["primary_soft"]};
        border-color: {COLORS["primary"]}; font-weight: 700;
    }}
    QFrame#section_navigation QPushButton {{ text-align: left; padding-left: 13px; }}
    QLineEdit, QPlainTextEdit, QComboBox, QDateEdit, QTableWidget {{
        color: {COLORS["text"]}; background: white;
        border: 1px solid {COLORS["border"]}; border-radius: 6px;
        padding: 7px; selection-background-color: {COLORS["primary"]};
    }}
    QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QDateEdit:focus,
    QTableWidget:focus {{ border-color: {COLORS["primary"]}; }}
    QHeaderView::section {{
        color: {COLORS["muted"]}; background: {COLORS["surface_alt"]};
        border: 0; border-bottom: 1px solid {COLORS["border"]};
        padding: 7px; font-weight: 700;
    }}
    """
