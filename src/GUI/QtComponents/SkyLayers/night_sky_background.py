from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QBrush
from .base import SkyLayer


class NightSkyBackground(SkyLayer):
    """夜空背景图层"""

    def __init__(self):
        super().__init__()
        self._night_top = QColor("#06122C")
        self._night_bottom = QColor("#020614")

    def set_colors(self, night_top: QColor, night_bottom: QColor, **kwargs):
        self._night_top = QColor(night_top)
        self._night_bottom = QColor(night_bottom)

    def paint(self, painter: QPainter, rect):
        h = rect.height()
        # 夜空加深：轻薄覆盖层（保证整体深蓝）
        sky = QLinearGradient(0, 0, 0, h)
        sky.setColorAt(0.0, self._night_top)
        sky.setColorAt(1.0, self._night_bottom)
        painter.setBrush(QBrush(sky))
        painter.drawRect(rect)