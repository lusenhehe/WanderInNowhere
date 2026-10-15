from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy
from src.GUI.QtComponents.main_menu_components import MainMenuHeroComponent, MainMenuActionsComponent
from src.GUI.QtComponents.base.base_ui import BaseUI

class MainMenuQt(BaseUI):
    def __init__(self, app_window):
        super().__init__(app_window)

        # 复用共享夜空背景（层级相同则不重建）
        self._background = self.app_window.get_shared_night_sky_background(fps=60)
        self.set_background(self._background)

        self.setObjectName("MainMenuRoot")
        self.setAutoFillBackground(False)

        # 设置UI布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addItem(QSpacerItem(0, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # 居中部分
        center = QVBoxLayout()
        center.setSpacing(16)
        center.addWidget(MainMenuHeroComponent(on_start=self.app_window.show_save_select))
        center.addWidget(MainMenuActionsComponent(
            on_start=self.app_window.show_save_select,
            on_settings=lambda: self.app_window.show_settings(return_screen_class=None),
            on_credits=self.app_window.show_credits,
            on_exit=self.app_window.close,
        ))
        wrap = QHBoxLayout()
        wrap.addLayout(center)
        layout.addLayout(wrap)
        layout.addItem(QSpacerItem(0, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))