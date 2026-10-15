from typing import Callable
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QTreeWidgetItem, QMenu, QWidget, QVBoxLayout, QScrollArea
from src.GUI.CustomWidgets.CardWidgets import EntityCardQt
from src.theme_manager import theme_manager
from src.utils.logger import logger
from src.GUI.QtComponents.cards import Card
from src.GUI.QtComponents.debug_utils import DebugEditDialog, debug_enabled
from src.Constants.debug_constants import DEBUG_FIELDS


class EntitiesComponent(QWidget):
    def __init__(
        self,
        on_select,
        on_edit: Callable | None = None,
        on_delete: Callable | None = None,
        on_add: Callable | None = None,
        *,
        debug_ctx: object | None = None,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._on_select = on_select
        self._on_edit = on_edit
        self._on_delete = on_delete
        self._on_add = on_add
        self._debug_ctx = debug_ctx

        self._entities: list[object] = []
        self._cards: list[EntityCardQt] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        card = Card("👥 实体")
        layout.addWidget(card, 1)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        card.body_layout.addWidget(self.scroll, 1)

        self._inner = QWidget()
        self._inner_layout = QVBoxLayout(self._inner)
        self._inner_layout.setContentsMargins(0, 0, 0, 0)
        self._inner_layout.setSpacing(8)
        self._inner_layout.addStretch(1)
        self.scroll.setWidget(self._inner)

        # Enable context menu on the inner widget for adding
        self._inner.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._inner.customContextMenuRequested.connect(self._on_inner_context_menu)

    def _on_inner_context_menu(self, pos):
        if not debug_enabled():
            return
        menu = QMenu()
        if callable(self._on_add):
            menu.addAction("添加实体", self._on_add)
        else:
            menu.addAction("添加实体", self._debug_add_entity)
        menu.exec(self._inner.mapToGlobal(pos))

    # ===== Debug actions (optional) =====
    def _debug_edit_entity(self, index: int) -> None:
        if not debug_enabled() or self._debug_ctx is None:
            return

        ents = getattr(self._debug_ctx, "entities", []) or []
        if index < 0 or index >= len(ents):
            return

        ent = ents[index]
        cur = {
            "name": getattr(ent, "name", "") or "",
            "attitude": getattr(ent, "attitude", "") or "",
            "desc": getattr(ent, "description", "") or "",
            "location": getattr(ent, "location", "") or "",
            "equipment": getattr(ent, "equipment", None),
        }
        fields = DEBUG_FIELDS.get("entity", [])
        dlg = DebugEditDialog(self, "编辑实体", fields, values=cur)

        from PyQt6.QtWidgets import QDialog

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        new = dlg.get_result()
        try:
            setattr(ent, "name", new.get("name", getattr(ent, "name", "")))
            setattr(ent, "attitude", new.get("attitude", getattr(ent, "attitude", "")))
            setattr(ent, "description", new.get("desc", getattr(ent, "description", "")))
            setattr(ent, "location", new.get("location", getattr(ent, "location", "")))
            setattr(ent, "equipment", new.get("equipment", getattr(ent, "equipment", None)))
        except Exception:
            pass
        try:
            self._debug_ctx.update_ui_display()
        except Exception:
            pass

    def _debug_delete_entity(self, index: int) -> None:
        if not debug_enabled() or self._debug_ctx is None:
            return

        ents = getattr(self._debug_ctx, "entities", []) or []
        if index < 0 or index >= len(ents):
            return

        from PyQt6.QtWidgets import QMessageBox

        if (
            QMessageBox.question(self, "删除实体", "确认删除该实体？", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            != QMessageBox.StandardButton.Yes
        ):
            return

        del ents[index]
        try:
            self._debug_ctx.entities = ents
        except Exception:
            pass
        try:
            self._debug_ctx.update_ui_display()
        except Exception:
            pass

    def _debug_add_entity(self) -> None:
        if not debug_enabled() or self._debug_ctx is None:
            return

        fields = DEBUG_FIELDS.get("entity", [])
        dlg = DebugEditDialog(self, "添加实体", fields)

        from PyQt6.QtWidgets import QDialog, QMessageBox

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        new = dlg.get_result()
        from src.Data.EntityData import EntityData

        try:
            entity = EntityData(
                name=new.get("name", "新实体"),
                attitude=new.get("attitude", "Neutral"),
                description=new.get("desc", ""),
                location=new.get("location", "未知地点"),
                equipment=new.get("equipment", None),
            )
            ents = getattr(self._debug_ctx, "entities", []) or []
            ents.append(entity)
            self._debug_ctx.entities = ents
        except Exception as e:
            QMessageBox.warning(self, "错误", f"添加实体失败: {e}")
        try:
            self._debug_ctx.update_ui_display()
        except Exception:
            pass

    def _on_current_item_changed(self, current: QTreeWidgetItem | None, _prev: QTreeWidgetItem | None):
        if current is None:
            return
        idx = current.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(idx, int):
            self._on_select(idx)

    def set_items(self, items: list):
        # items can be list[str] or list[object]
        self._cards = []
        while self._inner_layout.count() > 1:
            item = self._inner_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        items = items or []
        if not items:
            from PyQt6.QtWidgets import QLabel
            empty = QLabel("暂无实体")
            empty.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            empty.setStyleSheet(f"color: {theme_manager.currentTheme.COLOR_TEXT_SECONDARY}; font-style: italic;")
            self._inner_layout.insertWidget(0, empty)
            return

        # 使用迭代器分批创建，避免一次性构造大量 widgets 导致主线程卡顿
        self._items_iter = ((i, it) for i, it in enumerate(items))
        # 立即启动第一批
        QTimer.singleShot(0, self._populate_entities_batch)

    def _populate_entities_batch(self):
        BATCH = 6
        count = 0
        while count < BATCH:
            try:
                i, it = next(self._items_iter)
            except StopIteration:
                if hasattr(self, '_items_iter'):
                    del self._items_iter
                try:
                    logger.info(f"Entities populated: {len(self._cards)} items")
                except Exception:
                    pass
                return
            if isinstance(it, str):
                name = it
                attitude = "Neutral"
                location = ""
                equipment = None
                description = ""
            else:
                name = getattr(it, 'name', str(it))
                attitude = getattr(it, 'attitude', 'Neutral')
                location = getattr(it, 'location', '') or ''
                equipment = getattr(it, 'equipment', None)
                description = getattr(it, 'description', '') or ''

            on_edit = self._on_edit if callable(self._on_edit) else self._debug_edit_entity
            on_delete = self._on_delete if callable(self._on_delete) else self._debug_delete_entity
            cardw = EntityCardQt(index=i, name=name, attitude=attitude, location=location, equipment=equipment, description=description, on_click=self._card_clicked, on_edit=on_edit, on_delete=on_delete)
            self._cards.append(cardw)
            self._inner_layout.insertWidget(self._inner_layout.count() - 1, cardw)
            count += 1
        QTimer.singleShot(10, self._populate_entities_batch)

    def _card_clicked(self, idx: int):
        # single-select visual
        for c in self._cards:
            c.set_selected(c.index == idx)
        if callable(self._on_select):
            self._on_select(idx)
