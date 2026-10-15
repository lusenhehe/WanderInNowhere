from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QHeaderView, QPushButton, QFileDialog, QMessageBox, QInputDialog,
    QLineEdit, QTextEdit, QDialog, QDialogButtonBox, QLabel,
    QFormLayout, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import csv
import json
from src.GUI.CustomWidgets.custom_combo_box import CustomComboBox

class SkillsTab(QWidget):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.columns = ["name", "element", "cost", "density", "rarity", "preacttime", "finishtime", "description"]
        self.col_names = ["名称", "元素", "消耗", "浓度", "稀有度", "前摇(s)", "后摇(s)", "描述"]
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QHBoxLayout()

        add_btn = QPushButton("添加技能")
        add_btn.clicked.connect(self.add_skill)
        toolbar.addWidget(add_btn)

        delete_btn = QPushButton("删除技能")
        delete_btn.clicked.connect(self.delete_skill)
        toolbar.addWidget(delete_btn)

        edit_btn = QPushButton("编辑技能")
        edit_btn.clicked.connect(self.edit_skill)
        toolbar.addWidget(edit_btn)

        toolbar.addStretch()

        import_btn = QPushButton("导入 CSV")
        import_btn.clicked.connect(self.import_csv)
        toolbar.addWidget(import_btn)

        export_btn = QPushButton("导出 CSV")
        export_btn.clicked.connect(self.export_csv)
        toolbar.addWidget(export_btn)

        layout.addLayout(toolbar)

        # Table
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(self.col_names)
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.tree.itemDoubleClicked.connect(self._on_item_double_clicked)

        # Set column widths
        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # element
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # cost
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # density
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # rarity
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # preacttime
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # finishtime
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)  # description

        layout.addWidget(self.tree)

    def _on_item_double_clicked(self, item, column):
        self.edit_skill()

    def refresh(self):
        self.tree.clear()
        skills = self.data_manager.data.get("skills", [])
        for skill in skills:
            item = QTreeWidgetItem()
            for i, col in enumerate(self.columns):
                value = skill.get(col, "")
                item.setText(i, str(value))
            self.tree.addTopLevelItem(item)

    def _get_current_skills(self):
        skills = []
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            skill = {}
            for j, col in enumerate(self.columns):
                skill[col] = item.text(j)
            skills.append(skill)
        return skills

    def _save_to_manager(self):
        skills = self._get_current_skills()
        self.data_manager.update_skills(skills)

    def add_skill(self):
        dialog = SkillEditDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data:
                item = QTreeWidgetItem()
                for i, col in enumerate(self.columns):
                    value = data.get(col, "")
                    item.setText(i, str(value))
                self.tree.addTopLevelItem(item)
                self._save_to_manager()

    def edit_skill(self):
        current_item = self.tree.currentItem()
        if not current_item:
            return

        # Get current data
        data = {}
        for i, col in enumerate(self.columns):
            data[col] = current_item.text(i)

        dialog = SkillEditDialog(self, data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_data = dialog.get_data()
            if new_data:
                for i, col in enumerate(self.columns):
                    value = new_data.get(col, "")
                    current_item.setText(i, str(value))
                self._save_to_manager()

    def delete_skill(self):
        current_item = self.tree.currentItem()
        if not current_item:
            return

        reply = QMessageBox.question(
            self, "确认",
            "确定删除选中的技能吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            index = self.tree.indexOfTopLevelItem(current_item)
            self.tree.takeTopLevelItem(index)
            self._save_to_manager()

    def import_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 CSV 文件", "", "CSV Files (*.csv);;All Files (*.*)"
        )
        if not file_path:
            return

        try:
            skills = []
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    skill = {
                        "name": row.get("name", ""),
                        "element": row.get("element", ""),
                        "cost": row.get("cost", ""),
                        "density": row.get("density", ""),
                        "rarity": row.get("rarity", "普通"),
                        "preacttime": row.get("preacttime", "1.0"),
                        "finishtime": row.get("finishtime", "1.0"),
                        "description": row.get("description", "")
                    }
                    skills.append(skill)

            self.data_manager.update_skills(skills)
            self.refresh()
            QMessageBox.information(self, "成功", f"成功导入 {len(skills)} 个技能")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导入失败: {e}")

    def export_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存 CSV 文件", "", "CSV Files (*.csv)"
        )
        if not file_path:
            return

        try:
            skills = self._get_current_skills()
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.columns)
                writer.writeheader()
                writer.writerows(skills)
            QMessageBox.information(self, "成功", "导出成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {e}")


class SkillEditDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("编辑技能" if data else "添加技能")
        self.setModal(True)
        self.data = data or {}
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        form_layout = QFormLayout(scroll_widget)

        self.fields = {}

        # Name
        name_edit = QLineEdit(self.data.get("name", ""))
        form_layout.addRow("名称:", name_edit)
        self.fields["name"] = name_edit

        # Element
        element_edit = QLineEdit(self.data.get("element", ""))
        form_layout.addRow("元素:", element_edit)
        self.fields["element"] = element_edit

        # Cost
        cost_edit = QLineEdit(self.data.get("cost", ""))
        form_layout.addRow("消耗:", cost_edit)
        self.fields["cost"] = cost_edit

        # Density
        density_edit = QLineEdit(self.data.get("density", ""))
        form_layout.addRow("浓度:", density_edit)
        self.fields["density"] = density_edit

        # Rarity
        rarity_combo = CustomComboBox()
        rarity_combo.addItems(["普通", "稀有", "传奇", "水晶"])
        rarity_combo.setCurrentText(self.data.get("rarity", "普通"))
        form_layout.addRow("稀有度:", rarity_combo)
        self.fields["rarity"] = rarity_combo

        # Preact time
        preact_edit = QLineEdit(self.data.get("preacttime", "1.0"))
        form_layout.addRow("前摇(s):", preact_edit)
        self.fields["preacttime"] = preact_edit

        # Finish time
        finish_edit = QLineEdit(self.data.get("finishtime", "1.0"))
        form_layout.addRow("后摇(s):", finish_edit)
        self.fields["finishtime"] = finish_edit

        # Description
        desc_edit = QTextEdit()
        desc_edit.setPlainText(self.data.get("description", ""))
        desc_edit.setMaximumHeight(100)
        form_layout.addRow("描述:", desc_edit)
        self.fields["description"] = desc_edit

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_data(self):
        return {
            "name": self.fields["name"].text(),
            "element": self.fields["element"].text(),
            "cost": self.fields["cost"].text(),
            "density": self.fields["density"].text(),
            "rarity": self.fields["rarity"].currentText(),
            "preacttime": self.fields["preacttime"].text(),
            "finishtime": self.fields["finishtime"].text(),
            "description": self.fields["description"].toPlainText()
        }
