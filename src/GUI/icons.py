import os
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter, QFont
from PyQt6.QtCore import QSize, Qt
from src.paths import assets_path
class IconManager:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IconManager, cls).__new__(cls)
        return cls._instance
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._icons = {}
    def _ensure_icons_loaded(self):
        if not self._icons:
            self._load_icons()
    def _load_icons(self):
        base_dir = assets_path('Images', 'icons')
        def load_or_fallback(name, emoji, color):
            svg_path = os.path.join(base_dir, f"{name}.svg")
            if os.path.exists(svg_path):
                try:
                    return QIcon(svg_path)
                except Exception:
                    pass
            return self._create_simple_icon(emoji, color)

        self._icons['save']      = load_or_fallback('save',     '💾', QColor('#4CAF50'))
        self._icons['settings']  = load_or_fallback('settings', '⚙',  QColor('#FF9800'))
        self._icons['play']      = load_or_fallback('play',     '▶',  QColor('#2196F3'))
        self._icons['pause']     = load_or_fallback('pause',    '⏸',  QColor('#FF5722'))
        self._icons['quest']     = load_or_fallback('quest',    '📜', QColor('#9C27B0'))
        self._icons['skill']     = load_or_fallback('skill',    '⭐', QColor('#FFC107'))
        self._icons['inventory'] = load_or_fallback('inventory','📦', QColor('#795548'))
        self._icons['chat']      = load_or_fallback('chat',     '💬', QColor('#00BCD4'))
        self._icons['entity']    = load_or_fallback('entity',   '👤', QColor('#E91E63'))
        self._icons['summary']   = load_or_fallback('summary',  '📄', QColor('#607D8B'))
        self._icons['status']    = load_or_fallback('status',   '❤️', QColor('#F44336'))
        self._icons['detail']    = load_or_fallback('detail',   '🔍', QColor('#3F51B5'))
        self._icons['money']     = load_or_fallback('money',    '💰', QColor('#FFD700'))

    def _create_simple_icon(self, emoji: str, color: QColor) -> QIcon:
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        # 绘制圆角背景
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        bg_color = QColor(color)
        bg_color.setAlpha(40)
        painter.setBrush(bg_color)
        painter.setPen(Qt.GlobalColor.transparent)
        painter.drawRoundedRect(0, 0, 64, 64, 12, 12)
        # 绘制表情符号
        font = QFont("Segoe UI Emoji", 32)
        painter.setFont(font)
        painter.setPen(Qt.GlobalColor.white)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, emoji)
        painter.end()
        return QIcon(pixmap)

    def get_icon(self, name: str, size: QSize = QSize(24, 24)) -> QIcon:
        """ 得到指定名称的图标，如果不存在则返回一个默认图标。"""
        self._ensure_icons_loaded()
        icon = self._icons.get(name)
        if icon:
            return icon
        # 回退到默认图标
        return self._create_simple_icon('❓', QColor('#9E9E9E'))

    def get_pixmap(self, name: str, size: QSize = QSize(24, 24)) -> QPixmap:
        """Get a pixmap by name, scaled to the given size."""
        icon = self.get_icon(name)
        return icon.pixmap(size)
# 全局实例
icon_manager = IconManager()