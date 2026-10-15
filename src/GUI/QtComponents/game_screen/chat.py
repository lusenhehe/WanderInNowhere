from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QScrollArea, QFrame, QLabel, QSizePolicy
)

from src.GUI.QtComponents.cards import Card, enable_card_shadow
from src.GUI.CustomWidgets.custom_button import CustomButton
from src.AI.parser import strip_state_block


class ChatBubble(QFrame):
    def __init__(self, text: str, role: str, parent: QWidget | None = None):
        super().__init__(parent)
        self.role = role
        self.setObjectName("ChatBubble")
        self.setProperty('role', role)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4,4,4,4)
        self.label = QLabel(text)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        self.label.setMaximumHeight(self.maximumHeight()) 
        layout.addWidget(self.label)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)
        # Ensure proper sizing
        self.label.adjustSize()
        self.adjustSize()
    def set_text(self, text: str):
        self.label.setText(text)
        self.label.adjustSize()
        self.adjustSize()
        self.updateGeometry()

    def append_text(self, text: str):
        self.label.setText(self.label.text() + text)
        self.label.adjustSize()
        self.adjustSize()
        self.updateGeometry()


class ChatComponent(QWidget):
    def __init__(self, on_send, *, parent: QWidget | None = None):
        super().__init__(parent)
        self._on_send = on_send
        self.last_assistant_bubble = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        card = Card()
        layout.addWidget(card, 1)

        # Use ScrollArea for chat
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")
        
        self.container = QWidget()
        self.chat_layout = QVBoxLayout(self.container)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setSpacing(12)
        self.chat_layout.setContentsMargins(5,5,5,5)
        
        self.scroll_area.setWidget(self.container)
        card.body_layout.addWidget(self.scroll_area, 1)
        #添加输入行
        input_row = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("输入你的行动...")
        self.chat_input.returnPressed.connect(self._send_clicked)
        self.send_btn = CustomButton("发送", variant="primary")
        self.send_btn.clicked.connect(self._send_clicked)

        input_row.addWidget(self.chat_input, 1)
        input_row.addWidget(self.send_btn)
        card.body_layout.addLayout(input_row)

    @staticmethod
    def _clean_assistant_text(content: str) -> str:
        return strip_state_block(content)

    def _add_bubble(self, text: str, role: str):
        bubble = ChatBubble(text, role)
        self.chat_layout.addWidget(bubble)
        if role == "assistant":
            self.last_assistant_bubble = bubble
        # Ensure container resizes properly
        self.container.updateGeometry()
        self.scroll_area.updateGeometry()
            
        # Auto scroll to bottom
        QTimer.singleShot(50, self._scroll_to_bottom)
        return bubble

    def _scroll_to_bottom(self):
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def restore_history_display(self, history: list[dict]):
        """以分块方式恢复聊天历史，避免一次性创建大量 widget 导致主线程卡顿"""
        self.clear()
        # 使用生成器按批次还原历史
        self._restore_history_iter = (msg for msg in (history or []) if msg.get("role") != "system")
        self._restore_batch_process()

    def _restore_batch_process(self):
        BATCH = 8
        count = 0
        while count < BATCH:
            try:
                msg = next(self._restore_history_iter)
            except StopIteration:
                # 完成后滚动到底部
                if hasattr(self, '_restore_history_iter'):
                    del self._restore_history_iter
                QTimer.singleShot(50, self._scroll_to_bottom)
                return
            role = msg.get("role")
            content = msg.get("content", "")
            if role == "user":
                if "生成一段开场白" in str(content):
                    continue
                self._add_bubble(str(content), "user")
            elif role == "assistant":
                clean = self._clean_assistant_text(str(content))
                if clean:
                    self._add_bubble(clean, "assistant")
            count += 1
        # 计划下一批次
        QTimer.singleShot(10, self._restore_batch_process)

    def _send_clicked(self):
        text = self.chat_input.text().strip()
        if not text:
            return
        self.chat_input.clear()
        self._on_send(text)
    def append_text(self, text: str, role: str):
        if not text:
            return
        if role == "user":
            self._add_bubble(text, "user")
        elif role == "assistant":
            if self.last_assistant_bubble:
                self.last_assistant_bubble.append_text(text)
                # Ensure newly appended content is visible
                self._scroll_to_bottom()
            else:
                self._add_bubble(text, "assistant")
        else:
            self._add_bubble(text, "system")

    def clear(self):
        while self.chat_layout.count():
            item = self.chat_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.last_assistant_bubble = None

    def set_enabled(self, enabled: bool):
        self.chat_input.setEnabled(enabled)
        self.send_btn.setEnabled(enabled)
        self.send_btn.setText("发送" if enabled else "...")
        if enabled:
            self.chat_input.setFocus()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(100, self._scroll_to_bottom)
