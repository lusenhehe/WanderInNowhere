from __future__ import annotations

from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QWidget

from src.theme_manager import theme_manager
from .base_card import BaseCardQt


class EntityCardQt(BaseCardQt):
    def __init__(self,*,index: int,name: str,attitude: str,location: str = "",equipment: object | None,description: str = "",on_click=None,on_edit: Callable | None = None,on_delete: Callable | None = None,parent: QWidget | None = None,):
        super().__init__(parent)
        self.index = index
        self._on_click = on_click
        self._on_edit = on_edit
        self._on_delete = on_delete

        self.setObjectName("EntityCardQt")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._radius = 8

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        title = QLabel(name)
        title.setStyleSheet(f"font-weight: 700; color: {theme_manager.currentTheme.COLOR_TEXT_FG};")
        layout.addWidget(title)

        attitude_display = {"Enemy": "敌对", "Friendly": "友好", "Neutral": "中立"}.get(attitude, str(attitude))
        attitude_color = {
            "Enemy": "#ff4444",
            "Friendly": "#44ff44",
            "Neutral": theme_manager.currentTheme.COLOR_TEXT_SECONDARY,
        }.get(attitude, theme_manager.currentTheme.COLOR_TEXT_SECONDARY)

        att_label = QLabel(f"💭 态度: {attitude_display}")
        att_label.setStyleSheet(f"color: {attitude_color}; font-weight: 600;")
        layout.addWidget(att_label)

        if location:
            loc_label = QLabel(f"📍 地点: {location}")
            loc_label.setStyleSheet(f"color: {theme_manager.currentTheme.COLOR_TEXT_SECONDARY};")
            layout.addWidget(loc_label)

        if equipment:
            if isinstance(equipment, dict):
                equip_items = [str(v) for v in equipment.values() if v]
                equip_display = "\n".join(f"• {item}" for item in equip_items) if equip_items else "无装备"
            else:
                equip_display = str(equipment)
        else:
            equip_display = "无装备"

        equip_label = QLabel(f"⚔️ 装备: {equip_display}")
        equip_label.setWordWrap(True)
        equip_label.setStyleSheet(f"color: {theme_manager.currentTheme.COLOR_TEXT_SECONDARY};")
        layout.addWidget(equip_label)

        if description:
            desc = QLabel(f"📝 {description}")
            desc.setWordWrap(True)
            desc.setStyleSheet(
                f"color: {theme_manager.currentTheme.COLOR_TEXT_SECONDARY}; font-style: italic;"
            )
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
