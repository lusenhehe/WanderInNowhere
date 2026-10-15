class EntitiesHandlersMixin:
    def _on_entity_selected(self, row: int):
        if row < 0 or row >= len(self.entities):
            return
        e = self.entities[row]
        name = getattr(e, "name", "未知实体")
        details = f"【{name}】\n"
        desc = getattr(e, "description", "") or ""
        if desc:
            details += f"{desc}\n"
        attitude = getattr(e, "attitude", "Neutral")
        attitude_text = {"Enemy": "敌对", "Friendly": "友好", "Neutral": "中立"}.get(attitude, str(attitude))
        details += f"态度: {attitude_text}\n"
        loc = getattr(e, "location", "") or ""
        if loc:
            details += f"地点: {loc}\n"
        equip = getattr(e, "equipment", None)
        if equip:
            if isinstance(equip, dict):
                equip_items = []
                for v in equip.values():
                    if not v:
                        continue
                    equip_items.append(getattr(v, "name", str(v)))
                equip_display = ", ".join(equip_items) if equip_items else "-"
            else:
                equip_display = getattr(equip, "name", str(equip))
            details += f"装备: {equip_display}\n"
        self.detail_component.set_text(details)