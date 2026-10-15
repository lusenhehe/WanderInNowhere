import math

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QFrame,
    QListWidget,
    QListWidgetItem,
    QMenu,
)
from typing import Callable, Optional, Dict, List
from collections import OrderedDict

from src.GUI.QtComponents.debug_utils import DebugEditDialog, debug_enabled
from src.Constants.debug_constants import DEBUG_FIELDS
from src.Data.ItemData import ItemData
from src.GUI.QtComponents.cards import Card
from src.GUI.CustomWidgets.CardWidgets import InventoryItemCardQt
from src.theme_manager import theme_manager
from src.Constants.game_constants import EQUIPMENT_SLOTS
from src.GUI.icons import icon_manager
class InventoryComponent(QWidget):
    def __init__(
        self,
        on_money_clicked: Callable[[], None] | None,
        on_item_selected: Callable[[int], None],
        on_equipment_clicked: Callable[[str], None],
        on_edit_item: Callable | None = None,
        on_delete_item: Callable | None = None,
        on_add_item: Callable | None = None,
        *,
        debug_ctx: object | None = None,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._debug_ctx = debug_ctx
        self._on_money_clicked = on_money_clicked
        self._on_item_selected = on_item_selected
        self._on_equipment_clicked = on_equipment_clicked
        self._on_edit_item = on_edit_item
        self._on_delete_item = on_delete_item
        self._on_add_item = on_add_item
        self._selected_index = -1
        self._inventory_names: List[str] = []
        self._inventory_index_map: List[int] = []

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(10)

        # Single unified "物品" card (money + equipment + backpack in one area)
        items_card = Card("🎒 物品")
        main_layout.addWidget(items_card, 1)

        # Top: money row inside the same card
        money_row = QHBoxLayout()
        money_row.setContentsMargins(10, 4, 10, 4)
        money_icon = QLabel()
        money_icon.setPixmap(icon_manager.get_pixmap("money", QSize(20, 20)))
        money_row.addWidget(money_icon)
        self.money_label = QLabel("0铜")
        self.money_label.setProperty("role", "money")
        self.money_label.mousePressEvent = lambda _ev: self._handle_money_clicked()
        money_row.addWidget(self.money_label)
        money_row.addStretch()
        items_card.body_layout.addLayout(money_row)

        # Main content inside the same card: backpack grid (top) + equipment (bottom)
        content_layout = QVBoxLayout()
        content_layout.setSpacing(8)
        items_card.body_layout.addLayout(content_layout, 1)

        # Top: Backpack list
        inv_container = QFrame()
        inv_layout = QVBoxLayout(inv_container)
        inv_layout.setContentsMargins(6, 6, 6, 6)

        self.inv_list = QListWidget()
        self.inv_list.setObjectName("InventoryList")
        self.inv_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.inv_list.customContextMenuRequested.connect(self._on_container_context_menu)
        self.inv_list.itemClicked.connect(self._on_item_clicked)
        inv_layout.addWidget(self.inv_list)

        content_layout.addWidget(inv_container, 1)

        # Bottom: Equipment area (horizontal layout)
        equip_container = QFrame()
        equip_layout = QHBoxLayout(equip_container)
        equip_layout.setContentsMargins(0,0,0,0)
        self.equip_layout = QHBoxLayout()
        self.equip_layout.setSpacing(6)
        self.equip_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        equip_layout.addLayout(self.equip_layout)
        content_layout.addWidget(equip_container, 0)

        self._equip_slots: dict[str, InventoryItemCardQt] = {}
        self._setup_equipment_layout()
        
        self._relayout_items()

    def _on_item_clicked(self, item: QListWidgetItem):
        view_index = item.data(Qt.ItemDataRole.UserRole)
        if view_index is not None:
            self._select_item(view_index)

    def _on_container_context_menu(self, pos):
        if not debug_enabled():
            return
        menu = QMenu()
        if callable(self._on_add_item):
            menu.addAction("添加物品", self._on_add_item)
        else:
            menu.addAction("添加物品", self._debug_add_item)
        menu.exec(self.inv_list.mapToGlobal(pos))

    def _setup_equipment_layout(self) -> None:
        # Horizontal layout for equipment slots: head, body, legs, weapon, accessory
        slots_order = ["head", "body", "legs", "weapon", "accessory"]

        for slot in slots_order:
            if slot in EQUIPMENT_SLOTS:
                slot_name = EQUIPMENT_SLOTS[slot]
                widget = InventoryItemCardQt(slot_name, is_equipment=True, slot_id=slot, on_click=self._on_equipment_clicked)
                self.equip_layout.addWidget(widget)
                self._equip_slots[slot] = widget

    def _relayout_items(self) -> None:
        # Clear existing items
        self.inv_list.clear()
        self._inventory_index_map.clear()
        
        if not self._inventory_names:
            return

        # Build stacked view: same-name items are aggregated into one row.
        counts: "OrderedDict[str, dict]" = OrderedDict()
        for original_index, raw_name in enumerate(self._inventory_names):
            name = (raw_name or "").strip()
            if not name:
                name = "未知物品"
            if name not in counts:
                counts[name] = {"count": 1, "first_index": original_index, "indices": [original_index]}
            else:
                counts[name]["count"] += 1
                counts[name]["indices"].append(original_index)

        # Add items to list
        for view_index, (name, info) in enumerate(counts.items()):
            count = int(info.get("count", 1) or 1)
            display_name = f"{name}×{count}" if count > 1 else name
            original_index = int(info.get("first_index", 0) or 0)
            self._inventory_index_map.append(original_index)

            item = QListWidgetItem(display_name)
            item.setData(Qt.ItemDataRole.UserRole, view_index)
            self.inv_list.addItem(item)

            if view_index == self._selected_index:
                item.setSelected(True)

    @staticmethod
    def format_money(total_copper: int) -> str:
        total_copper = int(total_copper or 0)
        platinum = total_copper // 1000000
        remainder = total_copper % 1000000
        gold = remainder // 10000
        remainder = remainder % 10000
        silver = remainder // 100
        copper = remainder % 100

        parts = []
        if platinum > 0:
            parts.append(f"{platinum}铂金")
        if gold > 0:
            parts.append(f"{gold}金")
        if silver > 0:
            parts.append(f"{silver}银")
        if copper > 0 or not parts:
            parts.append(f"{copper}铜")
        return " ".join(parts)

    def _select_item(self, index: int) -> None:
        self._selected_index = index
        # Update list selection
        for i in range(self.inv_list.count()):
            item = self.inv_list.item(i)
            view_index = item.data(Qt.ItemDataRole.UserRole)
            if view_index == index:
                item.setSelected(True)
            else:
                item.setSelected(False)
        
        if self._on_item_selected:
            # Map from stacked view index -> original inventory index
            if 0 <= index < len(self._inventory_index_map):
                self._on_item_selected(self._inventory_index_map[index])
            else:
                self._on_item_selected(index)

    def _edit_item(self, index: int) -> None:
        if 0 <= index < len(self._inventory_index_map):
            index = self._inventory_index_map[index]
        if callable(self._on_edit_item):
            self._on_edit_item(index)
            return
        self._debug_edit_item(index)

    def _delete_item(self, index: int) -> None:
        if 0 <= index < len(self._inventory_index_map):
            index = self._inventory_index_map[index]
        if callable(self._on_delete_item):
            self._on_delete_item(index)
            return
        self._debug_delete_item(index)

    def _handle_money_clicked(self) -> None:
        if callable(self._on_money_clicked):
            self._on_money_clicked()
            return
        self._debug_edit_money()

    def _debug_edit_money(self) -> None:
        if not debug_enabled() or self._debug_ctx is None:
            return

        from PyQt6.QtWidgets import QInputDialog

        try:
            cur = int(getattr(self._debug_ctx.player_data, "money", 0) or 0)
        except Exception:
            cur = 0

        new_val, ok = QInputDialog.getInt(self, "Debug 修改", "修改金钱 (铜币):", value=cur, min=0)
        if not ok:
            return

        try:
            self._debug_ctx.player_data.money = int(new_val)
            self._debug_ctx.update_ui_display()
        except Exception:
            return

    def _debug_add_item(self) -> None:
        if not debug_enabled() or self._debug_ctx is None:
            return

        fields = DEBUG_FIELDS.get("item", [])
        dlg = DebugEditDialog(self, "添加物品", fields)

        from PyQt6.QtWidgets import QDialog, QMessageBox

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        new = dlg.get_result()
        try:
            item = ItemData(name=new.get("name", "新物品"), description=new.get("desc", ""))
            inv = getattr(self._debug_ctx.player_data, "inventory", []) or []
            inv.append(item)
            self._debug_ctx.player_data.inventory = inv
        except Exception as e:
            QMessageBox.warning(self, "错误", f"添加物品失败: {e}")
        self._debug_ctx.update_ui_display()

    def _debug_edit_item(self, index: int) -> None:
        if not debug_enabled() or self._debug_ctx is None:
            return

        inv = getattr(self._debug_ctx.player_data, "inventory", []) or []
        if index < 0 or index >= len(inv):
            return

        item = inv[index]
        cur = {
            "name": getattr(item, "name", str(item)) or "",
            "desc": getattr(item, "description", "") or "",
        }
        fields = DEBUG_FIELDS.get("item", [])
        dlg = DebugEditDialog(self, "编辑物品", fields, values=cur)

        from PyQt6.QtWidgets import QDialog

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        new = dlg.get_result()
        try:
            setattr(item, "name", new.get("name", getattr(item, "name", "")))
            setattr(item, "description", new.get("desc", getattr(item, "description", "")))
        except Exception:
            pass
        self._debug_ctx.update_ui_display()

    def _debug_delete_item(self, index: int) -> None:
        if not debug_enabled() or self._debug_ctx is None:
            return

        inv = getattr(self._debug_ctx.player_data, "inventory", []) or []
        if index < 0 or index >= len(inv):
            return

        from PyQt6.QtWidgets import QMessageBox

        if (
            QMessageBox.question(self, "删除物品", "确认删除该物品？", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            != QMessageBox.StandardButton.Yes
        ):
            return

        del inv[index]
        self._debug_ctx.player_data.inventory = inv
        self._debug_ctx.update_ui_display()

    def update_display(self, *, money: int, inventory_names: List[str], equipment_names: Dict[str, Optional[str]]) -> None:
        self.money_label.setText(self.format_money(money))

        # Update Inventory Grid
        self._inventory_names = inventory_names
        self._relayout_items()

        # Update Equipment Slots
        for slot, widget in self._equip_slots.items():
            val = equipment_names.get(slot)
            widget.set_item(val)

__all__ = ["InventoryComponent"]
