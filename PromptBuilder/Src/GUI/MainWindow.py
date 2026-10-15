import sys
import os
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QVBoxLayout, QWidget, QMessageBox,
    QFileDialog, QMenuBar, QMenu, QStatusBar, QApplication
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QKeySequence, QAction

from ..Logic.Config import ConfigManager
from ..Logic.DataManager import DataManager
from .Tabs.SystemTab import SystemTab
from .Tabs.OpeningTab import OpeningTab
from .Tabs.SkillsTab import SkillsTab
from .Tabs.TestTab import TestTab
from .SettingsDialog import SettingsDialog
from src.utils.logger import logger
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Initialize config and data managers
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.json")
        self.config_manager = ConfigManager(config_path)

        # Set theme
        theme = self.config_manager.config.get("theme", "cosmo")
        self._apply_theme(theme)

        self.setWindowTitle("乌有乡游记 - (LZN)提示词调试器")
        self.setGeometry(100, 100, 1400, 1000)

        self.data_manager = DataManager()
        self.data_manager.on_dirty_change = self._on_dirty_change

        self._init_menu()
        self._init_status_bar()
        self._init_layout()
        self._bind_shortcuts()

        # Load default file if exists
        default_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "Assets", "data", "prompts.json")
        if os.path.exists(default_path):
            try:
                self.data_manager.load_file(default_path)
                self._refresh_all_tabs()
                self._update_title()
            except Exception as e:
                logger.error(f"读取失败: {e}")

    def _apply_theme(self, theme_name):
        """Apply theme - for now just set window properties, theme_manager integration can be added later"""
        if theme_name == "darkly":
            # Dark theme
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QLabel {
                    background-color: transparent;
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #374151;
                    color: #ffffff;
                    border: 1px solid #444444;
                    border-radius: 6px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #4b5563;
                }
                QLineEdit, QTextEdit, QSpinBox, QComboBox {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    border: 1px solid #444444;
                    border-radius: 8px;
                    padding: 6px;
                }
                QListWidget, QListView {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    border: 1px solid #444444;
                    border-radius: 8px;
                }
                QMenu {
                    background-color: #1e1e1e;
                    color: #ffffff;
                    border: 1px solid #444444;
                    border-radius: 8px;
                }
                QMenu::item:selected {
                    background-color: #374151;
                }
                QTabWidget::pane {
                    border: 1px solid #444444;
                    background-color: #2b2b2b;
                }
                QTabBar::tab {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    padding: 8px 16px;
                    border: 1px solid #444444;
                }
                QTabBar::tab:selected {
                    background-color: #4c4c4c;
                }
                QScrollArea {
                    background-color: #2b2b2b;
                    border: none;
                }
                QFrame {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
            """)
        else:
            # Light theme (cosmo)
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #ffffff;
                    color: #000000;
                }
                QWidget {
                    background-color: #ffffff;
                    color: #000000;
                }
                QLabel {
                    background-color: transparent;
                    color: #000000;
                }
            """)

    def _init_menu(self):
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("文件")

        open_action = QAction("打开 JSON...", self)
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)

        save_action = QAction("保存", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("另存为...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.show_settings)
        file_menu.addAction(settings_action)

        file_menu.addSeparator()

        exit_action = QAction("退出", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.on_exit)
        file_menu.addAction(exit_action)

        # Help Menu
        help_menu = menubar.addMenu("帮助")

        help_action = QAction("使用帮助", self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)

        about_action = QAction("关于研发", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

        # Theme Menu
        theme_menu = menubar.addMenu("主题")

        dark_theme_action = QAction("深色模式 (Darkly)", self)
        dark_theme_action.triggered.connect(lambda: self.change_theme("darkly"))
        theme_menu.addAction(dark_theme_action)

        light_theme_action = QAction("浅色模式 (Cosmo)", self)
        light_theme_action.triggered.connect(lambda: self.change_theme("cosmo"))
        theme_menu.addAction(light_theme_action)

    def change_theme(self, theme_name):
        self._apply_theme(theme_name)
        self.config_manager.config["theme"] = theme_name
        self.config_manager.save_config()

    def _init_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")

    def _init_layout(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        self.tab_system = SystemTab(self.data_manager)
        self.tab_widget.addTab(self.tab_system, "[系统提示词]")

        self.tab_opening = OpeningTab(self.data_manager)
        self.tab_widget.addTab(self.tab_opening, "[开场白模板]")

        self.tab_skills = SkillsTab(self.data_manager)
        self.tab_widget.addTab(self.tab_skills, "[技能列表]")

        self.tab_test = TestTab(self.data_manager)
        self.tab_widget.addTab(self.tab_test, "[测试生成]")

        # Connect tab change signal
        self.tab_widget.currentChanged.connect(self._on_tab_changed)

    def _bind_shortcuts(self):
        # Shortcuts are already set in menu actions
        # Additional global shortcuts can be added here if needed
        pass

    def _on_dirty_change(self, is_dirty):
        self._update_title()

    def _update_title(self):
        title = "乌有乡游记 - (LZN)提示词调试器"
        if self.data_manager.current_file_path:
            title += f" - {os.path.basename(self.data_manager.current_file_path)}"

        if self.data_manager.is_dirty:
            title += " *"

        self.setWindowTitle(title)

    def _on_tab_changed(self, index):
        # Refresh current tab if needed
        pass

    def _refresh_all_tabs(self):
        self.tab_system.refresh()
        self.tab_opening.refresh()
        self.tab_skills.refresh()
        # Test tab doesn't need refresh, it pulls from data manager on generate

    def open_file_dialog(self):
        if not self.check_unsaved_changes():
            return

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择 prompts.json",
            "",
            "JSON Files (*.json);;All Files (*.*)"
        )
        if file_path:
            try:
                self.data_manager.load_file(file_path)
                self._refresh_all_tabs()
                self._update_title()
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载失败: {e}")

    def save_file(self):
        if not self.data_manager.current_file_path:
            self.save_file_as()
        else:
            try:
                self.data_manager.save_file()
                self._update_title()
                QMessageBox.information(self, "成功", "文件已保存")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {e}")

    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "另存为 JSON",
            "",
            "JSON Files (*.json)"
        )
        if file_path:
            try:
                self.data_manager.save_file(file_path)
                self._update_title()
                QMessageBox.information(self, "成功", "文件已另存")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败: {e}")

    def show_settings(self):
        dialog = SettingsDialog(self, self.config_manager)
        dialog.exec()
        # Re-bind shortcuts after settings close might be needed if we want immediate effect
        self._bind_shortcuts()

    def show_help(self):
        msg = """
        【快捷键】
        保存: Ctrl+S (默认)
        另存为: Ctrl+Shift+S (默认)
        撤销: Ctrl+Z
        重做: Ctrl+Y

        【功能说明】
        1. 系统提示词：管理 System Prompt 的各个模块。
        2. 开场白模板：编辑用于生成开场白的 Prompt 模板。
        3. 技能列表：编辑 JSON 格式的技能数据。
        4. 测试生成：随机生成角色并测试 AI 回复。
        """
        QMessageBox.information(self, "使用帮助", msg)

    def show_about(self):
        msg = "乌有乡游记 - 提示词调试器\n版本: v2.0\n\n研发: LZN"
        QMessageBox.information(self, "关于研发", msg)

    def check_unsaved_changes(self):
        if self.data_manager.is_dirty:
            reply = QMessageBox.question(
                self,
                "未保存的更改",
                "您有未保存的更改，是否保存？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Cancel:
                return False
            elif reply == QMessageBox.StandardButton.Yes:
                self.save_file()
                return True
            else:  # No
                return True
        return True

    def closeEvent(self, event):
        if self.check_unsaved_changes():
            event.accept()
        else:
            event.ignore()

    def on_exit(self):
        self.close()
