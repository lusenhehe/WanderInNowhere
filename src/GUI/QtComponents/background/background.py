from PyQt6.QtCore import QObject, QSize, QTimer
from PyQt6.QtGui import QPainter, QColor
from ..procedural_background import WesternFantasyPalette,WesternFantasyBackgroundRenderer
from ..SkyLayers.base import SkyLayer
class DynamicSky(QObject):
    """动态天空管理器"""

    def __init__(self, *, parent=None):
        super().__init__(parent)
        self._layers = []
        self._timer = QTimer(self)
        self._size = QSize(800, 600)  # 默认大小
        self._timer.timeout.connect(self._update_layers)
        self._fps = 30

    def set_fps(self, fps: int):
        self._fps = fps
        self._timer.setInterval(1000 // fps)
        if self._layers:
            self._timer.start()

    def set_size(self, size: QSize):
        """设置天空大小"""
        self._size = QSize(size)

    def addLayer(self, layer: SkyLayer):
        if layer not in self._layers:
            self._layers.append(layer)
            if not self._timer.isActive():
                self._timer.start()

    def removeLayer(self, layer: SkyLayer):
        if layer in self._layers:
            self._layers.remove(layer)
            if not self._layers:
                self._timer.stop()

    def getLayers(self):
        return self._layers.copy()

    def set_colors(self, **kwargs):
        for layer in self._layers:
            layer.set_colors(**kwargs)

    def _update_layers(self):
        dt = 1.0 / self._fps
        for layer in self._layers:
            layer.update(dt, self._size)

    def paint(self, painter: QPainter, rect):
        size = QSize(rect.width(), rect.height())
        for layer in self._layers:
            layer.set_size(size)
            layer.ensure(size)
            layer.paint(painter, rect)

    @property
    def updated(self):
        # 返回定时器信号作为更新信号
        return self._timer.timeout
class BackGround(QObject):
    """背景渲染基类"""

    def __init__(self, *, parent=None):
        super().__init__(parent)
        self._size = QSize(800, 600)  # 默认大小，会在paint时更新
        self._background_renderer = None
        self._dynamic_sky = None

    def set_static_background(self, palette: WesternFantasyPalette, cache_key: str):
        """设置静态背景"""
        if self._background_renderer is None:
            self._background_renderer = WesternFantasyBackgroundRenderer(parent=self.parent())
        self._background_renderer.set_palette(palette, cache_key=cache_key)

    def set_dynamic_sky(self, fps: int = 30):
        """设置动态天空"""
        if self._dynamic_sky is None:
            self._dynamic_sky = DynamicSky(parent=self)
        self._dynamic_sky.set_fps(fps)

    def set_colors(self, *, night_top: QColor, night_bottom: QColor, moon: QColor, fog: QColor):
        """设置动态天空颜色"""
        if self._dynamic_sky:
            self._dynamic_sky.set_colors(
                night_top=night_top,
                night_bottom=night_bottom,
                moon=moon,
                fog=fog
            )

    def request_size(self, size: QSize):
        """请求背景重新生成"""
        if self._background_renderer:
            self._background_renderer.request(size)
        if self._dynamic_sky:
            self._dynamic_sky.set_size(size)

    def paint(self, painter: QPainter, rect):
        """绘制背景"""
        size = QSize(rect.width(), rect.height())
        
        # 更新大小
        if size != self._size:
            self._size = QSize(size)
            if self._dynamic_sky:
                self._dynamic_sky.set_size(size)
        
        # 先绘制静态背景
        if self._background_renderer:
            self._background_renderer.paint(painter, rect)

        # 再绘制动态天空
        if self._dynamic_sky:
            self._dynamic_sky.paint(painter, rect)

    @property
    def updated(self):
        """获取更新信号"""
        # 返回一个组合的信号，或者主要信号
        if self._dynamic_sky:
            return self._dynamic_sky.updated
        elif self._background_renderer:
            return self._background_renderer.updated
        return None

    def add_layer(self, layer):
        """添加图层到动态天空"""
        if self._dynamic_sky:
            self._dynamic_sky.addLayer(layer)

    def remove_layer(self, layer):
        """从动态天空移除图层"""
        if self._dynamic_sky:
            self._dynamic_sky.removeLayer(layer)

    def get_layers(self):
        """获取所有图层"""
        if self._dynamic_sky:
            return self._dynamic_sky.getLayers()
        return []

    def clear_layers(self):
        """清空动态天空所有图层"""
        if not self._dynamic_sky:
            return
        for layer in list(self._dynamic_sky.getLayers()):
            self._dynamic_sky.removeLayer(layer)

    def get_layer_types(self):
        """获取当前动态天空图层的类型集合（用于判断层级是否一致）"""
        return {type(layer) for layer in self.get_layers()}