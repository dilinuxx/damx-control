import subprocess
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit


class SettingsPage(QWidget):
    """
    Settings / system info page.
    Converted from create_settings_page().
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        self._load_network_info()

    # -----------------------
    # NETWORK INFO
    # -----------------------
    def _load_network_info(self):
        try:
            result = subprocess.run(
                ["hostname", "-I"],
                capture_output=True,
                text=True
            )

            ips = result.stdout.strip()
            self.log.setText(
                f"IP Addresses: {ips}" if ips else "No IP addresses found"
            )

        except Exception as e:
            self.log.setText(f"Error getting network info:\n{e}")