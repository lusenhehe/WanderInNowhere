class InventoryHandlersMixin:
    def _on_inventory_selected(self, row: int):
        if row < 0 or row >= len(self.player_data.inventory):
            return
        item = self.player_data.inventory[row]
        name = getattr(item, "name", str(item))
        desc = getattr(item, "description", "暂无描述")
        self.detail_component.set_text(f"【{name}】\n\n{desc}")

    def _on_equipment_clicked(self, slot: str):
        equip = getattr(self.player_data, "equipment", {}) or {}
        item = equip.get(slot)
        if not item:
            self.detail_component.set_text("（空）")
            return
        name = getattr(item, "name", str(item))
        desc = getattr(item, "description", "暂无描述")
        self.detail_component.set_text(f"【{name}】\n\n{desc}")
