from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsDropShadowEffect, QSizePolicy
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen, QBrush
from src.GUI.CustomWidgets.custom_button import CustomButton
from src.GUI.QtComponents.cards import Card, enable_card_shadow
from src.GUI.icons import icon_manager
from src.theme_manager import theme_manager
from src.utils.font_utils import ensure_title_font
from src.Constants.game_constants import GAME_TITLE
from src.Constants.ui_constants import UI_TEXTS, UI_ICONS
import math
class AnimatedGradientLabel(QLabel):
    def __init__(self,text: str,*,font_px: int,font_family: str | None = None,weight: int = 800,color_a_key: str = "COLOR_ACCENT",color_b_key: str = "COLOR_HIGHLIGHT",float_amplitude: float = 5.0,float_speed: float = 0.05, parent: QWidget | None = None,):
        super().__init__(text, parent)
        self._font_px = font_px
        self._font_family = font_family
        self._weight = weight
        self._color_a_key = color_a_key
        self._color_b_key = color_b_key
        self._float_amplitude = float_amplitude  # 上下起伏幅度
        self._float_speed = float_speed          # 上下起伏速度
        self._float_phase = 0.0                  # 上下起伏相位
        self._timer = QTimer(self)   
        self._timer.setInterval(10)
        self._timer.timeout.connect(self._tick)
        self._timer.start()
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.setSizePolicy(self.sizePolicy().horizontalPolicy(), self.sizePolicy().verticalPolicy())
        self.setProperty("role", "animatedTitle")
        theme_manager.add_change_listener(self.apply_theme)
        self.apply_theme()
    def _tick(self):
        self._float_phase += self._float_speed
        self.update()
    def apply_theme(self):
        theme = theme_manager.currentTheme

        family = self._font_family or getattr(theme_manager, "FONT_FAMILY", "微软雅黑")
        f = QFont(family)
        f.setPointSize(int(self._font_px))
        f.setWeight(self._weight)
        self.setFont(f)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setOffset(0, 2)
        c = QColor(getattr(theme, "COLOR_SHADOW", "#000000"))
        c.setAlpha(150)
        shadow.setColor(c)
        self.setGraphicsEffect(shadow)
    def paintEvent(self, event):
        """
        自定义绘制：动态上下起伏 + 简洁双色渐变 + 文字描边 + 抗锯齿
        核心特效：
        1.  基于正弦函数的文字上下浮动
        2.  双色线性渐变（静态，无流动）
        3.  圆角描边增强立体感
        4.  多重抗锯齿优化清晰度
        """
        # 1. 初始化参数 & 渐变颜色获取
        theme = theme_manager.currentTheme
        # 使用主题颜色：accent 和 highlight
        color_a = QColor(getattr(theme, self._color_a_key, "#282f46"))
        color_b = QColor(getattr(theme, self._color_b_key, "#ffffff"))
        # 描边颜色（半透明，更柔和）
        stroke_color = QColor(getattr(theme, "COLOR_SHADOW", "#000000"))
        stroke_color.setAlpha(130)
        widget_height = max(1, self.height())

        # 2. 计算上下起伏偏移量（正弦函数实现平滑浮动）
        # 正弦函数值域[-1,1]，乘以幅度得到实际偏移像素
        float_offset_y = self._float_amplitude * math.sin(self._float_phase)

        # 3. 初始化绘制器，多重抗锯齿
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

            # 4. 创建简洁双色垂直线性渐变（静态，无流动）
            linear_gradient = QLinearGradient(
                0, 0,
                0, widget_height
            )
            # 双色渐变：顶部accent，底部highlight
            linear_gradient.setColorAt(0.0, color_a)
            linear_gradient.setColorAt(1.0, color_b)

            # 5. 绘制文字描边（底层，增强立体感）
            painter.setFont(self.font())
            text_rect = self.rect()
            # 描边画笔：圆角连接，宽度2像素
            stroke_pen = QPen(stroke_color, 2, Qt.PenStyle.SolidLine)
            stroke_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(stroke_pen)
            # 描边文字随起伏偏移，保持与主文字同步
            stroke_rect = text_rect.adjusted(1, 1 + int(float_offset_y), 1, 1 + int(float_offset_y))
            painter.drawText(stroke_rect, int(self.alignment()), self.text())

            # 6. 绘制动态起伏的渐变文字（顶层，核心特效）
            gradient_pen = QPen()
            gradient_pen.setBrush(QBrush(linear_gradient))
            painter.setPen(gradient_pen)
            # 文字绘制标志：精确居中，单行显示
            text_flags = int(self.alignment()) | Qt.TextFlag.TextSingleLine | Qt.TextFlag.TextExpandTabs
            # 主文字偏移：实现上下起伏效果
            main_text_rect = text_rect.adjusted(0, int(float_offset_y), 0, int(float_offset_y))
            painter.drawText(main_text_rect, text_flags, self.text())
        finally:
            painter.end()
class MainMenuHeroComponent(QWidget):
    def __init__(self, *, on_start=None, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        title = AnimatedGradientLabel(
            GAME_TITLE,
            font_px=70,
            weight=900,
            color_a_key="COLOR_ACCENT",
            color_b_key="COLOR_HIGHLIGHT",
            font_family=ensure_title_font(),
        )
        layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addSpacing(12)
class MainMenuActionsComponent(QWidget):
    def __init__(self,*,on_start=None,on_settings=None,on_credits=None,on_exit=None,parent: QWidget | None = None,):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        card = Card()
        card.setMaximumWidth(400)
        card.setObjectName("actions_card")
        enable_card_shadow(card)
        layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignHCenter)

        def mk_btn(text, on_click=None, variant="secondary", icon_name: str | None = None):
            b = CustomButton(text, variant=variant)
            if on_click:
                b.clicked.connect(on_click)
            b.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
            b.setProperty("variant", variant)
            b.setProperty("role", "action")
            b.setAccessibleName(text)
            if icon_name:
                b.setIcon(icon_manager.get_icon(icon_name))
                b.setIconSize(QSize(25, 25))  # 稍微调大图标
            return b
        self._start_btn    = mk_btn(UI_TEXTS["main_menu"]["btn_start_journey"], on_start, variant="primary", icon_name=UI_ICONS["icon_play"])
        self._settings_btn = mk_btn(UI_TEXTS["main_menu"]["btn_settings"],      on_settings, variant="secondary", icon_name=UI_ICONS["icon_settings"])
        self._credits_btn  = mk_btn(UI_TEXTS["main_menu"]["btn_credits"],       on_credits, variant="secondary", icon_name=UI_ICONS["icon_summary"])
        self._exit_btn     = mk_btn(UI_TEXTS["main_menu"]["btn_exit"],          on_exit, variant="secondary", icon_name=UI_ICONS["icon_status"])
        card.body_layout.addWidget(self._start_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        card.body_layout.addWidget(self._settings_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        card.body_layout.addWidget(self._credits_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        card.body_layout.addWidget(self._exit_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        card.body_layout.addSpacing(10)
        footer = QLabel("v0.5.0 | Powered by LZN")
        footer.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        footer.setProperty("role", "footer")
        card.body_layout.addWidget(footer)

    def set_callbacks(self, on_start, on_settings, on_credits, on_exit):
        if on_start:
            self._start_btn.clicked.connect(on_start)
        if on_settings:
            self._settings_btn.clicked.connect(on_settings)
        if on_credits:
            self._credits_btn.clicked.connect(on_credits)
        if on_exit:
            self._exit_btn.clicked.connect(on_exit)
