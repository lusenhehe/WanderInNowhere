from __future__ import annotations
from typing import Callable
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QHBoxLayout, QVBoxLayout, QLabel, QWidget
from src.GUI.CustomWidgets.custom_button import CustomButton
from src.theme_manager import theme_manager
from .base_card import BaseCardQt
class QuestCardQt(BaseCardQt):
    def __init__(self,*,quest: dict,is_active: bool,on_click,on_abandon=None,on_edit: Callable | None = None,on_delete: Callable | None = None,parent: QWidget | None = None,):
        super().__init__(parent)
        self.quest = quest or {}
        self.is_active = is_active
        self._on_click = on_click
        self._on_abandon = on_abandon
        self._on_edit = on_edit
        self._on_delete = on_delete

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("QuestCardQt")

        self._radius = 10

        outer = QHBoxLayout(self)
        outer.setContentsMargins(10, 10, 10, 10)
        outer.setSpacing(12)

        icon = QLabel("📜")
        icon.setStyleSheet(f"color: {theme_manager.currentTheme.COLOR_ACCENT}; font-size: 18px;")
        outer.addWidget(icon)

        mid = QVBoxLayout()
        mid.setSpacing(4)
        outer.addLayout(mid, 1)

        title = QLabel(str(self.quest.get("title", "无标题")))
        title.setStyleSheet(f"font-weight: 800; color: {theme_manager.currentTheme.COLOR_TEXT_FG};")
        mid.addWidget(title)

        desc = str(self.quest.get("description", "") or "")
        if not is_active:
            desc = (desc[:80] + "…") if len(desc) > 80 else desc
        desc_label = QLabel(desc)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet(f"color: {theme_manager.currentTheme.COLOR_TEXT_SECONDARY};")
        mid.addWidget(desc_label)

        right = QVBoxLayout()
        right.setAlignment(Qt.AlignmentFlag.AlignTop)
        outer.addLayout(right)

        status_text = str(self.quest.get("status", ""))
        pill = QLabel(status_text)
        pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pill_bg = theme_manager.currentTheme.COLOR_BUTTON_NORMAL
        pill_fg = theme_manager.currentTheme.COLOR_BUTTON_FG
        pill.setStyleSheet(
            f"background-color: {pill_bg}; color: {pill_fg}; border-radius: 6px; padding: 4px 8px; font-weight: 700;"
        )
        right.addWidget(pill)

        if is_active:
            btn = CustomButton("放弃")
            btn.clicked.connect(self._abandon_clicked)
            right.addWidget(btn)

        self._update_style()

    def _abandon_clicked(self):
        if callable(self._on_abandon):
            self._on_abandon(self.quest)

    def mousePressEvent(self, ev: QMouseEvent):
        from src.GUI.QtComponents.debug_utils import debug_enabled

        if ev.button() == Qt.MouseButton.RightButton and debug_enabled():
            menu = self._build_context_menu()
            menu.exec(ev.globalPosition().toPoint())
            return

        if callable(self._on_click):
            try:
                self._on_click(self.quest, self)
            except TypeError:
                self._on_click(self.quest)

    def _build_context_menu(self):
        from PyQt6.QtWidgets import QMenu

        menu = QMenu()
        if callable(self._on_edit):
            menu.addAction("编辑", lambda: self._on_edit(self.quest, self))
        if callable(self._on_delete):
            menu.addAction("删除", lambda: self._on_delete(self.quest))
        if self.is_active and callable(self._on_abandon):
            menu.addAction("放弃", lambda: self._on_abandon(self.quest))
        return menu
