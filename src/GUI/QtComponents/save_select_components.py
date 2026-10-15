from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget,QVBoxLayout,QLabel,QHBoxLayout,QScrollArea
from src.GUI.QtComponents.cards import Card
from src.GUI.CustomWidgets.CardWidgets import SaveCardQt
from src.GUI.CustomWidgets.custom_button import CustomButton
from src.Constants.ui_constants import UI_TEXTS
class SaveSelectHeaderComponent(QWidget):
    def __init__(self, *, parent: QWidget | None = None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        card = Card(None)
        layout.addWidget(card)
        title = QLabel(UI_TEXTS["save_select"]["title"])
        title.setObjectName("SaveSelectTitle")
        subtitle = QLabel(UI_TEXTS["save_select"]["subtitle"])
        subtitle.setObjectName("SaveSelectSubtitle")
        subtitle.setProperty("role", "secondary")
        card.body_layout.addWidget(title)
        card.body_layout.addWidget(subtitle)
class SaveListComponent(QWidget):
    def __init__(self, on_double_click, *, parent: QWidget | None = None):
        super().__init__(parent)
        self._on_double_click = on_double_click
        self.selected_index: int | None = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        card = Card(UI_TEXTS["save_select"]["save_list_title"])
        layout.addWidget(card, 1)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        card.body_layout.addWidget(self.scroll, 1)

        self._inner = QWidget()
        self._inner_layout = QVBoxLayout(self._inner)
        self._inner_layout.setContentsMargins(0, 0, 0, 0)
        self._inner_layout.setSpacing(10)
        self._inner_layout.addStretch(1)
        self.scroll.setWidget(self._inner)
        self._cards: list[SaveCardQt] = []
        self.setObjectName("SaveList")
    def clear(self):
        self.selected_index = None
        for c in self._cards:
            c.deleteLater()
        self._cards = []
        while self._inner_layout.count() > 1:
            item = self._inner_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
    def set_saves(self, saves: list[dict]):
        self.clear()
        saves = saves or []
        if not saves:
            empty = QLabel(UI_TEXTS["save_select"]["empty_hint"])
            empty.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            empty.setObjectName("SaveListEmptyHint")
            empty.setProperty("role", "secondary")
            self._inner_layout.insertWidget(0, empty)
            return

        for i, s in enumerate(saves):
            card = SaveCardQt(save_data=s,index=i,on_select=self.select_index,on_double_click=self._on_double_click,)
            self._cards.append(card)
            self._inner_layout.insertWidget(self._inner_layout.count() - 1, card)
    def select_index(self, idx: int):
        if self.selected_index is not None and 0 <= self.selected_index < len(self._cards):
            self._cards[self.selected_index].set_selected(False)
        self.selected_index = idx
        if 0 <= idx < len(self._cards):
            self._cards[idx].set_selected(True)
class SaveSelectActionsComponent(QWidget):
    def __init__(self,*,on_enter,on_create,on_delete,on_back,parent: QWidget | None = None,):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        card = Card()
        layout.addWidget(card)
        row1 = QHBoxLayout()
        row2 = QHBoxLayout()
        enter_btn  = CustomButton(UI_TEXTS["save_select"]["btn_enter_world"], variant="primary")
        create_btn = CustomButton(UI_TEXTS["save_select"]["btn_create_world"], variant="secondary")
        delete_btn = CustomButton(UI_TEXTS["save_select"]["btn_delete_save"], variant="secondary")
        back_btn   = CustomButton(UI_TEXTS["save_select"]["btn_back"], variant="secondary")
        enter_btn.clicked.connect(on_enter)
        create_btn.clicked.connect(on_create)
        delete_btn.clicked.connect(on_delete)
        back_btn.clicked.connect(on_back)
        row1.addWidget(enter_btn)
        row1.addWidget(create_btn)
        row2.addWidget(delete_btn)
        row2.addWidget(back_btn)
        card.body_layout.addLayout(row1)
        card.body_layout.addLayout(row2)
