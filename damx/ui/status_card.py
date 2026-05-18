from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt


class StatusCard(QFrame):
    """
    Reusable dashboard card used across pages.
    Example usage:
        card = StatusCard("Temperature")
        card.set_value("25 °C")
    """

    def __init__(self, title: str):
        super().__init__()

        self.setStyleSheet("""
        QFrame{
            background:#f2f4f7;
            border:1px solid #d0d7e2;
            border-radius:8px;
        }
        """)
        layout = QVBoxLayout(self)
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size:16px;font-weight:bold")
        self.value = QLabel("--")
        self.value.setAlignment(Qt.AlignCenter)
        self.value.setStyleSheet("font-size:28px;color:#1a73e8")
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(self.value)
        layout.addStretch()

    # Public API used by pages
    def set_value(self, text):
        self.value.setText(str(text))