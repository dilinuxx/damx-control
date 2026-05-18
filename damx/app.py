__version__ = "2.0"

import sys
from PyQt5.QtWidgets import (QApplication)
from ui.main_window import DAMXUI

# ----------------------
# MAIN
# ----------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DAMXUI()
    window.show()
    sys.exit(app.exec_())