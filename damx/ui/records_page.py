# records_page.py

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton
)

from datetime import datetime


class RecordsPage(QWidget):
    """
    System log / records page.
    Full conversion preserving runtime behaviour.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        # -----------------------
        # LOG WINDOW
        # -----------------------
        self.log = QTextEdit()

        self.log.setStyleSheet("""
            QTextEdit{
                background-color:#1e2a38;
                color:white;
                font-size:14px;
                border-radius:6px;
                padding:8px;
            }
        """)

        self.log.setText("System Log...\n")

        layout.addWidget(self.log)

        # -----------------------
        # BUTTONS
        # -----------------------
        button_layout = QHBoxLayout()

        self.clear_btn = QPushButton("Clear Logs")

        self.save_btn = QPushButton("Save Logs")

        self.clear_btn.clicked.connect(
            self.clear_logs
        )

        self.save_btn.clicked.connect(
            self.save_logs
        )

        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.save_btn)

        layout.addLayout(button_layout)

    # -----------------------
    # ADD LOG
    # -----------------------
    def add_log(self, message):

        timestamp = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        self.log.append(
            f"[{timestamp}] {message}"
        )

    # -----------------------
    # CLEAR LOGS
    # -----------------------
    def clear_logs(self):
        self.log.clear()

    # -----------------------
    # SAVE LOGS
    # -----------------------
    def save_logs(self):

        filename = "system_logs.txt"

        with open(filename, "w") as file:
            file.write(
                self.log.toPlainText()
            )

        self.add_log(
            f"Logs saved to {filename}"
        )