"""由同一组语义令牌派生的桌面浅色与深色主题。"""

from __future__ import annotations

from typing import Literal

ThemePreference = Literal["system", "light", "dark"]
ResolvedTheme = Literal["light", "dark"]

LIGHT_COLORS = {
    "canvas": "#f3f6f7",
    "surface": "#ffffff",
    "surface_alt": "#edf4f3",
    "field": "#ffffff",
    "border": "#d8e3e3",
    "text": "#183033",
    "muted": "#66797c",
    "primary": "#177d77",
    "primary_hover": "#126963",
    "primary_soft": "#dff2ef",
    "selected_text": "#0e5d58",
    "primary_text": "#ffffff",
    "warning": "#8d570d",
    "warning_soft": "#fff2d8",
}

DARK_COLORS = {
    "canvas": "#101718",
    "surface": "#182223",
    "surface_alt": "#1c302f",
    "field": "#111a1b",
    "border": "#334344",
    "text": "#e7eeee",
    "muted": "#9fb0b2",
    "primary": "#46b9ae",
    "primary_hover": "#5ac9be",
    "primary_soft": "#203f3c",
    "selected_text": "#8ee0d7",
    "primary_text": "#071817",
    "warning": "#f0b35a",
    "warning_soft": "#46351f",
}


def resolve_theme(preference: ThemePreference, *, system_is_dark: bool) -> ResolvedTheme:
    if preference == "system":
        return "dark" if system_is_dark else "light"
    return preference


def desktop_stylesheet(theme: ResolvedTheme = "light") -> str:
    """Return the shared Qt stylesheet derived from semantic tokens."""

    colors = DARK_COLORS if theme == "dark" else LIGHT_COLORS
    return f"""
    QWidget {{
        color: {colors["text"]};
        font-family: "Microsoft YaHei UI", "Segoe UI", sans-serif;
        font-size: 10.5pt;
    }}
    QWidget#desktop_shell, QWidget#first_run_page, QWidget#daily_plan_page,
    QWidget#settings_page {{
        color: {colors["text"]}; background: {colors["canvas"]};
    }}
    QLabel {{ color: {colors["text"]}; background: transparent; }}
    QLabel[role="pageTitle"] {{ font-size: 15.75pt; font-weight: 700; }}
    QLabel[role="sectionTitle"] {{ font-size: 12pt; font-weight: 700; }}
    QLabel[role="fieldLabel"] {{ color: {colors["muted"]}; font-size: 9pt; font-weight: 700; }}
    QLabel[role="muted"] {{ color: {colors["muted"]}; font-size: 9pt; }}
    QLabel[tone="status"] {{
        color: {colors["selected_text"]}; background: {colors["primary_soft"]};
        border-radius: 10px; padding: 5px 10px;
    }}
    QLabel[tone="warning"] {{
        color: {colors["warning"]}; background: {colors["warning_soft"]};
        border-radius: 6px; padding: 5px 9px;
    }}
    QFrame#top_context, QFrame#week_strip, QFrame#section_navigation,
    QFrame#setup_card, QFrame#settings_card {{
        color: {colors["text"]}; background: {colors["surface"]};
        border: 1px solid {colors["border"]}; border-radius: 10px;
    }}
    QFrame#field_card {{
        color: {colors["text"]}; background: {colors["surface"]};
        border: 1px solid {colors["border"]}; border-radius: 8px;
    }}
    QScrollArea, QScrollArea > QWidget > QWidget, QStackedWidget {{
        color: {colors["text"]}; background: {colors["canvas"]}; border: 0;
    }}
    QPushButton {{
        color: {colors["text"]}; min-height: 32px; padding: 0 12px;
        background: {colors["surface"]};
        border: 1px solid {colors["border"]}; border-radius: 6px;
    }}
    QPushButton:hover {{ border-color: {colors["primary"]}; }}
    QPushButton[kind="primary"] {{
        color: {colors["primary_text"]}; background: {colors["primary"]};
        border-color: {colors["primary"]}; font-weight: 700;
    }}
    QPushButton[kind="primary"]:hover {{ background: {colors["primary_hover"]}; }}
    QPushButton[sectionActive="true"], QPushButton[weekActive="true"] {{
        color: {colors["selected_text"]}; background: {colors["primary_soft"]};
        border-color: {colors["primary"]}; font-weight: 700;
    }}
    QFrame#section_navigation QPushButton {{ text-align: left; padding-left: 13px; }}
    QLineEdit, QPlainTextEdit, QComboBox, QDateEdit, QTableWidget {{
        color: {colors["text"]}; background: {colors["field"]};
        border: 1px solid {colors["border"]}; border-radius: 6px;
        padding: 7px; selection-background-color: {colors["primary"]};
        selection-color: {colors["primary_text"]};
    }}
    QComboBox QAbstractItemView, QCalendarWidget QWidget {{
        color: {colors["text"]}; background: {colors["surface"]};
        selection-background-color: {colors["primary_soft"]};
        selection-color: {colors["selected_text"]};
    }}
    QLineEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QDateEdit:focus,
    QTableWidget:focus {{ border-color: {colors["primary"]}; }}
    QHeaderView::section {{
        color: {colors["muted"]}; background: {colors["surface_alt"]};
        border: 0; border-bottom: 1px solid {colors["border"]};
        padding: 7px; font-weight: 700;
    }}
    QToolTip {{
        color: {colors["text"]}; background: {colors["surface"]};
        border: 1px solid {colors["border"]};
    }}
    """
