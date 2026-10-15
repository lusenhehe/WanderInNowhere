class SkillsHandlersMixin:
    def _on_skill_selected(self, row: int):
        if row < 0 or row >= len(self.player_data.skills):
            return
        skill = self.player_data.skills[row]

        name = getattr(skill, "name", "未知技能")
        desc = getattr(skill, "description", "暂无描述")
        type_data = getattr(skill, "type", ["Element", "无"])
        element = type_data[1] if isinstance(type_data, list) and len(type_data) > 1 else str(type_data)

        cost = getattr(skill, "manacost", 0)
        density = getattr(skill, "concentration", 0)
        rarity = getattr(skill, "rarity", "Common")
        if hasattr(rarity, "value"):
            rarity = rarity.value

        preact = getattr(skill, "preacttime", 1.0)
        finish = getattr(skill, "finishtime", 1.0)

        self.detail_component.set_text(
            f"【{name}】 [{rarity}]\n"
            f"元素: {element} | 消耗: {cost} | 浓度要求: {density}\n"
            f"前摇: {preact}s | 后摇: {finish}s\n\n"
            f"{desc}"
        )
