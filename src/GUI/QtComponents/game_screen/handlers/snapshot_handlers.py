class SnapshotHandlersMixin:
    @staticmethod
    def _safe_serialize(obj):
        if obj is None:
            return None
        if isinstance(obj, (str, int, float, bool)):
            return obj
        if isinstance(obj, dict):
            return {str(k): SnapshotHandlersMixin._safe_serialize(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple)):
            return [SnapshotHandlersMixin._safe_serialize(v) for v in obj]
        if hasattr(obj, "to_dict") and callable(getattr(obj, "to_dict")):
            try:
                return SnapshotHandlersMixin._safe_serialize(obj.to_dict())
            except Exception:
                pass
        return {
            "name": getattr(obj, "name", str(obj)),
            "attitude": getattr(obj, "attitude", None),
            "description": getattr(obj, "description", None),
        }

    def _snapshot_for_updates(self) -> dict:
        # Keep it deterministic and cheap; only computed at AI finish.
        inv = getattr(self.player_data, "inventory", []) or []
        equip = getattr(self.player_data, "equipment", {}) or {}
        skills = getattr(self.player_data, "skills", []) or []
        quests = getattr(self.player_data, "quests", []) or []

        inv_ser = [self._safe_serialize(i) for i in inv]
        equip_ser = {str(k): self._safe_serialize(v) for k, v in (equip or {}).items()}
        skills_ser = [self._safe_serialize(s) for s in skills]
        quests_ser = [self._safe_serialize(q) for q in quests]
        ents_ser = [
            {
                "name": getattr(e, "name", str(e)),
                "attitude": getattr(e, "attitude", None),
                "description": getattr(e, "description", None),
            }
            for e in (self.entities or [])
        ]
        return {
            "status": self._safe_serialize(getattr(self.player_data, "status", {}) or {}),
            "money": getattr(self.player_data, "money", None),
            "inventory": inv_ser,
            "equipment": equip_ser,
            "skills": skills_ser,
            "quests": quests_ser,
            "entities": ents_ser,
            "summaries": self._safe_serialize(self.summaries or []),
        }

    def _apply_update_indicators(self, before: dict, after: dict) -> None:
        # Map data keys to tabs
        changed = {
            "status": before.get("status") != after.get("status"),
            "inventory": (before.get("money") != after.get("money"))
            or (before.get("inventory") != after.get("inventory"))
            or (before.get("equipment") != after.get("equipment")),
            "skills": before.get("skills") != after.get("skills"),
            "quests": before.get("quests") != after.get("quests"),
            "entities": before.get("entities") != after.get("entities"),
            "summaries": before.get("summaries") != after.get("summaries"),
        }

        # Left tabs: 0 chat, 1 entities, 2 summaries
        if changed.get("entities") and self.left_tabs.currentIndex() != 1:
            self._tab_dirty[("left", 1)] = True
        if changed.get("summaries") and self.left_tabs.currentIndex() != 2:
            self._tab_dirty[("left", 2)] = True

        # Center tabs: 0 status, 1 inventory, 2 skills, 3 quests
        if changed.get("status") and self.center_tabs.currentIndex() != 0:
            self._tab_dirty[("center", 0)] = True
        if changed.get("inventory") and self.center_tabs.currentIndex() != 1:
            self._tab_dirty[("center", 1)] = True
        if changed.get("skills") and self.center_tabs.currentIndex() != 2:
            self._tab_dirty[("center", 2)] = True
        if changed.get("quests") and self.center_tabs.currentIndex() != 3:
            self._tab_dirty[("center", 3)] = True

        self._update_tab_badges()
