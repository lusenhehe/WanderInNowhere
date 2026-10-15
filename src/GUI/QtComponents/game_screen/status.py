from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QGridLayout, QProgressBar
from src.GUI.QtComponents.cards import Card
from src.Constants.game_constants import GAME_SCREEN_STATUS_ITEMS
from src.GUI.QtComponents.debug_utils import debug_enabled

class StatusComponent(QWidget):
    def __init__(self, on_status_clicked=None, *, debug_ctx: object | None = None, parent: QWidget | None = None):
        super().__init__(parent)
        self._on_status_clicked = on_status_clicked
        self._debug_ctx = debug_ctx

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        status_card = Card("当前状态")
        layout.addWidget(status_card)

        self._status_widgets: dict[str, object] = {}
        grid = QGridLayout()
        grid.setColumnStretch(1, 1)
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(6)

        for row, (key, label_text) in enumerate(GAME_SCREEN_STATUS_ITEMS):
            label = QLabel(label_text)
            label.setProperty("role", "statusLabel")
            grid.addWidget(label, row, 0)
            if key in ("hp", "hunger", "magic"):
                bar = QProgressBar()
                bar.setRange(0, 100)
                bar.setTextVisible(False)
                bar.setFixedHeight(14)
                bar.setProperty("barRole", key)

                val = QLabel("--")
                val.setProperty("role", "statusValue")
                val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                val.mousePressEvent = (lambda _ev, k=key: self._handle_status_clicked(k))

                grid.addWidget(bar, row, 1)
                grid.addWidget(val, row, 2)
                self._status_widgets[key] = {"bar": bar, "text": val}
            else:
                val = QLabel("--")
                val.setProperty("role", "statusValue")
                val.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                val.mousePressEvent = (lambda _ev, k=key: self._handle_status_clicked(k))
                grid.addWidget(val, row, 2)
                self._status_widgets[key] = val

        status_card.body_layout.addLayout(grid)

        injury_card = Card("🩹 受伤情况")
        layout.addWidget(injury_card, 1)
        self.injury_view = QTextEdit()
        self.injury_view.setReadOnly(True)
        injury_card.body_layout.addWidget(self.injury_view, 1)
    @staticmethod
    def parse_ratio(value):
        text = str(value).strip()
        if not text:
            return 0, "--"
        if "/" in text:
            parts = text.split("/")
            try:
                cur = float(parts[0])
                total = float(parts[1]) if len(parts) > 1 else 100.0
                total = 100.0 if total <= 0 else total
                percent = max(0.0, min(100.0, (cur / total) * 100.0))
                return int(round(percent)), f"{int(cur)}/{int(total)}"
            except Exception:
                return 0, text
        if text.endswith("%"):
            try:
                num = float(text.rstrip("%"))
                percent = max(0.0, min(100.0, num))
                return int(round(percent)), f"{percent:.0f}%"
            except Exception:
                return 0, text
        try:
            num = float(text)
            percent = max(0.0, min(100.0, num))
            return int(round(percent)), f"{percent:.0f}%"
        except Exception:
            return 0, text
    @staticmethod
    def format_injury_lines(value) -> str:
        if value is None:
            return "无"
        if isinstance(value, (list, tuple)):
            parts = [str(v).strip() for v in value if str(v).strip()]
        else:
            raw = str(value)
            for sep in [",", "，", ";", "；", "\n"]:
                raw = raw.replace(sep, "\n")
            parts = [p.strip() for p in raw.split("\n") if p.strip()]
        return "\n".join(parts) if parts else "无"
    def update_display(self, status: dict):
        status = status or {}
        for key, widget in self._status_widgets.items():
            value = status.get(key, "未知")
            if isinstance(widget, dict):
                percent, display = self.parse_ratio(value)
                widget["bar"].setValue(percent)
                widget["text"].setText(display)
            else:
                widget.setText(str(value))

        self.injury_view.setPlainText(self.format_injury_lines(status.get("injury", "无")))
    def _handle_status_clicked(self, key: str) -> None:
        if callable(self._on_status_clicked):
            self._on_status_clicked(key)
            return

        if not debug_enabled() or self._debug_ctx is None:
            return

        try:
            status = getattr(self._debug_ctx.player_data, "status", {}) or {}
            current_val = str(status.get(key, ""))
        except Exception:
            current_val = ""

        from PyQt6.QtWidgets import QInputDialog

        new_val, ok = QInputDialog.getText(self, "Debug 修改", f"修改 {key} 的值:", text=current_val)
        if not ok:
            return

        try:
            self._debug_ctx.player_data.status[key] = new_val
            self._debug_ctx.update_ui_display()
        except Exception:
            return
