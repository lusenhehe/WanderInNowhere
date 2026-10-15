import os
from typing import Optional
from string import Template
from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, QSize
from PyQt6.QtGui import QFont, QFontDatabase, QIcon
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QWidget, QApplication
from src.Constants.config import ICON_PATH, load_config
from src.theme_manager import theme_manager
from src.paths import assets_path
from src.GUI.QtUIs.main_menu    import MainMenuQt
from src.GUI.QtUIs.save_select  import SaveSelectQt
from src.GUI.QtUIs.create_world import CreateWorldQt
from src.GUI.QtUIs.game_screen  import GameScreenQt
from src.GUI.QtUIs.settings     import SettingsQt
from src.GUI.QtUIs.credits      import CreditsQt
from src.utils.logger           import logger
class GameAppQt(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("乌有乡游记")
        self.resize(1024, 768)

        icon_path = ICON_PATH
        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        # 核心堆栈
        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)
        # 当前和待切换的 widget
        self._current_widget: Optional[QWidget] = None
        self._pending_widget: Optional[QWidget] = None
        self._cached_background = None
        self._shared_backgrounds: dict[str, object] = {}
        self.apply_global_font()
        self.apply_global_qss()
        theme_manager.add_change_listener(self.apply_global_qss)
        self.show_main_menu()
    def get_shared_night_sky_background(self, *, fps: int = 60):
        """获取（或创建）共享的夜空背景。
        关键点：
        - 背景对象挂在 GameAppQt 上，切换页面时不会被 old_widget.deleteLater() 带走。
        - 当图层“层级集合”一致时，直接复用，不重复创建/重复 add_layer。
        """

        from src.GUI.QtComponents.background.background import BackGround
        from src.GUI.QtComponents.SkyLayers import (
            MeteorLayer,
            FogLayer,
            MoonLayer,
            StarsLayer,
            NightSkyBackground,
        )
        key = f"night_sky::fps={fps}"
        bg = self._shared_backgrounds.get(key)
        if not isinstance(bg, BackGround):
            bg = BackGround(parent=self)
            self._shared_backgrounds[key] = bg
        bg.set_dynamic_sky(fps=fps)
        expected_types = {
            NightSkyBackground,
            MeteorLayer,
            FogLayer,
            MoonLayer,
            StarsLayer,
        }
        if getattr(bg, "get_layer_types", None) is None or bg.get_layer_types() != expected_types:
            # 层级不一致：重配
            if getattr(bg, "clear_layers", None) is not None:
                bg.clear_layers()
            w, h = self.width(), self.height()
            bg.add_layer(NightSkyBackground())
            bg.add_layer(MeteorLayer())
            bg.add_layer(FogLayer())
            bg.add_layer(MoonLayer(dx=w * 0.8, dy=h * 0.2))
            bg.add_layer(StarsLayer())
        # 确保尺寸同步（避免首次绘制前 size 还停留在默认值）
        try:
            bg.request_size(QSize(self.width(), self.height()))
        except Exception:
            pass
        return bg
    def apply_global_qss(self) -> None:
        """
        apply_global_qss : 应用全局QSS样式表
        :param self: GameAppQt实例
        """
        base_qss_path = assets_path('themes', 'QssStyle', 'base.qss')
        if not os.path.exists(base_qss_path):
            return
        qapp = self._get_qapp()
        if qapp is None:
            return
        try:
            with open(base_qss_path, 'r', encoding='utf-8') as f:
                template = f.read()
            vars = theme_manager.get_qss_vars(scope=None)
            qss = Template(template).safe_substitute(vars)
            qapp.setStyleSheet(qss)
        except Exception:
            logger.error("应用全局QSS失败", exc_info=True)
    def closeEvent(self, event):
        theme_manager.remove_change_listener(self.apply_global_qss)
        super().closeEvent(event)
    def _get_qapp(self) -> Optional['QApplication']:
        return QApplication.instance()
    def apply_global_font(self) -> None:
        cfg = load_config()
        font_name = cfg.get('font', '微软雅黑')
        font_path = assets_path('fonts', font_name)
        family_name = font_name
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id != -1:
                families = QFontDatabase.applicationFontFamilies(font_id)
                if families:
                    family_name = families[0]
        app = self._get_qapp()
        if app is not None:
            app.setFont(QFont(family_name, 12))
        theme_manager.set_font_family(family_name)
    def switch_widget(self, widget: QWidget) -> None:
        if self._current_widget is widget:
            return
        self._pending_widget = widget
        if self._current_widget is None:
            self._attach_widget(self._pending_widget)
            return
        old_widget = self._current_widget
        new_widget = self._pending_widget
        self._pending_widget = None
        self._current_widget = new_widget
        # 先淡出再淡入
        old_widget.setWindowOpacity(1.0)
        new_widget.setWindowOpacity(0.0)
        self._stack.addWidget(new_widget)
        self._stack.setCurrentWidget(new_widget)
        fade_out = QPropertyAnimation(old_widget, b"windowOpacity", self)
        fade_out.setDuration(220)
        fade_out.setStartValue(1.0)
        fade_out.setEndValue(0.0)
        fade_out.setEasingCurve(QEasingCurve.Type.InOutQuad)

        fade_in = QPropertyAnimation(new_widget, b"windowOpacity", self)
        fade_in.setDuration(240)
        fade_in.setStartValue(0.0)
        fade_in.setEndValue(1.0)
        fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        def on_fade_out_finished():
            try:
                if self._stack.indexOf(old_widget) != -1:
                    self._stack.removeWidget(old_widget)
                old_widget.deleteLater()
            except RuntimeError as re:
                logger.error(f" 旧Widget删除失败: {re}", exc_info=True)
                pass
            if hasattr(old_widget, '_fade_animation'):
                del old_widget._fade_animation
            # 淡出完成后启动淡入
            fade_in.start()
            new_widget._fade_animation = fade_in
        def on_fade_in_finished():
            if hasattr(new_widget, '_fade_animation'):
                del new_widget._fade_animation
        fade_out.finished.connect(on_fade_out_finished)
        fade_in.finished.connect(on_fade_in_finished)
        fade_out.start()
        old_widget._fade_animation = fade_out
    def _attach_widget(self, widget: QWidget):
        if widget is None:
            return
        # 如果有缓存的背景，给widget使用
        if self._cached_background and hasattr(widget, 'set_background'):
            widget.set_background(self._cached_background)
            self._cached_background = None
        self._pending_widget = None
        self._current_widget = widget
        widget.setWindowOpacity(1.0)  # 直接设置为可见
        self._stack.addWidget(widget)
        self._stack.setCurrentWidget(widget)
    def show_main_menu(self) -> None:
        self.switch_widget(MainMenuQt(self))
    def show_save_select(self) -> None:
        self.switch_widget(SaveSelectQt(self))
    def show_create_world(self) -> None:
        self.switch_widget(CreateWorldQt(self))
    def show_game_screen(self, filename: str, save_data: dict) -> None:
        import time
        from src.utils.logger import logger
        t0 = time.perf_counter()
        widget = GameScreenQt(self, filename=filename, save_data=save_data)
        t1 = time.perf_counter()
        logger.info(f"GameScreen constructor took {t1 - t0:.3f}s")
        self.switch_widget(widget)
    def show_settings(self, return_screen_class=None, **return_screen_kwargs) -> None:
        return_action = self.show_main_menu
        self.switch_widget(SettingsQt(self, return_action=return_action))
    def show_credits(self) -> None:
        self.switch_widget(CreditsQt(self))
