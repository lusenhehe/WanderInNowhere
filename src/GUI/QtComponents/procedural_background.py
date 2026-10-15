from __future__ import annotations
from dataclasses import dataclass
from PyQt6.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QColor,QImage,QLinearGradient,QPainter,QBrush,QPixmap
@dataclass(frozen=True)
class WesternFantasyPalette:
    """纯色背景配色"""
    # 默认仍然是深空紫黑；也支持渐变（可选）
    bg_deep: str = "#0a0a1e"      # 深空紫黑
    bg_top: str | None = None
    bg_bottom: str | None = None
class _FantasyBgSignals(QObject):
    generated = pyqtSignal(QImage, QSize, str)
class _GenerateFantasyBgTask(QRunnable):
    """生成西幻背景任务"""
    def __init__(self, size: QSize, palette: WesternFantasyPalette, cache_key: str):
        super().__init__()
        self._size = size
        self._palette = palette
        self._key = cache_key
        self.signals = _FantasyBgSignals()

    def run(self) -> None:
        w = max(1, int(self._size.width()))
        h = max(1, int(self._size.height()))

        img = QImage(w, h, QImage.Format.Format_ARGB32_Premultiplied)
        img.fill(0)

        painter = QPainter(img)
        try:
            # 背景：纯色 or 渐变
            if self._palette.bg_top and self._palette.bg_bottom:
                grad = QLinearGradient(0, 0, 0, h)
                grad.setColorAt(0.0, QColor(self._palette.bg_top))
                grad.setColorAt(1.0, QColor(self._palette.bg_bottom))
                painter.fillRect(0, 0, w, h, QBrush(grad))
            else:
                painter.fillRect(0, 0, w, h, QColor(self._palette.bg_deep))

        finally:
            painter.end()
        self.signals.generated.emit(img, self._size, self._key)
class WesternFantasyBackgroundRenderer(QObject):
    """西幻静态背景渲染器"""

    def __init__(self, *, parent: QObject | None = None):
        super().__init__(parent)
        self._pool = QThreadPool.globalInstance()
        self._pending: tuple[QSize, str] | None = None
        self._palette = WesternFantasyPalette()
        self._cache_key: str = ""
        self._last_size = QSize(0, 0)
        self._pixmap: QPixmap | None = None

        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(5)  # 防抖延迟
        self._debounce.timeout.connect(self._initiate_bg_generation)
    updated = pyqtSignal()
    def set_palette(self, palette: WesternFantasyPalette, *, cache_key: str) -> None:
        self._palette = palette
        self._cache_key = cache_key

    def request(self, size: QSize) -> None:
        if self._palette is None:
            return

        size = QSize(max(1, size.width()), max(1, size.height()))
        self._pending = (size, self._cache_key)
        self._debounce.start()

    def _initiate_bg_generation(self) -> None:
        if self._pending is None:
            return

        size, key = self._pending
        self._pending = None

        if self._pixmap is not None and self._last_size == size and key == self._cache_key:
            return

        task = _GenerateFantasyBgTask(size, self._palette, key)
        task.signals.generated.connect(self._on_bg_generated)
        self._pool.start(task)

    def _on_bg_generated(self, image: QImage, size: QSize, key: str) -> None:
        self._pixmap = QPixmap.fromImage(image)
        self._last_size = size
        self.updated.emit()

    def paint(self, painter: QPainter, rect) -> None:
        if self._pixmap is not None:
            painter.drawPixmap(rect, self._pixmap)
