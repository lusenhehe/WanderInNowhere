import json

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit

from src.GUI.QtComponents.cards import Card


class DetailComponent(QWidget):
    def __init__(self, *, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        card = Card("详细信息")
        layout.addWidget(card, 1)

        self.view = QTextEdit()
        self.view.setReadOnly(True)
        self.view.setPlainText("选择内容查看详细信息…")
        card.body_layout.addWidget(self.view, 1)

    def set_text(self, text: str):
        self.view.setPlainText(text or "")

    def set_json(self, obj):
        try:
            self.set_text(json.dumps(obj, ensure_ascii=False, indent=2))
        except Exception:
            self.set_text(str(obj))
