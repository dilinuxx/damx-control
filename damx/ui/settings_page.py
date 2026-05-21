# settings_page.py

import subprocess

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton
)


class SettingsPage(QWidget):
    """
    Settings / system info page.
    Full class conversion preserving
    original functionality.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        # -----------------------
        # TEXT DISPLAY
        # -----------------------
        self.log = QTextEdit()

        self.log.setReadOnly(True)

        self.log.setStyleSheet("""
            QTextEdit{
                background-color:#1e2a38;
                color:white;
                font-size:14px;
                border-radius:6px;
                padding:8px;
            }
        """)

        layout.addWidget(self.log)

        # -----------------------
        # BUTTONS
        # -----------------------
        button_layout = QHBoxLayout()

        self.refresh_btn = QPushButton(
            "Refresh Network Info"
        )

        self.refresh_btn.clicked.connect(
            self.refresh_network_info
        )

        button_layout.addWidget(
            self.refresh_btn
        )

        layout.addLayout(button_layout)

        # Initial load
        self._load_network_info()

    # -----------------------
    # LOAD NETWORK INFO
    # -----------------------
    def _load_network_info(self):

        try:

            hostname = subprocess.check_output(
                ["hostname"],
                text=True
            ).strip()

            result = subprocess.run(
                ["hostname", "-I"],
                capture_output=True,
                text=True
            )

            ips = result.stdout.strip()

            network_text = f"""
Hostname:
{hostname}

IP Addresses:
{ips if ips else 'No IP addresses found'}
"""

            self.log.setText(network_text)

        except Exception as e:

            self.log.setText(
                f"Error getting network info:\n{e}"
            )

    # -----------------------
    # REFRESH
    # -----------------------
    def refresh_network_info(self):

        self._load_network_info()