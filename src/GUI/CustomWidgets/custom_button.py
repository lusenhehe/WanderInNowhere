from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QEvent, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor

class CustomButton(QPushButton):
    """A small, reusable button with animated hover/press and focus styling.

    Features:
    - property-based background animation (hover/press)
    - support for 'variant' property (primary/secondary)
    - accessible focus ring
    - easy to style via QSS using QPushButton[variant="primary"]
    """
    def __init__(self, *args, variant="secondary", **kwargs):
        super().__init__(*args, **kwargs)
        self.setProperty('variant', variant)
        self._bg_value = 0.0  # used for animation smoothing if needed
        self._anim = QPropertyAnimation(self, b"bgValue")
        self._anim.setDuration(180)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.setMouseTracking(True)
        # Accessibility
        self.setFocusPolicy(self.focusPolicy())
        self.setAccessibleName(self.text())
        # Improve keyboard appearance
        self.setCursor(self.cursor())
        # Track icon presence so QSS can add spacing
        self.setProperty('hasIcon', False)

    def setIcon(self, icon):
        # override to mark the presence of icon for styling
        super().setIcon(icon)
        try:
            self.setProperty('hasIcon', True)
            self.style().unpolish(self)
            self.style().polish(self)
        except Exception:
            pass
    def enterEvent(self, event):
        super().enterEvent(event)
        self.setProperty('hovered', True)
        self._animate_to(1.0)
        # add subtle shadow on hover; use accent glow for main CTA
        try:
            from PyQt6.QtWidgets import QGraphicsDropShadowEffect
            eff = QGraphicsDropShadowEffect(self)
            eff.setBlurRadius(12)
            eff.setOffset(0, 4)
            if self.objectName() == 'MainCTA':
                # accent colored glow for primary CTA
                try:
                    from src.theme_manager import theme_manager
                    col = theme_manager.currentTheme.COLOR_ACCENT
                    c = QColor(col)
                except Exception:
                    c = QColor(40, 160, 255)
                c.setAlpha(120)
                eff.setColor(c)
            else:
                color = QColor(0, 0, 0, 70)
                eff.setColor(color)
            self.setGraphicsEffect(eff)
            self._hover_shadow = eff
        except Exception:
            self._hover_shadow = None

    def leaveEvent(self, event):
        super().leaveEvent(event)
        self.setProperty('hovered', False)
        self._animate_to(0.0)
        try:
            if hasattr(self, '_hover_shadow') and self._hover_shadow is not None:
                self._hover_shadow.setEnabled(False)
                self.setGraphicsEffect(None)
                self._hover_shadow = None
        except Exception:
            pass

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        # quick press feedback: go to pressed state briefly
        self.setProperty('pressed', True)
        self.style().unpolish(self)
        self.style().polish(self)
        self._anim.stop()
        self._animate_to(0.5)
        # slightly reduce shadow on press
        try:
            eff = getattr(self, '_hover_shadow', None)
            if eff is not None:
                eff.setBlurRadius(4)
                eff.setOffset(0, 1)
        except Exception:
            pass

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.setProperty('pressed', False)
        self.style().unpolish(self)
        self.style().polish(self)
        self._animate_to(1.0)
        # restore shadow
        try:
            eff = getattr(self, '_hover_shadow', None)
            if eff is not None:
                eff.setBlurRadius(12)
                eff.setOffset(0, 4)
        except Exception:
            pass

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self._animate_to(1.0)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self._animate_to(0.0)

    def _animate_to(self, value: float):
        self._anim.stop()
        self._anim.setStartValue(self._bg_value)
        self._anim.setEndValue(value)
        self._anim.start()

    def getBgValue(self):
        return self._bg_value

    def setBgValue(self, v):
        self._bg_value = v
        hovered = (v > 0.5)
        self.setProperty('hovered', hovered)
        if not hovered:
            self.setProperty('pressed', False)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    bgValue = pyqtProperty(float, fget=getBgValue, fset=setBgValue)
