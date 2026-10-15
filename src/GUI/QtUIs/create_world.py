from PyQt6.QtWidgets import QMessageBox
from src.AI.prompts import OPENING_PROMPT_TEMPLATE
from src.saves import create_new_save_file, load_save_data
from src.GUI.QtComponents.create_world_components import CreateWorldHeaderComponent,CreateWorldFormComponent,CreateWorldActionsComponent
from src.GUI.QtComponents.base.base_ui import BaseUI
from src.GUI.QtComponents.common_ui_utils import CommonUIUtils
from src.Constants.ui_constants import UI_TEXTS
import random
class CreateWorldQt(BaseUI):
    def __init__(self, app_window):
        super().__init__(app_window)
        self.app_window = app_window
        # 复用共享夜空背景（层级相同则不重建）
        self._background = self.app_window.get_shared_night_sky_background(fps=60)
        self.set_background(self._background)
        self.setObjectName("CreateWorldRoot")
        # 使用通用布局工具
        self.form_component = CreateWorldFormComponent()
        layout = CommonUIUtils.create_vertical_layout([CreateWorldHeaderComponent(),self.form_component,CreateWorldActionsComponent(on_create=self._create_world,on_cancel=self.app_window.show_save_select,)], margins=(20, 20, 20, 20), spacing=8)
        self.setLayout(layout)
        self._apply_theme()
    def _create_world(self):
        # 验证表单
        if not getattr(self, 'form_component', None) or not self.form_component.validate():
            QMessageBox.critical(self, UI_TEXTS["create_world"]["error"], UI_TEXTS["create_world"]["fill_required_fields"])
            return
        world_name = self.form_component.world_name.text().strip()
        player_name = self.form_component.player_name.text().strip()
        race = self.form_component.race.currentText()
        magic_str = self.form_component.magic.currentText()
        birthplace = self.form_component.birthplace.currentText()
        magic_density = "15%"
        if "低" in magic_str:
            magic_density = random.randint(1, 25).__str__() + "%"
        elif "一般" in magic_str:
            magic_density = random.randint(25, 50).__str__() + "%"
        elif "高" in magic_str:
            magic_density = random.randint(50, 85).__str__() + "%"
        elif "极高" in magic_str:
            magic_density = random.randint(85, 100).__str__() + "%"
        custom_opening = OPENING_PROMPT_TEMPLATE.format(birthplace=birthplace,player_name=player_name,race=race,magic_density=magic_density,)
        history = [{"role": "user", "content": custom_opening}]
        filename = create_new_save_file(world_name,player_name,history,location=f"{birthplace}",magic_density=magic_density,)
        full_data = load_save_data(filename,confirm_load_backup=lambda title, msg: QMessageBox.question(self,title,msg,QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,QMessageBox.StandardButton.No,)== QMessageBox.StandardButton.Yes,on_info=lambda title, msg: QMessageBox.information(self, title, msg),on_warning=lambda title, msg: QMessageBox.warning(self, title, msg),on_error=lambda title, msg: QMessageBox.critical(self, title, msg))
        self.app_window.show_game_screen(filename, full_data)