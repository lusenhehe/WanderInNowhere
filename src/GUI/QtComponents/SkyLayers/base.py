from __future__ import annotations
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QPainter
class SkyLayer:
    """天空图层基类"""

    def __init__(self):
        self._size = QSize(0, 0)

    def set_colors(self, **kwargs):
        """设置颜色，子类可以重写"""
        pass

    def update(self, dt: float, size: QSize):
        """更新图层状态"""
        pass

    def ensure(self, size: QSize):
        """确保资源已准备好"""
        pass

    def paint(self, painter: QPainter, rect):
        """绘制图层"""
        pass

    def set_size(self, size: QSize):
        """设置尺寸"""
        if size != self._size:
            self._size = QSize(size)
            self.ensure(size)