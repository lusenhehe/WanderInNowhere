from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget, QGraphicsDropShadowEffect
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
from src.theme_manager import theme_manager
from src.utils.logger import logger
class Card(QFrame):
    def __init__(self,title: str | None = None,*,parent: QWidget | None = None,content_margins: tuple[int, int, int, int] = (12, 10, 12, 12),spacing: int = 8,):
        super().__init__(parent)
        self.setObjectName("Card")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(*content_margins)
        self._layout.setSpacing(spacing)
        self._title_label: QLabel | None = None
        if title:
            self._title_label = QLabel(title)
            self._title_label.setObjectName("CardTitle")
            from src.GUI.QtComponents.common_ui_utils import CommonUIUtils
            CommonUIUtils.apply_common_font(self._title_label, size=11, bold=True)
            self._layout.addWidget(self._title_label)

        self._body = QWidget(self)
        self.body_layout = QVBoxLayout(self._body)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(spacing)
        self._layout.addWidget(self._body)
def enable_card_shadow(frame: QFrame, *, accent_color: str | None = None):
    """
    启用卡片阴影效果
    通过动画实现悬停时阴影模糊半径变化
    """
    try:
        color_hex = accent_color or theme_manager.currentTheme.COLOR_ACCENT
        c = QColor(color_hex)
        c.setAlpha(90)

        eff = QGraphicsDropShadowEffect(frame)
        eff.setBlurRadius(6)
        eff.setOffset(0, 2)
        eff.setColor(c)
        frame.setGraphicsEffect(eff)

        anim = QPropertyAnimation(eff, b"blurRadius")
        anim.setDuration(180)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        setattr(frame, "_card_shadow_effect", eff)
        setattr(frame, "_card_shadow_anim", anim)
    except Exception:
        logger.error(f"启用卡片阴影效果失败 于 {frame}", exc_info=True)
        pass
def animate_card_hover(frame: QFrame, hover: bool):
    eff = getattr(frame, "_card_shadow_effect", None)
    anim = getattr(frame, "_card_shadow_anim", None)
    if eff is None or anim is None:
        return
    try:
        anim.stop()
        start = eff.blurRadius()
        end = 14 if hover else 6
        anim.setStartValue(start)
        anim.setEndValue(end)
        anim.start()
    except Exception:
        logger.error(f"卡片阴影动画失败 于 {frame}", exc_info=True)