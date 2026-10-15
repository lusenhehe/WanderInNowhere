from typing import Callable
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel
from src.Data.SkillData import SkillData, Rarity
from src.GUI.QtComponents.cards import Card
from src.GUI.CustomWidgets.CardWidgets.skill_card import SkillCardQt
from src.theme_manager import theme_manager
from src.GUI.QtComponents.debug_utils import DebugEditDialog, debug_enabled
from src.Constants.debug_constants import DEBUG_FIELDS
class SkillsComponent(QWidget):
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
        self._debug_ctx = debug_ctx
        self._on_edit = on_edit
        self._on_delete = on_delete
        self._on_add = on_add
        super().__init__(parent)
        self._on_select = on_select
        self._cards: list[SkillCardQt] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        card = Card("已习得技能")
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

    def set_items(self, items: list):
        # items can be list[str] or list[dict/object]
        self._cards = []
        while self._inner_layout.count() > 1:
            item = self._inner_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        items = items or []
        if not items:
            empty = QLabel("暂无技能")
            empty.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            empty.setStyleSheet(f"color: {theme_manager.currentTheme.COLOR_TEXT_SECONDARY}; font-style: italic;")
            self._inner_layout.insertWidget(0, empty)
            return

        for i, it in enumerate(items):
            if isinstance(it, str):
                name = it
                desc = ""
            else:
                name = getattr(it, 'name', str(it))
                desc = getattr(it, 'description', '') or ''

            on_edit = self._on_edit if callable(self._on_edit) else self._debug_edit_skill
            on_delete = self._on_delete if callable(self._on_delete) else self._debug_delete_skill
            cardw = SkillCardQt(index=i, name=name, description=desc, on_click=self._card_clicked, on_edit=on_edit, on_delete=on_delete)
            self._cards.append(cardw)
            self._inner_layout.insertWidget(self._inner_layout.count() - 1, cardw)

    def _card_clicked(self, idx: int):
        # single-select visual
        for c in self._cards:
            c.set_selected(c.index == idx)
        if callable(self._on_select):
            self._on_select(idx)

    def _on_inner_context_menu(self, pos):
        if not debug_enabled():
            return
        from PyQt6.QtWidgets import QMenu
        menu = QMenu()
        if callable(self._on_add):
            menu.addAction("添加技能", self._on_add)
        else:
            menu.addAction("添加技能", self._debug_add_skill)
        menu.exec(self._inner.mapToGlobal(pos))

    # ===== Debug actions (optional; used when callbacks are not provided) =====
    def _debug_add_skill(self) -> None:
        if not debug_enabled() or self._debug_ctx is None:
            return

        fields = DEBUG_FIELDS.get("skill", [])
        dlg = DebugEditDialog(self, "添加技能", fields)

        from PyQt6.QtWidgets import QDialog, QMessageBox

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        new = dlg.get_result()

        try:
            density_str = str(new.get("density", "0%")).strip()
            if density_str.endswith("%"):
                concentration = int(float(density_str.rstrip("%")))
            else:
                concentration = int(float(density_str) * 100)

            rarity_map = {
                "普通": Rarity.Common,
                "稀有": Rarity.Rare,
                "传奇": Rarity.Legendary,
                "水晶": Rarity.Crystal,
            }
            rarity = rarity_map.get(new.get("rarity", "普通"), Rarity.Common)

            skill = SkillData(
                name=new.get("name", "新技能"),
                type=["Element", new.get("element", "无")],
                manacost=int(new.get("cost", 0)),
                concentration=concentration,
                rarity=rarity,
                preacttime=float(new.get("preacttime", 1.0)),
                finishtime=float(new.get("finishtime", 1.0)),
                description=new.get("desc", ""),
            )
            skills = getattr(self._debug_ctx.player_data, "skills", []) or []
            skills.append(skill)
            self._debug_ctx.player_data.skills = skills
        except Exception as e:
            QMessageBox.warning(self, "错误", f"添加技能失败: {e}")
        self._debug_ctx.update_ui_display()

    def _debug_edit_skill(self, index: int) -> None:
        if not debug_enabled() or self._debug_ctx is None:
            return

        skills = getattr(self._debug_ctx.player_data, "skills", []) or []
        if index < 0 or index >= len(skills):
            return

        skill = skills[index]
        cur = {
            "name": getattr(skill, "name", skill.get("name") if isinstance(skill, dict) else None) or "",
            "element": getattr(skill, "element", "") or (skill.get("element", "") if isinstance(skill, dict) else ""),
            "cost": getattr(skill, "manacost", skill.get("cost") if isinstance(skill, dict) else "") or "",
            "density": getattr(skill, "concentration", skill.get("density") if isinstance(skill, dict) else "") or "",
            "rarity": getattr(skill, "rarity", skill.get("rarity") if isinstance(skill, dict) else "") or "",
            "preacttime": getattr(skill, "preacttime", skill.get("preacttime") if isinstance(skill, dict) else "") or "",
            "finishtime": getattr(skill, "finishtime", skill.get("finishtime") if isinstance(skill, dict) else "") or "",
            "desc": getattr(skill, "description", skill.get("description") if isinstance(skill, dict) else "") or "",
        }

        fields = DEBUG_FIELDS.get("skill", [])
        dlg = DebugEditDialog(self, "编辑技能", fields, values=cur)
        from PyQt6.QtWidgets import QDialog, QMessageBox

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        new = dlg.get_result()
        try:
            if isinstance(skill, dict):
                skill["name"] = new.get("name", skill.get("name"))
                skill["element"] = new.get("element", skill.get("element"))
                skill["cost"] = new.get("cost", skill.get("cost"))
                skill["density"] = new.get("density", skill.get("density"))
                skill["rarity"] = new.get("rarity", skill.get("rarity"))
                skill["preacttime"] = new.get("preacttime", skill.get("preacttime"))
                skill["finishtime"] = new.get("finishtime", skill.get("finishtime"))
                skill["description"] = new.get("desc", skill.get("description"))
            else:
                setattr(skill, "name", new.get("name", getattr(skill, "name", "")))
                setattr(skill, "element", new.get("element", getattr(skill, "element", "")))
                setattr(skill, "manacost", new.get("cost", getattr(skill, "manacost", 0)))
                setattr(skill, "concentration", new.get("density", getattr(skill, "concentration", 0)))
                setattr(skill, "rarity", new.get("rarity", getattr(skill, "rarity", "")))
                setattr(skill, "preacttime", new.get("preacttime", getattr(skill, "preacttime", 1.0)))
                setattr(skill, "finishtime", new.get("finishtime", getattr(skill, "finishtime", 1.0)))
                setattr(skill, "description", new.get("desc", getattr(skill, "description", "")))
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存技能失败: {e}")
        self._debug_ctx.update_ui_display()

    def _debug_delete_skill(self, index: int) -> None:
        if not debug_enabled() or self._debug_ctx is None:
            return

        skills = getattr(self._debug_ctx.player_data, "skills", []) or []
        if index < 0 or index >= len(skills):
            return

        from PyQt6.QtWidgets import QMessageBox

        if (
            QMessageBox.question(self, "删除技能", "确认删除该技能？", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            != QMessageBox.StandardButton.Yes
        ):
            return
        del skills[index]
        self._debug_ctx.player_data.skills = skills
        self._debug_ctx.update_ui_display()
