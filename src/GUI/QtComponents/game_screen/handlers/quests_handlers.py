from PyQt6.QtWidgets import QMessageBox


class QuestsHandlersMixin:
    def _on_active_quest_selected(self, row_or_quest: int | dict):
        if isinstance(row_or_quest, dict):
            self._show_quest_detail(row_or_quest)
            return

        row = int(row_or_quest)
        quests = getattr(self.player_data, "quests", []) or []
        active = [q for q in quests if q.get("status") == "进行中"]
        if row < 0 or row >= len(active):
            return
        self._show_quest_detail(active[row])

    def _on_done_quest_selected(self, row_or_quest: int | dict):
        if isinstance(row_or_quest, dict):
            self._show_quest_detail(row_or_quest)
            return

        row = int(row_or_quest)
        quests = getattr(self.player_data, "quests", []) or []
        done = [q for q in quests if q.get("status") != "进行中"]
        if row < 0 or row >= len(done):
            return
        self._show_quest_detail(done[row])

    def _on_abandon_quest(self, quest: dict):
        title = str((quest or {}).get("title", ""))
        result = QMessageBox.question(
            self,
            "放弃任务",
            f"确定放弃任务: {title} ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if result != QMessageBox.StandardButton.Yes:
            return

        qid = (quest or {}).get("id")
        quests = getattr(self.player_data, "quests", None)
        if not isinstance(quests, list):
            quests = []

        removed = False
        if qid:
            for i, q in enumerate(list(quests)):
                if isinstance(q, dict) and q.get("id") == qid:
                    del quests[i]
                    removed = True
                    break

        if not removed:
            for i, q in enumerate(list(quests)):
                if q == quest:
                    del quests[i]
                    removed = True
                    break
                if isinstance(q, dict) and q.get("title") == title and q.get("status") == quest.get("status"):
                    del quests[i]
                    removed = True
                    break

        self.player_data.quests = quests
        self.update_ui_display()

    def _show_quest_detail(self, q: dict):
        q = q or {}
        qid = q.get("id")
        title = str(q.get("title", "无标题"))
        status = str(q.get("status", ""))
        desc = str(q.get("description", "无描述"))

        parts: list[str] = [title, "", desc, ""]
        if status:
            parts.append(f"状态: {status}")
        if qid:
            parts.append(f"任务ID: {qid}")

        source = q.get("source")
        if source:
            parts.append(f"来源: {source}")
        reward = q.get("reward")
        if reward:
            parts.append(f"奖励: {reward}")
        conditions = q.get("conditions")
        if conditions:
            parts.append("")
            parts.append("条件:")
            parts.append(str(conditions))

        self.detail_component.set_text("\n".join(parts).strip())
