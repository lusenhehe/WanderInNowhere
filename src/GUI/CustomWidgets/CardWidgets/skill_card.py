from __future__ import annotations

from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QWidget

from src.theme_manager import theme_manager
from .base_card import BaseCardQt


class SkillCardQt(BaseCardQt):
    def __init__(self,*,index: int,name: str,description: str = "",on_click=None,on_edit: Callable | None = None,on_delete: Callable | None = None,parent: QWidget | None = None,):
        super().__init__(parent)
        self.index = index
        self._on_click = on_click
        self._on_edit = on_edit
        self._on_delete = on_delete

        self.setObjectName("SkillCardQt")
        self.setCursor(Qt.CursorShape.IBeamCursor)

        self._radius = 8

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        title = QLabel(name)
        title.setStyleSheet(f"font-weight: 700; color: {theme_manager.currentTheme.COLOR_TEXT_FG};")
        layout.addWidget(title)

        if description:
            desc = QLabel(description)
            desc.setWordWrap(True)
            desc.setStyleSheet(f"color: {theme_manager.currentTheme.COLOR_TEXT_SECONDARY};")
            layout.addWidget(desc)

        self._update_style()

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MouseButton.RightButton:
            from src.GUI.QtComponents.debug_utils import debug_enabled

            if not debug_enabled():
                return
            menu = self._build_context_menu()
            menu.exec(ev.globalPosition().toPoint())
            return

        if callable(self._on_click):
            self._on_click(self.index)

    def _build_context_menu(self):
        from PyQt6.QtWidgets import QMenu

        menu = QMenu()
        if callable(self._on_edit):
            menu.addAction("编辑", lambda: self._on_edit(self.index))
        if callable(self._on_delete):
            menu.addAction("删除", lambda: self._on_delete(self.index))
        return menu
