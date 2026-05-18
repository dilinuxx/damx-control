from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt


class CameraPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        self.label = QLabel("Camera Feed")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet(
            "background:black; color:white; font-size:20px;"
        )

        layout.addWidget(self.label)