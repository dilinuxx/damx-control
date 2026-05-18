from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit


class RecordsPage(QWidget):
    """
    System log / records page.
    Converted from create_records_page().
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)

        self.log = QTextEdit()
        self.log.setText("System Log...\n")

        layout.addWidget(self.log)