from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from src.Constants.ui_constants import CREDITS_DATA, UI_TEXTS
from src.GUI.CustomWidgets.custom_button import CustomButton
from src.GUI.QtComponents.base.base_ui import BaseUI
class CreditsQt(BaseUI):
    def __init__(self, app_window):
        super().__init__(app_window)
        # 复用共享夜空背景（层级相同则不重建）
        self._background = self.app_window.get_shared_night_sky_background(fps=60)
        self.set_background(self._background)
        self.scroll_speed = 1  # 每帧像素数
        self._setup_ui()
    def _setup_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # 顶部标题
        title = QLabel(UI_TEXTS["credits"]["credits_title"])
        title.setObjectName("CreditsTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

        subtitle = QLabel(UI_TEXTS["credits"]["subtitle"])
        subtitle.setObjectName("CreditsSubtitle")
        subtitle.setProperty("role", "secondary")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(subtitle)

        # 滚动区域用于制作人员名单
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("CreditsScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        root.addWidget(self.scroll_area, 1)

        # 内部控件用于制作人员名单内容
        self.inner_widget = QWidget()
        self.inner_layout = QVBoxLayout(self.inner_widget)
        self.inner_layout.setContentsMargins(20, 20, 20, 20)
        self.inner_layout.setSpacing(20)
        self.inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 构建制作人员名单部分
        self._build_credits_sections()

        self.scroll_area.setWidget(self.inner_widget)

        # 开始自动滚动
        self._start_auto_scroll()

        btn = CustomButton(UI_TEXTS["credits"]["btn_back_to_menu"], variant="secondary")
        btn.clicked.connect(self.app_window.show_main_menu)
        root.addWidget(btn)

        self._apply_theme()

    def _build_credits_sections(self):
        sections = {
            UI_TEXTS["credits"]["development_team"]: []
        }
        for role, names in CREDITS_DATA:
            sections[UI_TEXTS["credits"]["development_team"]].append((role, names))
        for section_title, credits_list in sections.items():
            if not credits_list:
                continue
            # 部分标题
            header = QLabel(section_title)
            header.setObjectName("CreditsSectionHeader")
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.inner_layout.addWidget(header)
            # 此部分中的制作人员名单
            for role, names in credits_list:
                role_label = QLabel(f"{role}: {names}")
                role_label.setObjectName("CreditsRoleLine")
                role_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.inner_layout.addWidget(role_label)

    def _start_auto_scroll(self):
        self.scroll_timer = QTimer(self)
        self.scroll_timer.timeout.connect(self._scroll_credits)
        self.scroll_timer.start(50)  # 每50ms更新一次

    def _scroll_credits(self):
        scrollbar = self.scroll_area.verticalScrollBar()
        current_value = scrollbar.value()
        max_value = scrollbar.maximum()

        if current_value < max_value:
            scrollbar.setValue(current_value + self.scroll_speed)
        else:
            # 到达末尾时重置到顶部
            scrollbar.setValue(0)