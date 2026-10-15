from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from src.GUI.CustomWidgets.custom_button import CustomButton

from src.theme_manager import theme_manager


class TopBarComponent(QWidget):
    def __init__(self,*,on_save=None,on_settings=None,parent: QWidget | None = None,):
        super().__init__(parent)
        self._on_save = on_save
        self._on_settings = on_settings
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        self.player_label = QLabel("⚔")
        self.location_label = QLabel("📍")
        self.world_info_label = QLabel("🕐")
        self.player_label.setStyleSheet("font-weight: 700;")
        self.world_info_label.setStyleSheet(f"color: {theme_manager.currentTheme.COLOR_WORLD_INFO};")
        self.location_label.setStyleSheet(f"color: {theme_manager.currentTheme.COLOR_LOCATION};")
        row.addWidget(self.player_label)
        row.addWidget(self.location_label)
        row.addStretch(1)
        row.addWidget(self.world_info_label)
        btn_save = CustomButton("💾 保存", variant="secondary")
        btn_settings = CustomButton("⚙ 设置", variant="secondary")
        btn_save.clicked.connect(self._on_save_clicked)
        btn_settings.clicked.connect(self._on_settings_clicked)
        row.addWidget(btn_save)
        row.addWidget(btn_settings)

    def _on_save_clicked(self):
        if callable(self._on_save):
            self._on_save()

    def _on_settings_clicked(self):
        if callable(self._on_settings):
            self._on_settings()

    def update_display(self, *, player_name: str, location: str, time_text: str, weather: str):
        self.player_label.setText(f"⚔ {player_name}")
        self.location_label.setText(f"📍 {location}")
        self.world_info_label.setText(f"🕐 {time_text} 🌤 {weather}")
