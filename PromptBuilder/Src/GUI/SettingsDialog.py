from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QScrollArea, QWidget, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class SettingsDialog(QDialog):
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setGeometry(400, 300, 400, 300)
        self.config_manager = config_manager
        self.parent = parent

        self.setModal(True)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel("快捷键设置")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Scroll area for shortcuts
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        self.entries = {}

        shortcuts = self.config_manager.config.get("shortcuts", {})

        # Helper function to add row
        def add_row(label, key):
            row_frame = QFrame()
            row_layout = QHBoxLayout(row_frame)

            label_widget = QLabel(label)
            label_widget.setFixedWidth(120)
            row_layout.addWidget(label_widget)

            entry = QLineEdit()
            entry.setText(shortcuts.get(key, ""))
            row_layout.addWidget(entry)

            self.entries[key] = entry
            scroll_layout.addWidget(row_frame)

        add_row("保存 (Save)", "save")
        add_row("另存为 (Save As)", "save_as")
        add_row("撤销 (Undo)", "undo")
        add_row("重做 (Redo)", "redo")
        add_row("退出 (Quit)", "quit")

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        # Buttons
        btn_frame = QFrame()
        btn_layout = QHBoxLayout(btn_frame)

        save_btn = QPushButton("保存设置")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setDefault(True)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addWidget(btn_frame)

    def save_settings(self):
        for key, entry in self.entries.items():
            if "shortcuts" not in self.config_manager.config:
                self.config_manager.config["shortcuts"] = {}
            self.config_manager.config["shortcuts"][key] = entry.text()

        self.config_manager.save_config()
        QMessageBox.information(self, "提示", "设置已保存，部分快捷键可能需要重启应用生效。")
        self.accept()
