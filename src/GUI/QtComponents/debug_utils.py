from PyQt6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QFormLayout,QLabel,QLineEdit,QTextEdit,QPushButton,QWidget
from src.Constants.config import load_config
from src.GUI.CustomWidgets.custom_combo_box import CustomComboBox

class DebugEditDialog(QDialog):
    """Generic debug editor dialog driven by a `fields` specification.
    Fields format matches `Constants.debug_constants.DEBUG_FIELDS` entries.
    """

    def __init__(self, parent: QWidget | None, title: str, fields: list[dict], values: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self._fields = fields or []
        self._values = values or {}
        self._widgets = {}

        self._init_ui()

    def _init_ui(self):
        root = QVBoxLayout(self)
        form = QFormLayout()
        root.addLayout(form)

        for f in self._fields:
            key = f.get("key")
            label = f.get("label", key)
            wtype = f.get("type", "entry")
            default = f.get("default", "")

            if wtype == "entry":
                w = QLineEdit()
                w.setText(str(self._values.get(key, default)))
            elif wtype == "text":
                w = QTextEdit()
                w.setPlainText(str(self._values.get(key, default)))
                h = f.get("height", 4)
                w.setFixedHeight(int(h) * 24)
            elif wtype == "combo":
                w = CustomComboBox()
                for v in f.get("values", []):
                    w.addItem(str(v))
                val = self._values.get(key, default)
                if val is not None and str(val) in [str(w.itemText(i)) for i in range(w.count())]:
                    w.setCurrentText(str(val))
            else:
                w = QLineEdit()
                w.setText(str(self._values.get(key, default)))

            form.addRow(QLabel(label + ":"), w)
            self._widgets[key] = w

        btn_layout = QHBoxLayout()
        root.addLayout(btn_layout)
        btn_layout.addStretch(1)
        cancel = QPushButton("取消")
        ok = QPushButton("确定")
        cancel.clicked.connect(self.reject)
        ok.clicked.connect(self.accept)
        btn_layout.addWidget(cancel)
        btn_layout.addWidget(ok)

    def get_result(self) -> dict:
        data = {}
        for k, w in self._widgets.items():
            if isinstance(w, QTextEdit):
                data[k] = w.toPlainText()
            elif isinstance(w, CustomComboBox):
                data[k] = w.currentText()
            else:
                data[k] = w.text()
        return data
def debug_enabled() -> bool:
    return bool(load_config().get("debug", False))
def dump_widget_styles(widget, depth: int = 0, max_depth: int = 2) -> str:
    try:
        lines = []
        name = widget.objectName() or "<anon>"
        cls = widget.__class__.__name__
        ss = widget.styleSheet() or "(none)"
        indent = "  " * depth
        lines.append(f"{indent}{cls}#{name}: {ss}")
        if depth < max_depth:
            for child in widget.findChildren(QWidget):
                try:
                    lines.append(dump_widget_styles(child, depth + 1, max_depth))
                except Exception:
                    continue
        return "\n".join(lines)
    except Exception:
        return "(failed to dump styles)"
