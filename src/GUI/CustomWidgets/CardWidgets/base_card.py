from __future__ import annotations
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QFrame, QWidget
from src.GUI.QtComponents.cards import animate_card_hover, enable_card_shadow
class BaseCardQt(QFrame):
    """
    BaseCardQt 的 Docstring
    基类，用于所有卡片式组件，提供基本的样式和交互功能。
    继承自 QFrame，支持圆角、阴影和悬停动画

    属性:
        _selected (bool): 卡片是否被选中。
        _hovered (bool): 卡片当前是否处于悬停状态。
        _hover_phase (float): 悬停动画的相位，用于生成动态背景
    方法:
        set_selected(selected: bool) -> None:
            设置卡片的选中状态并更新样式。
        on_hover_changed(hovered: bool) -> None:
            当悬停状态改变时调用，子类可重写以提供自定义行为。
        extra_qss() -> str:
            子类可重写以提供额外的 QSS 样式。
        enterEvent(ev) -> None:
            处理鼠标进入事件，启动悬停动画并更新样式。
        leaveEvent(ev) -> None:
            处理鼠标离开事件，停止悬停动画并更新样式。
        _tick_hover() -> None:
            悬停动画的定时器回调，更新悬停相位并刷新样式。
        _wave_background() -> str:
            生成动态波浪背景的 QSS 字符串。
        _update_style() -> None:
            更新卡片的 QSS 样式并刷新显示。
    """

    def __init__(self, parent: QWidget | None = None, *, enable_shadow: bool = True):
        super().__init__(parent)

        # Prevent QFrame native frame painting (can look like a second border)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setLineWidth(0)
        self.setMidLineWidth(0)

        self._selected = False
        self._hovered = False
        self._hover_phase = 0.0

        # Style knobs (subclasses may tweak these)
        self._radius = 10
        self._border_width = 1
        self._wave_alpha = 0.50

        self._hover_timer = QTimer(self)
        self._hover_timer.setInterval(10)
        self._hover_timer.timeout.connect(self._tick_hover)

        if enable_shadow:
            try:
                enable_card_shadow(self)
            except Exception:
                pass

    def set_selected(self, selected: bool) -> None:
        self._selected = bool(selected)
        self._update_style()

    def on_hover_changed(self, hovered: bool) -> None:
        """Called when hover state changes.

        Subclasses can override to provide custom behavior.
        """
        pass
    def extra_qss(self) -> str:
        """Subclasses can override to provide extra QSS styling."""
        return ""

    # ---- Hover animation ----
    def enterEvent(self, ev):
        self._hovered = True
        try:
            animate_card_hover(self, True)
        except Exception:
            pass
        if not self._hover_timer.isActive():
            self._hover_timer.start()
        self._update_style()
        try:
            self.on_hover_changed(True)
        finally:
            super().enterEvent(ev)

    def leaveEvent(self, ev):
        self._hovered = False
        try:
            animate_card_hover(self, False)
        except Exception:
            pass
        self._hover_timer.stop()
        self._update_style()
        try:
            self.on_hover_changed(False)
        finally:
            super().leaveEvent(ev)

    def _tick_hover(self) -> None:
        if not self._hovered:
            return
        self._hover_phase = (self._hover_phase + 0.02) % 1.0
        self._update_style()

    # ---- Styling ----
    def _wave_background(self) -> str:
        hue1 = int(self._hover_phase * 360) % 360
        hue2 = (hue1 + 180) % 360
        color1 = QColor.fromHsv(hue1, 200, 255)
        color2 = QColor.fromHsv(hue2, 200, 255)
        r1, g1, b1, _ = color1.getRgb()
        r2, g2, b2, _ = color2.getRgb()
        a = float(self._wave_alpha)
        return (
            "qlineargradient(x1:0, y1:0, x2:1, y2:1, "
            f"stop:0 rgba({r1},{g1},{b1},{a}), "
            f"stop:1 rgba({r2},{g2},{b2},{a}))"
        )

    def _update_style(self) -> None:
        obj = self.objectName() or "BaseCardQt"
        bg  = self._wave_background() if self._hovered else "transparent"
        qss = f"""
            #{obj} {{
                background-color: {bg};
                border: 1px solid rgba(100,100,100,100);
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
        extra = self.extra_qss()
        if extra:
            qss += f"\n{extra}"
        self.setStyleSheet(qss)
        self.update()
