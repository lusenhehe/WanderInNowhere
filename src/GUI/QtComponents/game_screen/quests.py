from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget,QVBoxLayout,QLabel,QMessageBox,QDialog,QScrollArea,QFrame,QMenu,QSizePolicy
from src.GUI.QtComponents.cards import Card
from src.GUI.CustomWidgets.CardWidgets import QuestCardQt
from src.theme_manager import theme_manager
from typing import Callable

from src.GUI.QtComponents.debug_utils import DebugEditDialog, debug_enabled
from src.Constants.debug_constants import DEBUG_FIELDS

class QuestsComponent(QWidget):
    def __init__(self,on_active_select,on_done_select,on_abandon=None,on_edit: Callable | None = None,on_delete: Callable | None = None,on_add: Callable | None = None,*,debug_ctx: object | None = None,parent: QWidget | None = None,):
        super().__init__(parent)
        self._on_active_select = on_active_select
        self._on_done_select = on_done_select
        self._on_abandon = on_abandon
        self._on_edit = on_edit
        self._on_delete = on_delete
        self._on_add = on_add
        self._debug_ctx = debug_ctx
        self._cards: list[QuestCardQt] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        card = Card("任务")
        layout.addWidget(card, 1)

        self.scroll = QScrollArea()
        # Ensure the scroll area will resize its widget to fit the viewport
        self.scroll.setWidgetResizable(True)
        card.body_layout.addWidget(self.scroll, 1)

        self._inner = QWidget()
        # Allow the inner widget to expand vertically as children are added
        self._inner.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        self._inner_layout = QVBoxLayout(self._inner)
        self._inner_layout.setContentsMargins(0, 0, 0, 0)
        self._inner_layout.setSpacing(10)
        self._inner_layout.addStretch(1)
        self.scroll.setWidget(self._inner)

        # Enable context menu on the inner widget for adding
        self._inner.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._inner.customContextMenuRequested.connect(self._on_inner_context_menu)

    def set_quests(self, *, active: list[dict], done: list[dict]):
        # clear existing cards list and widgets
        self._cards = []
        while self._inner_layout.count() > 1:
            item = self._inner_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        self._add_section(title="进行中", quests=active or [], is_active=True, empty_text="暂无进行中的任务")
        sep = QFrame()
        sep.setFixedHeight(2)
        sep.setStyleSheet(f"background-color: {theme_manager.currentTheme.COLOR_BORDER};")
        self._inner_layout.insertWidget(self._inner_layout.count() - 1, sep)
        self._add_section(title="已结束", quests=done or [], is_active=False, empty_text="暂无已结束的任务")
    def _add_section(self, *, title: str, quests: list[dict], is_active: bool, empty_text: str):
        label = QLabel(title)
        label.setStyleSheet(f"font-weight: 700; color: {theme_manager.currentTheme.COLOR_TEXT_SECONDARY};")
        self._inner_layout.insertWidget(self._inner_layout.count() - 1, label)

        if not quests:
            empty = QLabel(empty_text)
            empty.setStyleSheet(f"font-style: italic; color: {theme_manager.currentTheme.COLOR_TEXT_SECONDARY};")
            self._inner_layout.insertWidget(self._inner_layout.count() - 1, empty)
            return

        for q in quests:
            # wrap click so we can manage single-selection and still call external callbacks
            card = QuestCardQt(
                quest=q,
                is_active=is_active,
                on_click=self._card_clicked,
                on_abandon=self._on_abandon,
                on_edit=(self._on_edit if callable(self._on_edit) else self._debug_edit_quest),
                on_delete=(self._on_delete if callable(self._on_delete) else self._debug_delete_quest),
            )
            self._cards.append(card)
            self._inner_layout.insertWidget(self._inner_layout.count() - 1, card)

    def _card_clicked(self, quest: dict, card: 'QuestCardQt'):
        # deselect others
        for c in self._cards:
            if c is card:
                c.set_selected(True)
            else:
                c.set_selected(False)

        # call external callback with quest dict
        try:
            if quest.get("status") == "进行中":
                if callable(self._on_active_select):
                    self._on_active_select(quest)
            else:
                if callable(self._on_done_select):
                    self._on_done_select(quest)
        except Exception:
            # fallback: call active selector
            if callable(self._on_active_select):
                self._on_active_select(quest)

    def _on_inner_context_menu(self, pos):
        if not debug_enabled():
            return
        menu = QMenu()
        if callable(self._on_add):
            menu.addAction("添加任务", self._on_add)
        else:
            menu.addAction("添加任务", self._debug_add_quest)
        menu.exec(self._inner.mapToGlobal(pos))

    # ===== Debug actions (optional) =====
    def _debug_add_quest(self) -> None:
        if not debug_enabled() or self._debug_ctx is None:
            return
        fields = DEBUG_FIELDS.get("quest", [])
        dlg = DebugEditDialog(self, "添加任务", fields)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        new = dlg.get_result()
        quest = {
            "id": new.get("qid", ""),
            "title": new.get("title", "新任务"),
            "description": new.get("desc", ""),
            "status": "进行中",
        }

        quests = getattr(self._debug_ctx.player_data, "quests", []) or []
        quests.append(quest)
        self._debug_ctx.player_data.quests = quests
        self._debug_ctx.update_ui_display()

    def _debug_edit_quest(self, quest: dict, _card=None) -> None:
        if not debug_enabled() or self._debug_ctx is None:
            return

        q = quest or {}
        cur = {
            "qid": q.get("id", ""),
            "title": q.get("title", ""),
            "desc": q.get("description", ""),
        }
        fields = DEBUG_FIELDS.get("quest", [])
        dlg = DebugEditDialog(self, "编辑任务", fields, values=cur)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        new = dlg.get_result()
        quests = getattr(self._debug_ctx.player_data, "quests", []) or []
        for qq in quests:
            if qq is quest or (isinstance(qq, dict) and qq.get("id") == q.get("id")) or qq.get("title") == q.get("title"):
                qq["id"] = new.get("qid", qq.get("id"))
                qq["title"] = new.get("title", qq.get("title"))
                qq["description"] = new.get("desc", qq.get("description"))
                break

        self._debug_ctx.update_ui_display()

    def _debug_delete_quest(self, quest: dict) -> None:
        if not debug_enabled() or self._debug_ctx is None:
            return

        quests = getattr(self._debug_ctx.player_data, "quests", []) or []
        for i, qq in enumerate(list(quests)):
            if qq is quest or (isinstance(qq, dict) and qq.get("id") == quest.get("id")) or qq.get("title") == quest.get("title"):
                if (
                    QMessageBox.question(self, "删除任务", "确认删除该任务？", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                    != QMessageBox.StandardButton.Yes
                ):
                    return
                del quests[i]
                break
        self._debug_ctx.player_data.quests = quests
        self._debug_ctx.update_ui_display()
