# 集中式主题颜色默认值，用于在 ThemeManager 和样式中重用

THEME_DEFAULTS = {
    "COLOR_BG": "#222222",
    "COLOR_BUTTON_NORMAL": "#374151",
    "COLOR_BUTTON_ACTIVE": "#064E44",
    "COLOR_BUTTON_HOVER": "#0F766E",
    "COLOR_BUTTON_FG": "#ffffff",
    "COLOR_TEXT_BG": "#444444",
    "COLOR_TEXT_FG": "#e0e0e0",
    "COLOR_TEXT_SECONDARY": "#aaaaaa",
    "COLOR_BORDER": "#2a2a2a",
    "COLOR_TAB_BG": "#2a2a2a",
    "COLOR_TAB_FG": "#aaaaaa",
    "COLOR_TAB_SEL_BG": "#1e1e1e",
    "COLOR_TAB_SEL_FG": "#ffffff",
    "COLOR_ROLE_NAME": "#ffffff",
    "COLOR_SEPARATOR": "#555555",
    "COLOR_LOCATION": "#ffb347",
    "COLOR_WORLD_INFO": "#00ffcc",
    "COLOR_STATUS_HEADER": "#ffcc00",
    "COLOR_STATUS_LABEL": "#888888",
    "COLOR_STATUS_VALUE": "#ffffff",
    "COLOR_INJURY_BG": "#151515",
    "COLOR_INJURY_FG": "#ff5555",
    "COLOR_EQUIPMENT_HEADER": "#00ccff",
    "COLOR_EQUIPMENT_VALUE": "#ffd580",
    "COLOR_EQUIPMENT_EMPTY": "#555555",
    "COLOR_MONEY": "#ffd700",
    "COLOR_INVENTORY_BG": "#151515",
    "COLOR_INVENTORY_FG": "#eeeeee",
    "COLOR_CHAT_TITLE": "#aaaaaa",
    "COLOR_CHAT_USER": "#4da6ff",
    "COLOR_CHAT_USER_BG": "#374151",
    "COLOR_CHAT_USER_FG": "#ffffff",
    "COLOR_CHAT_ASSISTANT_BG": "#2a2a2a",
    "COLOR_CHAT_ASSISTANT_FG": "#e0e0e0",
    "COLOR_CHAT_SYSTEM": "#666666",
    "COLOR_CHAT_CURSOR": "#00ffcc",
    "COLOR_BG_SECONDARY": "#2e2e2e",
    "COLOR_ATTITUDE_ENEMY": "#ff5555",
    "COLOR_ATTITUDE_FRIENDLY": "#55ff55",
    "COLOR_ATTITUDE_NEUTRAL": "#ffff55",
    "COLOR_ACCENT": "#282f46",
    "COLOR_SHADOW": "#000000",
    "COLOR_HIGHLIGHT": "#ffffff",
    "COLOR_GRADIENT_START": "#333333",
    "COLOR_GRADIENT_END": "#1a1a1a",
    "COLOR_BLUR": "#444444",

    # 仅QSS助手
    "COLOR_PANEL_BG": "rgba(6, 18, 44, 0.65)",
    "COLOR_SELECTED_BG": "rgba(6, 200, 170, 0.35)",
    "COLOR_CARD_BG": "rgba(6, 18, 44, 0.60)",

    # 语义
    "COLOR_DANGER": "#ff6b6b",
    "COLOR_HP": "#FF5555",
    "COLOR_HUNGER": "#FFAA00",
    "COLOR_MAGIC": "#1f6aa5",
}

LIGHT_DEFAULTS = {
    "COLOR_BG": "#FFFFFF",
    "COLOR_BUTTON_NORMAL": "#374151",
    "COLOR_BUTTON_ACTIVE": "#064E44",
    "COLOR_BUTTON_HOVER": "#0F766E",
    "COLOR_BUTTON_FG": "#FFFFFF",
    "COLOR_TEXT_BG": "#FFFFFF",
    "COLOR_TEXT_FG": "#0F172A",
    "COLOR_ACCENT": "#282f46",
    "COLOR_BORDER": "#E6EDF8",
    "COLOR_BG_SECONDARY": "#F8FAFC",
    "COLOR_GRADIENT_START": "#FFFFFF",
    "COLOR_GRADIENT_END": "#F3F4F6",

    # 仅QSS助手
    "COLOR_PANEL_BG": "rgba(255, 255, 255, 0.85)",
    "COLOR_SELECTED_BG": "rgba(15, 118, 110, 0.18)",
    "COLOR_CARD_BG": "rgba(255, 255, 255, 0.85)",

    # 语义
    "COLOR_DANGER": "#dc2626",
    "COLOR_HP": "#dc2626",
    "COLOR_HUNGER": "#d97706",
    "COLOR_MAGIC": "#2563eb",
}
def get_theme_defaults(theme_name: str | None) -> dict:
    name = (theme_name or "").strip().lower()
    if name == "light" or name.startswith("light_"):
        return LIGHT_DEFAULTS
    return THEME_DEFAULTS
