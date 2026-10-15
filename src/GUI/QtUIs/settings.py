import os
from src.paths import assets_path
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import  QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QStackedWidget, QLineEdit, QSlider, QSpinBox, QCheckBox, QMessageBox, QInputDialog
from src.GUI.QtComponents.cards import Card
from src.Constants.config import load_app_config, load_config, save_app_config, DEFAULT_MODELS
from src.config_model                  import AppConfig
from src.theme_manager                 import theme_manager
from src.GUI.CustomWidgets             import CustomButton, CustomComboBox
from src.GUI.QtComponents.base.base_ui import BaseUI
from src.Constants.ui_constants import UI_TEXTS

class SettingsQt(BaseUI):
    def __init__(self, app_window, *, return_action=None):
        super().__init__(app_window)
        self._return_action = return_action
        # 复用共享夜空背景（层级相同则不重建）
        self._background = self.app_window.get_shared_night_sky_background(fps=60)
        self.set_background(self._background)
        self.setObjectName("SettingsRoot")
        self.setAutoFillBackground(False)
        self._cfg = load_app_config().to_dict()
        self._initializing = True
        self._setup_ui()
        self._load_from_config(self._cfg)
        self._initializing = False
    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)
        # 头部标题
        header = QLabel(UI_TEXTS["settings"]["title"])
        header.setObjectName("SettingsHeader")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(header)
        body = QHBoxLayout()
        root.addLayout(body, 1)
        # 侧边栏 + 页面区域
        self.sidebar = self._setup_ui_sidebar()
        self.pages = self._setup_ui_pages()

        body.addWidget(self.sidebar)
        body.addWidget(self.pages)

        self.sidebar.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.sidebar.setCurrentRow(0)

        root.addLayout(self._setup_ui_btn_row())
        # 应用主题
        self._apply_theme()
    def _setup_ui_pages(self) -> QStackedWidget:
        pages = QStackedWidget()

        self.page_appearance = self._build_appearance_page()
        self.page_ai = self._build_ai_page()
        self.page_debug = self._build_debug_page()

        pages.addWidget(self.page_appearance)
        pages.addWidget(self.page_ai)
        pages.addWidget(self.page_debug)
        return pages
    def _setup_ui_sidebar(self) -> QListWidget:
        sidebar = QListWidget()
        sidebar.setFixedWidth(200)
        sidebar.addItem(UI_TEXTS["settings"]["sidebar_appearance"])
        sidebar.addItem(UI_TEXTS["settings"]["sidebar_ai"])
        sidebar.addItem(UI_TEXTS["settings"]["sidebar_debug"])
        return sidebar
    def _setup_ui_btn_row(self) -> QHBoxLayout:
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        self.btn_apply     = CustomButton(UI_TEXTS["settings"]["btn_apply"], variant="primary")
        self.btn_save_back = CustomButton(UI_TEXTS["settings"]["btn_save_back"], variant="primary")
        self.btn_cancel    = CustomButton(UI_TEXTS["settings"]["btn_cancel"], variant="secondary")

        self.btn_apply.clicked.connect(self.apply_settings)
        self.btn_save_back.clicked.connect(self.save_and_back)
        self.btn_cancel.clicked.connect(self.go_back)

        btn_row.addWidget(self.btn_apply)
        btn_row.addWidget(self.btn_save_back)
        btn_row.addWidget(self.btn_cancel)
        return btn_row
    def _build_appearance_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        theme_card = Card(UI_TEXTS["settings"]["theme_card_title"])
        layout.addWidget(theme_card)
        theme_row = QHBoxLayout()
        theme_row.addWidget(QLabel(UI_TEXTS["settings"]["theme_label"]))
        self.combo_theme = CustomComboBox()
        self.combo_theme.addItems(self._scan_theme_candidates())
        theme_row.addWidget(self.combo_theme, 1)
        theme_card.body_layout.addLayout(theme_row)
        font_card = Card(UI_TEXTS["settings"]["font_card_title"])
        layout.addWidget(font_card)
        font_row = QHBoxLayout()
        font_row.addWidget(QLabel(UI_TEXTS["settings"]["font_label"]))
        self.combo_font = CustomComboBox()
        self.combo_font.addItems(self._scan_font_candidates())
        font_row.addWidget(self.combo_font, 1)
        font_card.body_layout.addLayout(font_row)
        layout.addStretch(1)
        return page
    def _scan_theme_candidates(self) -> list[str]:
        theme_dir = assets_path("themes")
        items: list[str] = []
        try:
            for name in os.listdir(theme_dir):
                if not name.lower().endswith(".json"):
                    continue
                items.append(os.path.splitext(name)[0])
        except Exception:
            items = []

        items = sorted(set(items))
        return items or ["darkly"]
    def _scan_font_candidates(self) -> list[str]:
        values = ["微软雅黑", "SimHei", "Arial"]
        font_dir = assets_path("fonts")
        if os.path.exists(font_dir):
            for name in os.listdir(font_dir):
                if name.lower().endswith((".ttf", ".ttc", ".otf")):
                    values.append(name)
        # de-dupe
        seen = set()
        out = []
        for v in values:
            if v not in seen:
                out.append(v)
                seen.add(v)
        return out
    def _build_ai_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        api_card = Card(UI_TEXTS["settings"]["api_card_title"])
        layout.addWidget(api_card)
        api_card.body_layout.addWidget(QLabel(UI_TEXTS["settings"]["api_url_label"]))
        self.edit_api_url = QLineEdit()
        api_card.body_layout.addWidget(self.edit_api_url)
        api_card.body_layout.addWidget(QLabel(UI_TEXTS["settings"]["api_key_label"]))
        self.edit_api_key = QLineEdit()
        self.edit_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        api_card.body_layout.addWidget(self.edit_api_key)
        model_card = Card(UI_TEXTS["settings"]["model_card_title"])
        layout.addWidget(model_card)
        model_row = QHBoxLayout()
        model_row.addWidget(QLabel(UI_TEXTS["settings"]["model_label"]))
        self.combo_model = CustomComboBox()
        self.combo_model.addItems(DEFAULT_MODELS)
        model_row.addWidget(self.combo_model, 1)
        model_card.body_layout.addLayout(model_row)
        params_card = Card(UI_TEXTS["settings"]["params_card_title"])
        layout.addWidget(params_card)
        temp_row = QHBoxLayout()
        temp_row.addWidget(QLabel(UI_TEXTS["settings"]["temperature_label"]))
        self.slider_temp = QSlider(Qt.Orientation.Horizontal)
        self.slider_temp.setRange(0, 200)
        self.label_temp = QLabel("0.70")
        self.slider_temp.valueChanged.connect(self._on_temp_changed)
        temp_row.addWidget(self.slider_temp, 1)
        temp_row.addWidget(self.label_temp)
        params_card.body_layout.addLayout(temp_row)
        limits_row = QHBoxLayout()
        limits_row.addWidget(QLabel(UI_TEXTS["settings"]["max_tokens_label"]))
        self.spin_max_tokens = QSpinBox()
        self.spin_max_tokens.setRange(1, 4096)
        limits_row.addWidget(self.spin_max_tokens)
        limits_row.addSpacing(16)
        limits_row.addWidget(QLabel(UI_TEXTS["settings"]["max_history_label"]))
        self.spin_max_history = QSpinBox()
        self.spin_max_history.setRange(1, 200)
        limits_row.addWidget(self.spin_max_history)

        params_card.body_layout.addLayout(limits_row)
        layout.addStretch(1)

        self._ai_widgets = [self.edit_api_url,self.edit_api_key,self.combo_model,self.slider_temp,self.spin_max_tokens,self.spin_max_history,]
        return page
    def _build_debug_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        debug_card = Card(UI_TEXTS["settings"]["debug_card_title"])
        self.chk_debug = QCheckBox(UI_TEXTS["settings"]["debug_checkbox"])
        self.chk_debug.stateChanged.connect(self._on_debug_toggled)
        layout.addWidget(debug_card)
        debug_card.body_layout.addWidget(self.chk_debug)
        info = QLabel(UI_TEXTS["settings"]["debug_info"])
        info.setWordWrap(True)
        info.setProperty("role", "secondary")
        debug_card.body_layout.addWidget(info)
        layout.addStretch(1)
        return page
    def _on_temp_changed(self, value: int):
        temp = value / 100.0
        self.label_temp.setText(f"{temp:.2f}")
    def _on_debug_toggled(self, _state: int):
        if self._initializing:
            self._sync_ai_enabled()
            return
        enabling = self.chk_debug.isChecked()
        if enabling:
            cfg = load_config()
            correct_pwd = os.getenv("DEBUG_PASSWORD", cfg.get("debug_password", "123456"))
            pwd, ok = QInputDialog.getText(self, UI_TEXTS["settings"]["debug_verification"], UI_TEXTS["settings"]["enter_debug_password"], QLineEdit.EchoMode.Password)
            if (not ok) or (pwd != str(correct_pwd)):
                QMessageBox.critical(self, UI_TEXTS["settings"]["error"], UI_TEXTS["settings"]["password_incorrect"])
                self.chk_debug.setChecked(False)
                return
        self._sync_ai_enabled()
    def _sync_ai_enabled(self):
        enabled = self.chk_debug.isChecked()
        for w in getattr(self, "_ai_widgets", []):
            w.setEnabled(enabled)
    def _load_from_config(self, cfg: dict):
        self.chk_debug.setChecked(bool(cfg.get("debug", False)))

        theme = cfg.get("theme", "darkly")
        idx = self.combo_theme.findText(theme)
        if idx >= 0:
            self.combo_theme.setCurrentIndex(idx)

        font = cfg.get("font", "微软雅黑")
        self.combo_font.setCurrentText(str(font))

        self.edit_api_url.setText(str(cfg.get("api_url", "")))
        self.edit_api_key.setText(str(cfg.get("api_key", "")))
        self.combo_model.setCurrentText(str(cfg.get("model", "")))

        temp = float(cfg.get("temperature", 0.7) or 0.7)
        self.slider_temp.setValue(int(round(temp * 100)))
        self._on_temp_changed(self.slider_temp.value())

        self.spin_max_tokens.setValue(int(cfg.get("max_tokens", 256) or 256))
        self.spin_max_history.setValue(int(cfg.get("max_history", 20) or 20))

        self._sync_ai_enabled()
    def _collect_config(self) -> dict:
        cfg = load_app_config()
        cfg.debug = bool(self.chk_debug.isChecked())
        cfg.theme = str(self.combo_theme.currentText()).strip() or "darkly"
        cfg.font = str(self.combo_font.currentText()).strip() or "微软雅黑"
        cfg.api_url = str(self.edit_api_url.text()).strip()
        cfg.api_key = str(self.edit_api_key.text()).strip()
        cfg.model = str(self.combo_model.currentText()).strip()
        cfg.temperature = float(self.slider_temp.value() / 100.0)
        cfg.max_tokens = int(self.spin_max_tokens.value())
        cfg.max_history = int(self.spin_max_history.value())

        return cfg.to_dict()
    def _save_settings(self) -> bool:
        cfg = self._collect_config()
        new_theme = cfg.get("theme", "darkly")
        if new_theme != theme_manager.current_theme_name:
            theme_manager.set_theme(new_theme)

        save_app_config(AppConfig.from_dict(cfg))

        if hasattr(self.app_window, "apply_global_font"):
            self.app_window.apply_global_font()

        return True
    def apply_settings(self):
        if self._save_settings():
            # rebuild to apply theme cleanly
            self.app_window.show_settings(return_screen_class=None)
    def save_and_back(self):
        if self._save_settings():
            self.go_back()
    def go_back(self):
        if callable(self._return_action):
            self._return_action()
        else:
            self.app_window.show_main_menu()