from PyQt6.QtWidgets import QMessageBox
from src.saves import get_all_saves, load_save_data, delete_save_file
from src.GUI.QtComponents.base.base_ui import BaseUI
from src.GUI.QtComponents.common_ui_utils import CommonUIUtils
from src.GUI.QtComponents.save_select_components import (SaveSelectHeaderComponent,SaveListComponent,SaveSelectActionsComponent)
from src.Constants.ui_constants import UI_TEXTS

class SaveSelectQt(BaseUI):
    def __init__(self, app_window):
        super().__init__(app_window)
        # 复用共享夜空背景（层级相同则不重建）
        self._background = self.app_window.get_shared_night_sky_background(fps=60)
        self.set_background(self._background)
        # 设置UI布局
        self.saves = []
        self.list_component = SaveListComponent(self._enter_selected)
        self.setObjectName("SaveSelectRoot")
        # 使用通用布局工具
        layout = CommonUIUtils.create_vertical_layout([SaveSelectHeaderComponent(),self.list_component,SaveSelectActionsComponent(on_enter=self._enter_selected,on_create=self.app_window.show_create_world,on_delete=self._delete_selected,on_back=self.app_window.show_main_menu)], margins=(20, 20, 20, 20), spacing=8)
        self.setLayout(layout)
        self.refresh_list()
        self._apply_theme()
    def refresh_list(self):
        self.saves = get_all_saves()
        self.list_component.set_saves(self.saves)
    def _selected_index(self):
        return self.list_component.selected_index if isinstance(self.list_component.selected_index, int) else None
    def _enter_selected(self, *_):
        idx = self.get_idx()
        if idx is None:
            return
        save_info = self.saves[idx]
        full_data = load_save_data(save_info['filename'],confirm_load_backup=lambda title, msg: QMessageBox.question(self,title,msg,QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,QMessageBox.StandardButton.No,)== QMessageBox.StandardButton.Yes,on_info=lambda title, msg: QMessageBox.information(self, title, msg),on_warning=lambda title, msg: QMessageBox.warning(self, title, msg),on_error=lambda title, msg: QMessageBox.critical(self, title, msg),)
        if not full_data:
            return
        self.app_window.show_game_screen(save_info['filename'], full_data)
    def _delete_selected(self):
        idx = self.get_idx()
        if idx is None:
            return
        save_info = self.saves[idx]
        world_name = save_info.get('world_name', save_info.get('name', '未知世界'))
        ok = QMessageBox.question(self, UI_TEXTS["save_select"]["confirm_delete"], UI_TEXTS["save_select"]["delete_save_prompt"].format(world_name=world_name))
        if ok == QMessageBox.StandardButton.Yes:
            delete_save_file(save_info['filename'])
            self.refresh_list()
    def get_idx(self) -> int | None:
        idx = self._selected_index()
        if idx is None:
            QMessageBox.warning(self, UI_TEXTS["save_select"]["warning"], UI_TEXTS["save_select"]["select_save_first"])
            return None
        return idx