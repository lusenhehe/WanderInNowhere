from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QTextEdit, QSplitter, QGroupBox, QPushButton,
    QLabel, QScrollArea, QFrame, QInputDialog, QMessageBox,
    QLineEdit, QDialog, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QKeySequence, QShortcut
from src.GUI.CustomWidgets.custom_combo_box import CustomComboBox

class SystemTab(QWidget):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.current_part_key = None

        # Order for system prompt parts
        self.part_order = [
            "最高指令",
            "AI角色设定",
            "世界观设置",
            "开场白指令",
            "绝对禁区",
            "叙述规则",
            "战斗规则",
            "生存系统",
            "状态与物品跟踪",
            "输出格式",
            "错误规避"
        ]

        self.undo_stack = []
        self.redo_stack = []

        self._init_ui()
        self._bind_shortcuts()

    def _bind_shortcuts(self):
        # Find/Replace shortcut
        find_shortcut = QShortcut(QKeySequence.StandardKey.Find, self)
        find_shortcut.activated.connect(self._show_find_replace)

        replace_shortcut = QShortcut(QKeySequence("Ctrl+H"), self)
        replace_shortcut.activated.connect(self._show_find_replace)

    def _show_find_replace(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("查找/替换")
        dialog.setGeometry(300, 300, 350, 150)

        layout = QVBoxLayout(dialog)

        # Find
        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel("查找内容:"))
        self.find_entry = QLineEdit()
        find_layout.addWidget(self.find_entry)
        layout.addLayout(find_layout)

        # Replace
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel("替换为:"))
        self.replace_entry = QLineEdit()
        replace_layout.addWidget(self.replace_entry)
        layout.addLayout(replace_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        find_next_btn = QPushButton("查找下一个")
        find_next_btn.clicked.connect(self._find_next)
        btn_layout.addWidget(find_next_btn)

        replace_btn = QPushButton("替换")
        replace_btn.clicked.connect(self._replace)
        btn_layout.addWidget(replace_btn)

        replace_all_btn = QPushButton("全部替换")
        replace_all_btn.clicked.connect(self._replace_all)
        btn_layout.addWidget(replace_all_btn)

        layout.addLayout(btn_layout)

        dialog.exec()

    def _find_next(self):
        target = self.find_entry.text()
        if not target:
            return

        cursor = self.part_text.textCursor()
        if cursor.hasSelection():
            cursor.setPosition(cursor.selectionEnd())

        found = self.part_text.find(target)
        if not found:
            # Wrap around
            cursor.movePosition(cursor.MoveOperation.Start)
            self.part_text.setTextCursor(cursor)
            found = self.part_text.find(target)
            if not found:
                QMessageBox.information(self, "提示", "未找到内容")

    def _replace(self):
        if self.part_text.textCursor().hasSelection():
            self.part_text.textCursor().removeSelectedText()
            self.part_text.insertPlainText(self.replace_entry.text())
            self._find_next()

    def _replace_all(self):
        target = self.find_entry.text()
        replacement = self.replace_entry.text()
        if not target:
            return

        cursor = self.part_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        self.part_text.setTextCursor(cursor)

        count = 0
        while self.part_text.find(target):
            self.part_text.textCursor().removeSelectedText()
            self.part_text.insertPlainText(replacement)
            count += 1

        QMessageBox.information(self, "完成", f"已替换 {count} 处")

    def _init_ui(self):
        main_layout = QHBoxLayout(self)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # 1. Left: List of parts and presets
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        # Preset Area
        preset_group = QGroupBox("预设快照 (Presets)")
        preset_layout = QVBoxLayout(preset_group)

        self.cb_presets = CustomComboBox()
        preset_layout.addWidget(self.cb_presets)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_preset)
        btn_layout.addWidget(save_btn)

        load_btn = QPushButton("加载")
        load_btn.clicked.connect(self.load_preset)
        btn_layout.addWidget(load_btn)

        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(self.delete_preset)
        btn_layout.addWidget(delete_btn)

        preset_layout.addLayout(btn_layout)
        left_layout.addWidget(preset_group)

        # Toolbar for Listbox
        toolbar_layout = QHBoxLayout()
        toolbar_layout.addWidget(QLabel("提示词模块列表"))

        add_btn = QPushButton("添加")
        add_btn.clicked.connect(self.add_module)
        toolbar_layout.addWidget(add_btn)

        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(self.delete_module)
        toolbar_layout.addWidget(delete_btn)

        left_layout.addLayout(toolbar_layout)

        self.parts_listbox = QListWidget()
        self.parts_listbox.itemSelectionChanged.connect(self._on_part_selected)
        left_layout.addWidget(self.parts_listbox)

        splitter.addWidget(left_widget)

        # 2. Middle: Editor
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)

        self.part_label = QLabel("编辑内容")
        editor_layout.addWidget(self.part_label)

        self.part_text = QTextEdit()
        self.part_text.setFont(QFont("Consolas", 10))
        self.part_text.textChanged.connect(self._on_text_modified)
        editor_layout.addWidget(self.part_text)

        # Token Counter Bar
        self.status_bar = QFrame()
        status_layout = QHBoxLayout(self.status_bar)
        status_layout.addStretch()
        self.token_label = QLabel("Token 估算: 0")
        self.token_label.setStyleSheet("color: gray; font-size: 9pt;")
        status_layout.addWidget(self.token_label)
        editor_layout.addWidget(self.status_bar)

        splitter.addWidget(editor_widget)

        # 3. Right: Live Preview
        preview_group = QGroupBox("实时预览 (Live Preview)")
        preview_layout = QVBoxLayout(preview_group)

        self.preview_text = QTextEdit()
        self.preview_text.setFont(QFont("Consolas", 8))
        self.preview_text.setReadOnly(True)
        self.preview_text.setStyleSheet("background-color: #f0f0f0;")
        preview_layout.addWidget(self.preview_text)

        splitter.addWidget(preview_group)

        # Set splitter proportions
        splitter.setSizes([200, 400, 300])

    def _update_preview(self):
        # Construct full prompt
        parts = self.data_manager.data.get("system_prompt_parts", {})
        full_prompt = ""

        # Use the same logic as TestTab to construct prompt
        header_map = {
            "最高指令": "【最高指令】",
            "AI角色设定": "【核心定位】",
            "世界观设置": "【世界设定（强制遵循）】",
            "开场白指令": "【初始化指令（游戏开始时强制执行）】",
            "绝对禁区": "【绝对禁区：操控玩家（God-Modding）】",
            "叙述规则": "【叙述规则（严格执行）】",
            "战斗规则": "【战斗与冲突（硬核模式）】",
            "生存系统": "【生存系统（时间/天气/饥饿）】",
            "状态与物品跟踪": "【生存系统（强制执行）】",
            "输出格式": "【输出格式】",
            "错误规避": "【错误规避（补充强化・极致硬核探索导向）】"
        }

        for key in self.part_order:
            if key in parts:
                header = header_map.get(key, f"【{key}】")
                full_prompt += f"{header}\n{parts[key]}\n\n"

        # Add extra parts
        for key in parts:
            if key not in self.part_order:
                full_prompt += f"【{key}】\n{parts[key]}\n\n"

        # Update Preview Text
        self.preview_text.setPlainText(full_prompt)

        # Update Token Count
        char_count = len(full_prompt)
        est_tokens = int(char_count * 0.7)
        self.token_label.setText(f"字符数: {char_count} | 预估 Token: ~{est_tokens}")

    def _on_text_modified(self):
        self._save_current_part()
        self._update_preview()

    def refresh(self):
        self.parts_listbox.clear()
        parts = self.data_manager.data.get("system_prompt_parts", {})

        display_keys = [k for k in self.part_order if k in parts]
        extra_keys = [k for k in parts.keys() if k not in self.part_order]
        self.all_part_keys = display_keys + extra_keys

        for key in self.all_part_keys:
            self.parts_listbox.addItem(key)

        self.part_text.clear()
        self.current_part_key = None
        self._update_preview()
        self._refresh_presets()

    def _refresh_presets(self):
        presets = self.data_manager.data.get("presets", {})
        self.cb_presets.clear()
        self.cb_presets.addItems(presets.keys())
        if presets:
            self.cb_presets.setCurrentIndex(0)

    def _on_part_selected(self):
        current_item = self.parts_listbox.currentItem()
        if not current_item:
            return

        # Save previous if needed
        self._save_current_part()

        key = current_item.text()
        self.current_part_key = key

        content = self.data_manager.data.get("system_prompt_parts", {}).get(key, "")

        self.part_text.setPlainText(content)
        self.part_label.setText(f"编辑: {key}")

    def _save_current_part(self):
        if self.current_part_key:
            content = self.part_text.toPlainText().strip()
            self.data_manager.update_part(self.current_part_key, content)

    def add_module(self):
        key, ok = QInputDialog.getText(self, "添加模块", "请输入新模块的 Key (英文):")
        if ok and key:
            key = key.strip()
            if self.data_manager.add_part(key):
                # Push to undo stack: ("add", key, content="")
                self.undo_stack.append(("add", key, ""))
                self.redo_stack.clear()

                self.refresh()
                # Select new
                items = self.parts_listbox.findItems(key, Qt.MatchFlag.MatchExactly)
                if items:
                    self.parts_listbox.setCurrentItem(items[0])
            else:
                QMessageBox.critical(self, "错误", "该模块已存在！")

    def delete_module(self):
        current_item = self.parts_listbox.currentItem()
        if not current_item:
            QMessageBox.warning(self, "提示", "请先选择要删除的模块")
            return

        key = current_item.text()
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除模块 '{key}' 吗？\n此操作不可撤销(可通过Ctrl+Z撤销)。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Save content before delete for undo
            content = self.data_manager.data.get("system_prompt_parts", {}).get(key, "")

            self.data_manager.delete_part(key)

            # Push to undo stack: ("delete", key, content)
            self.undo_stack.append(("delete", key, content))
            self.redo_stack.clear()

            self.refresh()

    def save_preset(self):
        name, ok = QInputDialog.getText(self, "保存预设", "请输入预设名称:")
        if ok and name:
            name = name.strip()
            if not name:
                return
            presets = self.data_manager.data.get("presets", {})
            if name in presets:
                reply = QMessageBox.question(
                    self, "覆盖确认",
                    f"预设 '{name}' 已存在，是否覆盖？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            self.data_manager.save_preset(name)
            self._refresh_presets()
            self.cb_presets.setCurrentText(name)
            QMessageBox.information(self, "成功", f"预设 '{name}' 已保存")

    def load_preset(self):
        name = self.cb_presets.currentText()
        if not name:
            QMessageBox.warning(self, "提示", "请选择要加载的预设")
            return

        reply = QMessageBox.question(
            self, "确认加载",
            f"加载预设 '{name}' 将覆盖当前的所有系统提示词设置，是否继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.data_manager.load_preset(name):
                self.refresh()
                self.cb_presets.setCurrentText(name)
                QMessageBox.information(self, "成功", f"预设 '{name}' 已加载")
            else:
                QMessageBox.critical(self, "错误", f"加载预设 '{name}' 失败")

    def delete_preset(self):
        name = self.cb_presets.currentText()
        if not name:
            QMessageBox.warning(self, "提示", "请选择要删除的预设")
            return

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除预设 '{name}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.data_manager.delete_preset(name):
                self._refresh_presets()
                QMessageBox.information(self, "成功", f"预设 '{name}' 已删除")
            else:
                QMessageBox.critical(self, "错误", f"删除预设 '{name}' 失败")
