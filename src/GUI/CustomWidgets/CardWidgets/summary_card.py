from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget

from src.theme_manager import theme_manager
from .base_card import BaseCardQt


class SummaryCardQt(BaseCardQt):
    def __init__(self,*,index: int,content: str,level: int = 1,selected: bool = False,on_toggle=None,parent: QWidget | None = None,):
        super().__init__(parent)
        self.index = index
        self.level = int(level or 1)
        self._selected = bool(selected)
        self._on_toggle = on_toggle

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("SummaryCardQt")

        self._radius = 10

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        header = QHBoxLayout()
        header.setSpacing(8)
        layout.addLayout(header)

        title = QLabel(f"摘要 #{index + 1}")
        title.setStyleSheet("font-weight: 800;")
        header.addWidget(title)

        lvl = QLabel(f"Lv.{self.level}")
        lvl.setStyleSheet(f"font-weight: 700; color: {self._level_color(self.level)};")
        header.addWidget(lvl)
        header.addStretch(1)

        self.content_lbl = QLabel(content or "")
        self.content_lbl.setWordWrap(True)
        self.content_lbl.setStyleSheet(f"color: {theme_manager.currentTheme.COLOR_TEXT_FG};")
        layout.addWidget(self.content_lbl)

        self._update_style()

    @staticmethod
    def _level_color(level: int) -> str:
        if level <= 1:
            return theme_manager.currentTheme.COLOR_LEVEL_TEXT
        if level == 2:
            return theme_manager.currentTheme.COLOR_MONEY
        return theme_manager.currentTheme.COLOR_ACCENT

    def mousePressEvent(self, _ev):
        self._selected = not self._selected
        self._update_style()
        if callable(self._on_toggle):
            self._on_toggle(self.index, self._selected)

    def _update_style(self):
        obj = self.objectName() or "SummaryCardQt"
        bg = "transparent"
        border_color = "rgba(100,100,100,100)"
        border_width = 1
        if self._selected:
            border_color = theme_manager.currentTheme.COLOR_LEVEL_TEXT  # 例如使用主题的强调色
            border_width = 3  # 变粗
        qss = f"""
            #{obj} {{
                background-color: {bg};
                border: {border_width}px solid {border_color};
                border-radius: {int(self._radius)}px;
            }}
            #{obj} QLabel {{
                background: transparent;
                border: none;
            }}
            #{obj} QFrame {{
                background: transparent;
                border: none;
            }}
            """
        self.setStyleSheet(qss)
        self.update()
