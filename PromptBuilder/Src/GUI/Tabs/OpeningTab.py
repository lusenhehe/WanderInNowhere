from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt6.QtGui import QFont

class OpeningTab(QWidget):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        layout.addWidget(QLabel("开场白模板 (Opening Prompt Template)"))

        self.opening_text = QTextEdit()
        self.opening_text.setFont(QFont("Consolas", 10))
        self.opening_text.textChanged.connect(self._on_text_modified)
        layout.addWidget(self.opening_text)

    def refresh(self):
        content = self.data_manager.data.get("opening_prompt_template", "")
        self.opening_text.setPlainText(content)

    def _on_text_modified(self):
        content = self.opening_text.toPlainText().strip()
        self.data_manager.update_opening(content)
