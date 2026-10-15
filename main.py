import sys
sys.dont_write_bytecode = True
from src.utils import setup_logging
from PyQt6.QtWidgets import QApplication
from src.GUI.qt_gui import GameAppQt
if __name__ == "__main__":
    setup_logging()
    qapp = QApplication(sys.argv)
    window = GameAppQt()
    window.show()
    sys.exit(qapp.exec())