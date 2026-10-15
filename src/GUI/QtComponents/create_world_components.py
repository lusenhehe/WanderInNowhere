from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFormLayout,
    QLineEdit,
    QHBoxLayout,
)
from src.GUI.CustomWidgets.custom_combo_box import CustomComboBox
from src.GUI.QtComponents.cards import Card
from src.GUI.CustomWidgets.custom_button import CustomButton
from src.Constants.ui_constants import UI_TEXTS
from PyQt6.QtCore import Qt


def _repolish(widget: QWidget) -> None:
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()

class CreateWorldHeaderComponent(QWidget):
    def __init__(self, *, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        card = Card(None)
        card.setObjectName("CreateHeaderCard")
        card.setMaximumHeight(100)
        layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignHCenter)

        title = QLabel(UI_TEXTS["create_world"]["title"])
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title.setProperty("role", "title")
        subtitle = QLabel(UI_TEXTS["create_world"]["subtitle"])
        subtitle.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        subtitle.setProperty("role", "subtitle")
        card.body_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        card.body_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)
        card.body_layout.addWidget(subtitle, alignment=Qt.AlignmentFlag.AlignHCenter)


class CreateWorldFormComponent(QWidget):
    def __init__(self, *, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        card = Card(UI_TEXTS["create_world"]["form_title"])
        card.setObjectName("CreateFormCard")
        layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignHCenter)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setHorizontalSpacing(14)
        card.body_layout.addLayout(form)

        self.world_name = QLineEdit()
        self.world_name.setPlaceholderText("例如：新的世界")
        self.world_name.setMaximumWidth(420)
        self.player_name = QLineEdit()
        self.player_name.setPlaceholderText("例如：Steve")
        self.player_name.setMaximumWidth(300)

        # Helper texts
        self.helper_world = QLabel("建议使用 3-20 字符")
        self.helper_world.setProperty('formHelper', True)
        self.helper_player = QLabel("由你扮演的主角名称")
        self.helper_player.setProperty('formHelper', True)
        self.race = CustomComboBox()
        self.race.addItems(["人类", "高等精灵", "不死族", "魔物"])

        self.magic = CustomComboBox()
        self.magic.addItems(["低 (0-25%)", "一般 (25-50%)", "高 (50-85%)", "极高 (85%以上)"])
        self.magic.setCurrentText("一般 (25-50%)")

        self.birthplace = CustomComboBox()
        self.birthplace.addItems(["北境", "南疆", "废都", "浮空城"])
        self.birthplace.setCurrentText("南疆")

        form.addRow(UI_TEXTS["create_world"]["world_name_label"], self.world_name)
        form.addRow("", self.helper_world)
        form.addRow(UI_TEXTS["create_world"]["player_name_label"], self.player_name)
        form.addRow("", self.helper_player)
        form.addRow(UI_TEXTS["create_world"]["race_label"], self.race)
        form.addRow(UI_TEXTS["create_world"]["magic_label"], self.magic)
        form.addRow(UI_TEXTS["create_world"]["birthplace_label"], self.birthplace)
    def validate(self) -> bool:
        valid = True
        if not self.world_name.text().strip():
            self.world_name.setProperty("invalid", True)
            _repolish(self.world_name)
            valid = False
        else:
            self.world_name.setProperty("invalid", False)
            _repolish(self.world_name)
        if not self.player_name.text().strip():
            self.player_name.setProperty("invalid", True)
            _repolish(self.player_name)
            valid = False
        else:
            self.player_name.setProperty("invalid", False)
            _repolish(self.player_name)
        return valid


class CreateWorldActionsComponent(QWidget):
    def __init__(self, *, on_create, on_cancel, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        card = Card(UI_TEXTS["create_world"]["actions_title"])
        card.setObjectName("CreateActionsCard")
        card.setMaximumHeight(90)
        layout.addWidget(card, alignment=Qt.AlignmentFlag.AlignHCenter)

        row = QHBoxLayout()
        row.setSpacing(12)
        create_btn = CustomButton(UI_TEXTS["create_world"]["btn_create"], variant="primary")
        cancel_btn = CustomButton(UI_TEXTS["create_world"]["btn_cancel"], variant="secondary")
        create_btn.setMinimumWidth(140)
        create_btn.setFixedHeight(44)
        cancel_btn.setMinimumWidth(110)
        cancel_btn.setFixedHeight(40)
        create_btn.clicked.connect(on_create)
        cancel_btn.clicked.connect(on_cancel)
        row.addStretch(1)
        row.addWidget(create_btn)
        row.addWidget(cancel_btn)
        row.addStretch(1)
        card.body_layout.addLayout(row)
