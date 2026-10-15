import random,math
from PyQt6.QtCore import QPointF, QSize
from PyQt6.QtGui import QPainter, QColor, QImage, QPixmap, QBrush, QRadialGradient, QLinearGradient
from .base import SkyLayer
from PyQt6.QtCore import Qt
def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))
def _with_alpha(color: QColor, alpha: float) -> QColor:
    c = QColor(color)
    c.setAlphaF(_clamp(alpha, 0.0, 1.0))
    return c
class FogLayer(SkyLayer):
    """雾气图层"""
    def __init__(self):
        super().__init__()
        self._fog_color            = QColor("#CFE6FF")
        self._fog_far_pix          = None
        self._fog_near_pix         = None
        self._fog_far_offset       = QPointF(0.0, 0.0)
        self._fog_near_offset      = QPointF(0.0, 0.0)
        self._fog_far_speed        = QPointF(-30.0, 1.8)
        self._fog_near_speed       = QPointF(-66.0, 3.6)
        self._fog_tile             = QSize(0, 0)
        self._fog_far_phase        = 0.0
        self._fog_near_phase       = 0.0
        self._fog_far_phase_speed  = 0.18
        self._fog_near_phase_speed = 0.33
        self._fog_far_base         = 0.46
        self._fog_near_base        = 0.60
        self._fog_far_amp          = 0.10
        self._fog_near_amp         = 0.14
        self._fog_far_opacity      = self._fog_far_base
        self._fog_near_opacity     = self._fog_near_base
    def set_colors(self, fog: QColor, **kwargs):
        self._fog_color = QColor(fog)
        self._fog_far_pix = None
        self._fog_near_pix = None
    def update(self, dt: float, size: QSize):
        # 贴图滚动：每帧仅更新偏移
        self._fog_far_offset = QPointF(
            self._fog_far_offset.x() + self._fog_far_speed.x() * dt,
            self._fog_far_offset.y() + self._fog_far_speed.y() * dt,
        )
        self._fog_near_offset = QPointF(
            self._fog_near_offset.x() + self._fog_near_speed.x() * dt,
            self._fog_near_offset.y() + self._fog_near_speed.y() * dt,
        )

        # 雾层透明度振荡（低频）
        self._fog_far_phase += self._fog_far_phase_speed * dt
        self._fog_near_phase += self._fog_near_phase_speed * dt
        self._fog_far_opacity = _clamp(self._fog_far_base + math.sin(self._fog_far_phase) * self._fog_far_amp, 0.0, 1.0)
        self._fog_near_opacity = _clamp(self._fog_near_base + math.sin(self._fog_near_phase) * self._fog_near_amp, 0.0, 1.0)
    def ensure(self, size: QSize):
        if size == self._size and self._fog_far_pix is not None and self._fog_near_pix is not None:
            return

        w = max(1, size.width())
        h = max(1, size.height())
        self._size = QSize(w, h)

        rng = random.Random(w * 1000003 + h * 9176)

        # 贴图尺寸：稍大便于平铺滚动
        self._fog_tile = QSize(max(520, min(1400, int(w * 0.95))), max(320, min(900, int(h * 0.62))))

        # 远雾薄、近雾厚：叠加产生更强的"翻腾"层次
        self._fog_far_pix = self._build_fog_pix(self._fog_tile, rng, intensity=0.75)
        self._fog_near_pix = self._build_fog_pix(self._fog_tile, rng, intensity=1.05)
    def _build_fog_pix(self, tile: QSize, rng: random.Random, *, intensity: float) -> QPixmap:
        tw = max(1, tile.width())
        th = max(1, tile.height())
        img = QImage(tw, th, QImage.Format.Format_ARGB32_Premultiplied)
        img.fill(0)

        p = QPainter(img)
        try:
            p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            p.setPen(Qt.PenStyle.NoPen)

            def draw_wrapped_ellipse(cx: float, cy: float, r: float, ry: float, a: float, *, mid: float = 0.55) -> None:
                # 周期性边界：边缘处把同一个雾团复制到对侧，平铺时无缝
                g = QRadialGradient(QPointF(cx, cy), r)
                g.setColorAt(0.0, _with_alpha(self._fog_color, a))
                g.setColorAt(mid, _with_alpha(self._fog_color, a * 0.58))
                g.setColorAt(1.0, _with_alpha(self._fog_color, 0.0))
                p.setBrush(QBrush(g))
                p.drawEllipse(QPointF(cx, cy), r, ry)

                # 只有在可能跨边界时才绘制复制，减少生成成本
                wrap_x = (cx - r) < 0 or (cx + r) > tw
                wrap_y = (cy - r) < 0 or (cy + r) > th
                if not (wrap_x or wrap_y):
                    return

                dxs = (0.0, -float(tw), float(tw)) if wrap_x else (0.0,)
                dys = (0.0, -float(th), float(th)) if wrap_y else (0.0,)
                for dx in dxs:
                    for dy in dys:
                        if dx == 0.0 and dy == 0.0:
                            continue
                        g2 = QRadialGradient(QPointF(cx + dx, cy + dy), r)
                        g2.setColorAt(0.0, _with_alpha(self._fog_color, a))
                        g2.setColorAt(mid, _with_alpha(self._fog_color, a * 0.58))
                        g2.setColorAt(1.0, _with_alpha(self._fog_color, 0.0))
                        p.setBrush(QBrush(g2))
                        p.drawEllipse(QPointF(cx + dx, cy + dy), r, ry)

            # 不规则雾：大量渐变团叠加（一次性渲染）
            blobs = int(_clamp((tw * th) * 0.00028, 90, 260))
            for _ in range(blobs):
                cx = rng.uniform(0, tw)
                cy = rng.uniform(0, th)
                r = rng.uniform(0.08 * tw, 0.26 * tw)
                ry = r * rng.uniform(0.18, 0.42)
                a = intensity * rng.uniform(0.010, 0.055)

                draw_wrapped_ellipse(cx, cy, r, ry, a, mid=0.55)

            # 细丝雾：增强层次
            wisps = int(_clamp(tw / 16, 26, 80))
            for _ in range(wisps):
                cx = rng.uniform(0, tw)
                cy = rng.uniform(0.20 * th, th)
                r = rng.uniform(0.05 * tw, 0.14 * tw)
                ry = r * rng.uniform(0.12, 0.28)
                a = intensity * rng.uniform(0.006, 0.020)
                # 细丝雾更锐：中点更靠近中心
                draw_wrapped_ellipse(cx, cy, r, ry, a, mid=0.40)
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
        h = rect.height()
        # 雾气：两层不规则雾贴图叠加，offset 差速滚动制造"翻腾"
        if self._fog_far_pix is not None:
            self._draw_tiled(painter, self._fog_far_pix, rect, self._fog_far_offset, opacity=self._fog_far_opacity)
        if self._fog_near_pix is not None:
            self._draw_tiled(painter, self._fog_near_pix, rect, self._fog_near_offset, opacity=self._fog_near_opacity)

        # 上方渐隐（雾主要在下方/近景）
        fog_fade = QLinearGradient(0, 0, 0, h)
        fog_fade.setColorAt(0.0, _with_alpha(QColor("#06122C"), 0.86))
        fog_fade.setColorAt(0.48, _with_alpha(QColor("#06122C"), 0.0))
        fog_fade.setColorAt(1.0, _with_alpha(QColor("#06122C"), 0.0))
        painter.setBrush(QBrush(fog_fade))
        painter.drawRect(rect)