import time
import random
import math
from dataclasses import dataclass
from PyQt6.QtCore import QPointF, QSize, QRect
from PyQt6.QtGui import QPainter, QColor, QRadialGradient, QBrush, QPen
from .base import SkyLayer
from PyQt6.QtCore import Qt
def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))
def _with_alpha(color: QColor, alpha: float) -> QColor:
    c = QColor(color)
    c.setAlphaF(_clamp(alpha, 0.0, 1.0))
    return c
def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t
@dataclass
class FantasyMeteor:
    born: float
    x0: float
    y0: float
    vx: float
    vy: float
    ay: float
    tail_seconds: float
    head_radius: float
    base_width: float
    head_color: QColor
    tail_color: QColor
    def is_alive(self, now: float, rect) -> bool:
        age = now - self.born
        if age < 0.0:
            return True  # 还没开始
        head = self._pos_at(age)
        pad = 120
        return rect.adjusted(-pad, -pad, pad, pad).contains(int(head.x()), int(head.y()))

    def _pos_at(self, t: float) -> QPointF:
        # 抛物线（屏幕坐标系 y 向下）
        x = self.x0 + self.vx * t
        y = self.y0 + self.vy * t + 0.5 * self.ay * t * t
        return QPointF(x, y)

    def draw(self, painter: QPainter, rect, now: float) -> None:
        age = now - self.born
        if age < 0.0:
            return

        # 头部位置
        head = self._pos_at(age)
        if not rect.contains(int(head.x()), int(head.y())):
            # 允许在边缘外一段，避免突然消失
            pad = 120
            if not rect.adjusted(-pad, -pad, pad, pad).contains(int(head.x()), int(head.y())):
                return

        # 尾迹采样：沿真实抛物线回溯，形成“曲线尾巴”
        tail_dt = 1 / 60
        steps = max(12, int(self.tail_seconds / tail_dt))
        tail_points: list[QPointF] = [head]
        for i in range(1, steps + 1):
            t = max(0.0, age - i * tail_dt)
            tail_points.append(self._pos_at(t))

        # 画尾迹：分段绘制，越远越细越透明
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        for i in range(len(tail_points) - 1):
            p0 = tail_points[i]
            p1 = tail_points[i + 1]
            k = i / max(1, (len(tail_points) - 2))  # 0 头部 -> 1 尾端

            width = _lerp(self.base_width, max(0.6, self.base_width * 0.2), k)
            alpha = (1.0 - k) ** 1.8
            # 先画一层更宽更淡的辉光拖尾，让尾迹更绚烂
            glow_alpha = alpha * 0.22
            glow_pen = QPen(_with_alpha(self.head_color, glow_alpha))
            glow_pen.setWidthF(width * 2.6)
            glow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(glow_pen)
            painter.drawLine(p0, p1)

            # 再画核心尾迹
            color = _with_alpha(self.tail_color, alpha * 0.9)

            pen = QPen(color)
            pen.setWidthF(width)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(p0, p1)

        # 头部附近少量火花点（轻微闪烁），增强质感
        flicker_base = (now - self.born) * 12.0
        for j in range(3):
            t = max(0.0, age - j * tail_dt * 2.0)
            pos = self._pos_at(t)
            flicker = 0.6 + 0.4 * math.sin(flicker_base + j * 2.1)
            a = (0.30 - j * 0.08) * flicker
            r = 9.0 - j * 2.0
            spark = QRadialGradient(pos, r)
            spark.setColorAt(0.0, _with_alpha(QColor("#FFFFFF"), a))
            spark.setColorAt(0.6, _with_alpha(self.head_color, a * 0.85))
            spark.setColorAt(1.0, _with_alpha(self.head_color, 0.0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(spark))
            painter.drawEllipse(pos, r, r)

        # 头部发光：外圈辉光 + 内核
        glow = QRadialGradient(head, self.head_radius * 2.8)
        glow.setColorAt(0.0, _with_alpha(self.head_color, 1.0))
        glow.setColorAt(0.35, _with_alpha(self.head_color, 0.55))
        glow.setColorAt(1.0, _with_alpha(self.head_color, 0.0))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(glow))
        r = self.head_radius * 2.8
        painter.drawEllipse(head, r, r)

        core = QRadialGradient(head, max(1.0, self.head_radius))
        core.setColorAt(0.0, _with_alpha(QColor("#FFFFFF"), 1.0))
        core.setColorAt(1.0, _with_alpha(self.head_color, 0.0))
        painter.setBrush(QBrush(core))
        painter.drawEllipse(head, self.head_radius, self.head_radius)

        painter.restore()
PALLETE = [
    QColor("#2F80ED"),
    QColor("#FFFFFF"),
    QColor("#FFD700"),
    QColor("#FF6B6B"),
    QColor("#4ECDC4"),
    QColor("#45B7D1"),
    QColor("#FF9F43"),
    QColor("#D980FA"),
    QColor("#32E875"),
    QColor("#8A2BE2"),
    QColor("#00BFFF"),
    QColor("#FF1493"),
    QColor("#F0E68C"),
    QColor("#00FA9A"),
    QColor("#FF7F50"),
    QColor("#9370DB"),
    QColor("#00CED1"),
    QColor("#FFB6C1"),
    QColor("#1E90FF"),
    QColor("#FF6347"),
    QColor("#98FB98"),
    QColor("#87CEEB"),
    QColor("#DDA0DD"),
    QColor("#F5DEB3"),
]
class MeteorLayer(SkyLayer):
    """流星雨图层"""

    def __init__(self):
        super().__init__()
        self._meteors: list[FantasyMeteor] = []
        self._max_meteors = 100
        self._colors = PALLETE
        self._next_spawn_at = 0.0
    def update(self, dt: float, size: QSize):
        # 更新现有流星
        now = time.monotonic()
        self._meteors = [m for m in self._meteors if m.is_alive(now, self._get_rect(size))]

        # 生成新流星
        self._maybe_spawn(size, now)
    def _get_rect(self, size: QSize):
        return QRect(0, 0, size.width(), size.height())
    def _maybe_spawn(self, size: QSize, now: float):
        """可能生成新的流星"""
        if len(self._meteors) >= self._max_meteors:
            return

        if now < self._next_spawn_at:
            return

        rect = self._get_rect(size)
        self._spawn(rect, now)
        # 随机生成间隔
        self._next_spawn_at = now + random.uniform(0.14, 0.32)

    def _spawn(self, rect, now: float):
        """生成单个流星"""
        w = max(1, rect.width())
        h = max(1, rect.height())

        # 起点：屏幕上方/左上方，向右下飞行
        x0 = random.uniform(-0.15 * w, -0.01 * w)
        y0 = random.uniform(-0.15 * h, 0.25 * h)

        # 速度：整体再慢一些，弧线更柔
        vx = random.uniform(300.0, 320.0)
        vy = random.uniform(50, 80)
        ay = 0  # 重力加速度更小（更"轻盈"）

        # 更慢速度下适当延长寿命/尾迹
        tail_seconds = random.uniform(0.45, 0.9)
        head_radius = random.uniform(1.8, 6.5)  # 更大范围
        base_width = random.uniform(1.0, 3.2)   # 更大范围

        head_color = random.choice(self._colors)
        # 尾迹稍偏冷、透明一些
        tail_color = QColor(head_color)
        tail_color.setAlphaF(0.85)

        self._meteors.append(
            FantasyMeteor(
                born=now,
                x0=x0,
                y0=y0,
                vx=vx,
                vy=vy,
                ay=ay,
                tail_seconds=tail_seconds,
                head_radius=head_radius,
                base_width=base_width,
                head_color=head_color,
                tail_color=tail_color,
            )
        )

    def paint(self, painter: QPainter, rect):
        """绘制流星雨"""
        if not self._meteors:
            return

        now = time.monotonic()
        for m in self._meteors:
            m.draw(painter, rect, now)