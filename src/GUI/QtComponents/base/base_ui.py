from typing import Iterable
import os
from string import Template

from src.paths import assets_path
from PyQt6.QtCore import Qt,QTimer,QEasingCurve,QPropertyAnimation,QSequentialAnimationGroup,QParallelAnimationGroup,QPauseAnimation,pyqtProperty,QPoint
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QWidget
from src.theme_manager import theme_manager
from src.utils.logger import logger


_QSS_CACHE: dict[str, tuple[float, str]] = {}


def _read_text_cached(path: str) -> str:
    try:
        mtime = os.path.getmtime(path)
        cached = _QSS_CACHE.get(path)
        if cached and cached[0] == mtime:
            return cached[1]
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read()
        _QSS_CACHE[path] = (mtime, text)
        return text
    except Exception:
        return ""

class SlideFadeEffect(QGraphicsOpacityEffect):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._offset = 0.0

    @pyqtProperty(float)
    def offset(self) -> float:
        return self._offset

    @offset.setter
    def offset(self, value: float):
        if self._offset == value:
            return
        self._offset = value
        self.update()

    def draw(self, painter):
        # 关键：先判断Painter是否处于激活状态，未激活则直接返回
        if not painter.isActive():
            super().draw(painter)
            return
        
        try:  # 增加异常捕获，避免绘制异常扩散
            painter.save()  # 保存Painter状态
            painter.translate(0, -self._offset)  # 坐标变换
            super().draw(painter)  # 调用父类绘制逻辑
        finally:  # 无论是否异常，都要恢复Painter状态，避免状态混乱
            painter.restore()


class BaseUI(QWidget):
    """所有UI组件的基类，提供共同的功能"""

    def __init__(self, app_window, *, parent=None):
        super().__init__(parent)
        self.app_window = app_window

        # 设置为透明背景，让自定义背景可见
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # 背景相关
        self._background = None
        self._background_enabled = True

        # 入口动画相关
        self._entry_widget_overrides: list[QWidget] = []
        self._entry_animation_group: QSequentialAnimationGroup | None = None
        self._is_entry_animating = False

        # 主题管理
        self._theme_update_timer = QTimer(self)
        self._theme_update_timer.setSingleShot(True)
        self._theme_update_timer.setInterval(1000 // 120)  # 防抖
        self._theme_update_timer.timeout.connect(self._apply_theme)

        # 注册主题变化监听
        theme_manager.add_change_listener(self._on_theme_changed)
        # 防止页面反复创建/销毁导致监听器积累
        self.destroyed.connect(lambda *_: theme_manager.remove_change_listener(self._on_theme_changed))

        # 延迟初始化主题，让子类有机会设置背景
        QTimer.singleShot(0, self._apply_theme)

    def set_background_enabled(self, enabled: bool):
        """启用或禁用背景渲染"""
        self._background_enabled = enabled
        self.update()

    def set_background(self, background):
        """设置背景组件"""
        if self._background and hasattr(self._background, 'updated') and self._background.updated:
            try:
                self._background.updated.disconnect(self.update)
            except (TypeError, RuntimeError):
                # 信号可能没有连接，忽略错误
                pass
        self._background = background
        if background and hasattr(background, 'updated') and background.updated:
            background.updated.connect(self.update)
        self.update()  # 强制更新以显示背景

    def _on_theme_changed(self):
        """主题变化时的处理"""
        self._theme_update_timer.start()

    def _apply_theme(self):
        """应用主题样式"""
        # 默认透明背景，让自定义背景可见
        self.setStyleSheet("background-color: transparent;")
        # 每个BaseUI子类一个qss（全局 base.qss 建议由 QApplication 统一应用）
        qss_parts: list[str] = []
        per_qss_path = assets_path('themes', 'QssStyle', f'{self.__class__.__name__}.qss')
        if os.path.exists(per_qss_path):
            qss_parts.append(_read_text_cached(per_qss_path))

        if not qss_parts:
            return

        qss_template = "\n\n".join(qss_parts)
        vars = theme_manager.get_qss_vars(scope=self.__class__.__name__)
        try:
            qss = Template(qss_template).safe_substitute(vars)
            self.setStyleSheet(qss)
        except Exception:
            logger.exception(f"应用主题{self.__class__.__name__}样式失败")
            self.setStyleSheet("background-color: transparent;")

    def register_entry_widgets(self, widgets: Iterable[QWidget]):
        """Register multiple widgets to participate in the entry animation."""
        for widget in widgets:
            self.register_entry_widget(widget)

    def _resolve_entry_targets(self) -> list[QWidget]:
        if self._entry_widget_overrides:
            return [w for w in self._entry_widget_overrides if isinstance(w, QWidget) and w.isVisible()]

        return [
            widget
            for widget in self.findChildren(QWidget, "", Qt.FindChildOption.FindDirectChildrenOnly)
            if widget is not self._background and widget.isVisible()
        ]

    def play_entry_animation(self):
        if self._is_entry_animating or not self.isVisible():
            return

        targets = self._resolve_entry_targets()
        if not targets:
            return

        self._is_entry_animating = True
        animation_group = QSequentialAnimationGroup(self)

        for index, widget in enumerate(targets):
            slide_effect = SlideFadeEffect(widget)
            slide_effect.setOpacity(0.0)
            slide_effect.offset = 24.0
            widget.setGraphicsEffect(slide_effect)

            parallel = QParallelAnimationGroup(self)

            opacity_anim = QPropertyAnimation(slide_effect, b"opacity", self)
            opacity_anim.setStartValue(0.0)
            opacity_anim.setEndValue(1.0)
            opacity_anim.setDuration(100)
            opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

            offset_anim = QPropertyAnimation(slide_effect, b"offset", self)
            offset_anim.setStartValue(24.0)
            offset_anim.setEndValue(0.0)
            offset_anim.setDuration(100)
            offset_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

            parallel.addAnimation(opacity_anim)
            parallel.addAnimation(offset_anim)

            def _cleanup(w: QWidget, eff, target: QPoint):
                if w is None or eff is None:
                    return
                try:
                    # 移除w.move(target)：控件原始位置未改变，该操作无意义且可能导致位置错乱
                    # w.move(target) 
                    w.setGraphicsEffect(None)  # 解除特效绑定
                    eff.deleteLater()
                except (RuntimeError, AttributeError) as e:
                    return

            # 【需要修改2】修正lambda绑定：使用默认参数强制捕获当前循环的widget、slide_effect、原始位置
            # 提前保存原始位置，避免lambda调用时widget.pos()已变化
            original_pos = widget.pos()
            parallel.finished.connect(
                lambda w=widget, eff=slide_effect, target=original_pos: _cleanup(w, eff, target)
            )
            if index > 0:
                animation_group.addAnimation(QPauseAnimation(45))
            animation_group.addAnimation(parallel)

        def _on_finished():
            self._is_entry_animating = False
            self._entry_animation_group = None

        animation_group.finished.connect(_on_finished)
        self._entry_animation_group = animation_group
        animation_group.start()

    def showEvent(self, event):
        super().showEvent(event)
        self.play_entry_animation()

    def paintEvent(self, event):
        """统一的绘制事件处理"""
        if self._background_enabled and self._background:
            painter = QPainter(self)
            try:
                painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
                painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
                rect = self.rect()
                self._background.paint(painter, rect)
            finally:
                painter.end()

        # 调用子类的绘制
        super().paintEvent(event)

    def resizeEvent(self, event):
        """统一的尺寸变化处理"""
        super().resizeEvent(event)
        if self._background and hasattr(self._background, 'request'):
            self._background.request(self.size())

    def closeEvent(self, event):
        """清理资源"""
        theme_manager.remove_change_listener(self._on_theme_changed)
        if hasattr(self._background, 'updated') and self._background:
            try:
                self._background.updated.disconnect(self.update)
            except:
                pass  # 可能已经断开连接
        super().closeEvent(event)