from __future__ import annotations
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QMessageBox

from src.saves import delete_save_file
from src.theme_manager import theme_manager
from src.Constants.ui_constants import UI_TEXTS
from .base_card import BaseCardQt

from src.GUI.CustomWidgets.custom_button import CustomButton

class SaveCardQt(BaseCardQt):
    def __init__(self,*,save_data: dict,index: int,on_select,on_double_click,parent: QWidget | None = None,):
        super().__init__(parent)
        self.save_data = save_data
        self.index = index
        self._on_select = on_select
        self._on_double_click = on_double_click

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("SaveCardQt")

        self._radius = 10

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)

        # 左侧区域：缩略图 + 主要信息
        thumb = QLabel()
        thumb.setObjectName("SaveCardThumb")
        thumb.setFixedSize(96, 64)
        layout.addWidget(thumb)

        left = QVBoxLayout()
        left.setSpacing(6)
        layout.addLayout(left, 1)

        world_name = save_data.get("world_name", save_data.get("name", "未知世界"))
        player_name = save_data.get("player_name", "未知角色")

        title = QLabel(str(world_name))
        title.setObjectName("SaveCardTitle")
        left.addWidget(title)

        subtitle = QLabel(f"角色: {player_name}  •  世界: {world_name}")
        subtitle.setObjectName("SaveCardSubtitle")
        subtitle.setProperty("role", "secondary")
        subtitle.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        left.addWidget(subtitle)

        status = save_data.get("status", {}) or {}
        location = save_data.get("location", "未知地点")
        world = save_data.get("world", {}) or {}
        hp = status.get("hp", "???")
        time_str = world.get("time", "")

        status_parts = [f"📍 {location}", f"❤ {hp}"]
        if time_str:
            status_parts.append(f"🕒 {time_str}")
        status_row = QLabel("  ".join(status_parts))
        status_row.setObjectName("SaveCardStatus")
        status_row.setProperty("role", "secondary")
        left.addWidget(status_row)

        #  右侧区域：最后游玩时间 + 操作按钮
        right_box = QVBoxLayout()
        right_box.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        layout.addLayout(right_box)

        last_played = save_data.get("last_played", "")
        last = QLabel(str(last_played))
        last.setObjectName("SaveCardLast")
        last.setProperty("role", "secondary")
        last.setAlignment(Qt.AlignmentFlag.AlignRight)
        right_box.addWidget(last)

        action_widget = QWidget()
        action_row = QHBoxLayout(action_widget)
        action_row.setContentsMargins(0, 0, 0, 0)
        action_row.setSpacing(6)

        load_btn = CustomButton("加载")
        load_btn.setMinimumWidth(84)
        load_btn.clicked.connect(lambda *_: (self._on_double_click() if callable(self._on_double_click) else None))
        del_btn = CustomButton("删除")
        del_btn.clicked.connect(self._delete_clicked)
        action_row.addWidget(load_btn)
        action_row.addWidget(del_btn)
        action_widget.setVisible(False)
        right_box.addWidget(action_widget)

        self._action_widget = action_widget
        self._thumb = thumb

        self._update_style()

    def on_hover_changed(self, hovered: bool) -> None:
        self._action_widget.setVisible(bool(hovered))

    def mousePressEvent(self, _ev):
        if callable(self._on_select):
            self._on_select(self.index)

    def mouseDoubleClickEvent(self, _ev):
        if callable(self._on_select):
            self._on_select(self.index)
        if callable(self._on_double_click):
            self._on_double_click()

    def _delete_clicked(self):
        world_name = self.save_data.get("world_name", self.save_data.get("name", "未知世界"))
        ok = QMessageBox.question(self, UI_TEXTS["save_select"]["confirm_delete"], UI_TEXTS["save_select"]["delete_save_prompt"].format(world_name=world_name))
        if ok != QMessageBox.StandardButton.Yes:
            return
        try:
            delete_save_file(self.save_data["filename"])
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除失败: {e}")
            return

        p = self.parent()
        while p is not None and not hasattr(p, "refresh_list"):
            p = p.parent()
        if p is not None:
            try:
                p.refresh_list()
            except Exception:
                pass
