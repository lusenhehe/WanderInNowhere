import os
from PyQt6.QtGui import QFontDatabase
from src.paths import assets_path

_title_font_family = None

def ensure_title_font() -> str | None:
    """
    ensure_title_font : 确保标题字体已加载，并返回字体家族名称.
    :return: 字体家族名称或 None
    :rtype: str | None
    """
    global _title_font_family
    if _title_font_family:
        return _title_font_family
    title_font_path = assets_path('fonts', 'TitleFont', 'IslandMoments.ttf')
    if os.path.exists(title_font_path):
        font_id = QFontDatabase.addApplicationFont(title_font_path)
        if font_id != -1:
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                _title_font_family = families[0]
    return _title_font_family
