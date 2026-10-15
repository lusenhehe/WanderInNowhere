from __future__ import annotations

from typing import Callable, Optional

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QWidget

from src.GUI.icons import icon_manager
from src.theme_manager import theme_manager
from .base_card import BaseCardQt


class InventoryItemCardQt(BaseCardQt):
    def __init__(self,name: str,*,is_equipment: bool = False,slot_id: str = "",on_click: Optional[Callable] = None,on_edit: Callable | None = None,on_delete: Callable | None = None,parent: Optional[QWidget] = None,) -> None:
        super().__init__(parent)
        self.setObjectName("InventoryItemCardQt")

        self.name = name
        self.is_equipment = is_equipment
        self.slot_id = slot_id
        self.on_click = on_click
        self.on_edit = on_edit
        self.on_delete = on_delete

        self._radius = 6 if self.is_equipment else 10

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        if self.is_equipment:
            self.icon_label = QLabel()
            self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.icon_label.setPixmap(icon_manager.get_pixmap("status", QSize(18, 18)))
            layout.addWidget(self.icon_label)

            self.name_label = QLabel(name)
            self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.name_label.setStyleSheet(
                f"color: {theme_manager.currentTheme.COLOR_TEXT_SECONDARY}; font-size: 9px;"
            )
            layout.addWidget(self.name_label)

            self.item_label = QLabel("（空）")
            self.item_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.item_label.setWordWrap(True)
            self.item_label.setStyleSheet(
                f"color: {theme_manager.currentTheme.COLOR_EQUIPMENT_EMPTY}; font-size: 9px; font-weight: bold;"
            )
            layout.addWidget(self.item_label)
            self.setFixedSize(60, 60)
        else:
            self.name_label = QLabel(name)
            self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.name_label.setWordWrap(True)
            self.name_label.setStyleSheet("font-size: 11px; font-weight: 600;")
            layout.addWidget(self.name_label)
            self.setFixedSize(50, 50)
        self._update_style()
    def _update_style(self):
        obj = self.objectName() or "BaseCardQt"
        bg = self._wave_background() if self._hovered else "transparent"
        qss = f"""
            #{obj} {{
                background-color: {bg};
                border: 2px solid {theme_manager.currentTheme.COLOR_BORDER};
                border-radius: 4px;
            }}
            """
        extra = self.extra_qss()
        if extra:
            qss += "\n" + extra
        self.setStyleSheet(qss)
        self.update()

    def set_item(self, item_name: Optional[str]) -> None:
        if not self.is_equipment:
            return
        if item_name:
            self.item_label.setText(item_name)
            self.item_label.setStyleSheet(
                f"color: {theme_manager.currentTheme.COLOR_EQUIPMENT_VALUE}; font-size: 9px; font-weight: bold;"
            )
        else:
            self.item_label.setText("（空）")
            self.item_label.setStyleSheet(
                f"color: {theme_manager.currentTheme.COLOR_EQUIPMENT_EMPTY}; font-size: 9px; font-weight: bold;"
            )

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            from src.GUI.QtComponents.debug_utils import debug_enabled

            if debug_enabled():
                menu = self._build_context_menu()
                menu.exec(event.globalPosition().toPoint())
                return

        if self.on_click:
            if self.is_equipment:
                self.on_click(self.slot_id)
            else:
                self.on_click()

        super().mousePressEvent(event)

    def _build_context_menu(self):
        from PyQt6.QtWidgets import QMenu

        menu = QMenu()
        if callable(self.on_edit):
            menu.addAction("编辑", self.on_edit)
        if callable(self.on_delete):
            menu.addAction("删除", self.on_delete)
        return menu
