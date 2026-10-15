from __future__ import annotations

from typing import Any, List
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLayout, QLabel, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class CommonUIUtils:
    """通用UI工具类，提供常用的UI创建和样式设置方法。"""

    @staticmethod
    def create_vertical_layout(
        widgets: List[QWidget | QLayout],
        *,
        margins: tuple[int, int, int, int] = (0, 0, 0, 0),
        spacing: int = 0,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignTop
    ) -> QVBoxLayout:
        """创建垂直布局并添加组件。"""
        layout = QVBoxLayout()
        layout.setContentsMargins(*margins)
        layout.setSpacing(spacing)
        layout.setAlignment(alignment)

        for widget in widgets:
            if isinstance(widget, QLayout):
                layout.addLayout(widget)
            else:
                layout.addWidget(widget)

        return layout

    @staticmethod
    def create_horizontal_layout(
        widgets: List[QWidget | QLayout],
        *,
        margins: tuple[int, int, int, int] = (0, 0, 0, 0),
        spacing: int = 0,
        alignment: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft
    ) -> QHBoxLayout:
        """创建水平布局并添加组件。"""
        layout = QHBoxLayout()
        layout.setContentsMargins(*margins)
        layout.setSpacing(spacing)
        layout.setAlignment(alignment)

        for widget in widgets:
            if isinstance(widget, QLayout):
                layout.addLayout(widget)
            else:
                layout.addWidget(widget)

        return layout

    @staticmethod
    def apply_common_font(
        widget: QLabel,
        *,
        size: int = 10,
        bold: bool = False,
        family: str = ""
    ) -> None:
        """应用通用字体样式。"""
        font = widget.font()
        if family:
            font.setFamily(family)
        font.setPointSize(size)
        font.setBold(bold)
        widget.setFont(font)
