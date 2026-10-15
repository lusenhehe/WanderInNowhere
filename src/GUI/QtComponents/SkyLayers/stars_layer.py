import random
import math
from PyQt6.QtCore import QPointF, QSize
from PyQt6.QtGui import QPainter, QColor, QImage, QPixmap, QBrush
from .base import SkyLayer
from PyQt6.QtCore import Qt
import time
PALLETE = [
    QColor("#FFFFFF"),
    QColor("#FFF9E3"),
    QColor("#FFEEDD"),
    QColor("#FFDDAA"),
    QColor("#FFCC88"),
    QColor("#FFBB66"),
    QColor("#FFAA44"),
    QColor("#FF9933"),
    QColor("#FFFFFF"),
    QColor("#8CCBFF"),
    QColor("#FFD9A6"),
    QColor("#FFE3FF"),
    QColor("#C8FFA8"),
    QColor("#FFD0EA"),
    QColor("#B0D6FF"),
]
def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))
def _with_alpha(color: QColor, alpha: float) -> QColor:
    c = QColor(color)
    c.setAlphaF(_clamp(alpha, 0.0, 1.0))
    return c
class StarsLayer(SkyLayer):
    """星空图层"""
    def __init__(self):
        super().__init__()
        self._stars_pix = None
        self._stars_offset = QPointF(0.0, 0.0)
        self._stars_speed = QPointF(-15.0, -5)
        self._stars_tile = QSize(0, 0)
    def set_colors(self):
        pass
    def update(self, dt: float, size: QSize):
        # 贴图滚动：每帧仅更新偏移
        self._stars_offset = QPointF(
            self._stars_offset.x() + self._stars_speed.x() * dt,
            self._stars_offset.y() + self._stars_speed.y() * dt,
        )

    def ensure(self, size: QSize):
        if size == self._size and self._stars_pix is not None:
            return

        w = max(1, size.width())
        h = max(1, size.height())
        self._size = QSize(w, h)

        rng = random.Random(w * 1000003 + h * 9176)

        # 贴图尺寸：稍大便于平铺滚动
        self._stars_tile = QSize(max(420, min(1200, w + 220)), max(300, min(900, int(h * 0.86) + 220)))

        self._stars_pix = self._build_star_pix(self._stars_tile, rng)

    def _build_star_pix(self, tile: QSize, rng: random.Random) -> QPixmap:
        tw = max(1, tile.width())
        th = max(1, tile.height())
        img = QImage(tw, th, QImage.Format.Format_ARGB32_Premultiplied)
        img.fill(0)

        p = QPainter(img)
        try:
            p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            p.setPen(Qt.PenStyle.NoPen)
            count = int(_clamp((tw * th) * 0.016, 220, 900))
            palette = PALLETE
            for _ in range(count):
                x = rng.uniform(0, tw)
                y = rng.uniform(0, th)
                z = rng.random()  # 深度，0近1远
                r_base = rng.uniform(0.55, 2.6)
                r = r_base * (0.5 + 0.5 * (1 - z))  # 近处星星更大
                a_base = 0.08 + 0.78 * (rng.random() ** 2)
                a = a_base * (0.4 + 0.6 * (1 - z))  # 近处星星更亮
                c = palette[rng.randrange(len(palette))]
                c = _with_alpha(c, 1.0)
                p.setBrush(QBrush(_with_alpha(c, a)))
                p.drawEllipse(QPointF(x, y), r, r)
        finally:
            p.end()

        return QPixmap.fromImage(img)

    def _draw_tiled(self, painter: QPainter, pix: QPixmap, rect, offset: QPointF, *, opacity: float) -> None:
        if pix is None or pix.isNull():
            return

        pw = max(1, pix.width())
        ph = max(1, pix.height())
        # 使用"整型起点 + 整步长"平铺，避免 float -> int 截断导致 tile 边界出现 1px 缝
        ox = int(math.floor(float(offset.x()))) % pw
        oy = int(math.floor(float(offset.y()))) % ph

        painter.setOpacity(_clamp(opacity, 0.0, 1.0))

        left = int(rect.left())
        top = int(rect.top())
        right = int(rect.right())
        bottom = int(rect.bottom())

        x = left - ox - pw
        while x < right + pw:
            y = top - oy - ph
            while y < bottom + ph:
                painter.drawPixmap(x, y, pix)
                y += ph
            x += pw
        painter.setOpacity(1.0)  # 恢复透明度

    def paint(self, painter: QPainter, rect):
        # 星空：贴图平铺 + 缓慢滚动（性能极好）
        if self._stars_pix is not None:
            t = time.monotonic()
            twinkle = 0.90 + 0.10 * math.sin(t * 0.35)
            self._draw_tiled(painter, self._stars_pix, rect, self._stars_offset, opacity=twinkle)