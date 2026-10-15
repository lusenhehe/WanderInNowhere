import random, math
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QPointF, QSize, QRectF
from PyQt6.QtGui import QPainter, QColor, QRadialGradient, QBrush, QPainterPath
from .base import SkyLayer
def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))
def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t
def _with_alpha(color: QColor, alpha: float) -> QColor:
    c = QColor(color)
    c.setAlphaF(_clamp(alpha, 0.0, 1.0))
    return c
class MoonLayer(SkyLayer):
    """月亮图层"""
    def __init__(self, dx, dy):
        super().__init__()
        self._moon_color = QColor("#EAF5FF")
        self._moon_center = QPointF(dx, dy)
        self._moon_r = 70.0
        self._phase = 0.35  # 0 新月 -> 1 满月
        self._phase_dir = 1.0
        self._highlight_phase = 0.0

    def set_colors(self, moon: QColor, **kwargs):
        self._moon_color = QColor(moon)

    def update(self, dt: float, size: QSize):
        self._moon_center = QPointF(size.width() * 0.8, size.height() * 0.2)
        self._phase += self._phase_dir * dt * 0.02
        if self._phase > 0.92:
            self._phase = 0.92
            self._phase_dir = -1.0
        if self._phase < 0.08:
            self._phase = 0.08
            self._phase_dir = 1.0
        self._highlight_phase += dt * 0.2

    def ensure(self, size: QSize):
        if size == self._size:
            return

        w = max(1, size.width())
        h = max(1, size.height())
        self._size = QSize(w, h)

        rng = random.Random(w * 1000003 + h * 9176)

        # 月亮位置
        self._moon_r = rng.uniform(0.085, 0.12) * min(w, h)
        self._moon_center = QPointF(rng.uniform(0.68, 0.88) * w, rng.uniform(0.12, 0.26) * h)

    def paint(self, painter: QPainter, rect):
        # 明月：月面 + 光影（相位）
        mc = self._moon_center
        mr = self._moon_r

        painter.setPen(Qt.PenStyle.NoPen)
        moon = QRadialGradient(mc + QPointF(-mr * 0.16, -mr * 0.16), mr)
        moon.setColorAt(0.0, _with_alpha(QColor("#FFFFFF"), 0.92))
        moon.setColorAt(0.7, _with_alpha(self._moon_color, 0.92))
        moon.setColorAt(1.0, _with_alpha(QColor("#BFD7EE"), 0.92))
        painter.setBrush(QBrush(moon))
        painter.drawEllipse(mc, mr, mr)

        # 月亮阴影：用裁剪 + 偏移暗色渐变模拟"光影"
        path = QPainterPath()
        path.addEllipse(QRectF(mc.x() - mr, mc.y() - mr, mr * 2, mr * 2))
        painter.setClipPath(path)
        # phase 越大越亮（阴影越少），offset 控制终止线位置
        offset = _lerp(mr * 1.05, -mr * 0.25, self._phase)
        shadow_center = QPointF(mc.x() + offset, mc.y())
        shadow = QRadialGradient(shadow_center, mr * 1.25)
        shadow.setColorAt(0.0, _with_alpha(QColor("#0A0F20"), 0.85))
        shadow.setColorAt(0.55, _with_alpha(QColor("#0A0F20"), 0.55))
        shadow.setColorAt(1.0, _with_alpha(QColor("#0A0F20"), 0.0))
        painter.setBrush(QBrush(shadow))
        painter.drawEllipse(mc, mr, mr)
        painter.setClipping(False)

        # 添加动态高光
        highlight_center = mc + QPointF(mr * 0.3 * math.cos(self._highlight_phase), mr * 0.3 * math.sin(self._highlight_phase))
        highlight_r = mr * 0.15
        highlight = QRadialGradient(highlight_center, highlight_r)
        highlight.setColorAt(0.0, _with_alpha(QColor("#FFFFFF"), 0.6))
        highlight.setColorAt(1.0, _with_alpha(QColor("#FFFFFF"), 0.0))
        painter.setBrush(QBrush(highlight))
        painter.drawEllipse(highlight_center, highlight_r, highlight_r)