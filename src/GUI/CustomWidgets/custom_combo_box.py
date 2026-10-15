from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QPainterPath, QColor, QFont, QPen, QBrush
from PyQt6.QtWidgets import QComboBox, QWidget
from src.theme_manager import theme_manager
class CustomComboBox(QComboBox):
    def __init__(self, *args, parent: QWidget | None = None, **kwargs):
        super().__init__(*args, parent=parent, **kwargs)
        self.setProperty("ui", "custom-combobox")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._radius = 2
        self._theme = theme_manager.currentTheme
        self.apply_theme()
        theme_manager.add_change_listener(self.apply_theme)
    def paintEvent(self, event):
        painter = QPainter()
        if not painter.begin(self):
            return
            
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = self.rect()
        theme = self._theme
        border_color = QColor(theme.COLOR_BORDER)

        semi_bg = QColor(theme.COLOR_BG_SECONDARY)
        semi_bg.setAlpha(160)

        bg_path = QPainterPath()
        bg_path.addRoundedRect(QRectF(rect), self._radius, self._radius)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(semi_bg))
        painter.drawPath(bg_path)

        painter.setPen(QPen(border_color, 1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(QRectF(rect).adjusted(0.5, 0.5, -0.5, -0.5), self._radius, self._radius)

        if not self.isEditable() or not self.lineEdit():
            painter.setPen(QPen(QColor(theme.COLOR_TEXT_FG)))
            painter.setFont(QFont(theme_manager.FONT_FAMILY, 13))
            text_rect = rect.adjusted(10, 0, -30, 0)
            painter.drawText(
                text_rect,
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                self.currentText() or "",
            )

        arrow_rect = QRectF(rect.right() - 26, rect.center().y() - 5, 10, 10)
        arrow_path = QPainterPath()
        arrow_path.moveTo(arrow_rect.left(), arrow_rect.top())
        arrow_path.lineTo(arrow_rect.right(), arrow_rect.top())
        arrow_path.lineTo(arrow_rect.center().x(), arrow_rect.bottom())
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(border_color))
        painter.drawPath(arrow_path)
        
        painter.end()

    def apply_theme(self):
        self._theme = theme_manager.currentTheme
        self.update()