from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem,
    QPushButton, QHeaderView, QProgressBar
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt


class PartsPage(QWidget):
    """
    Parts / Materials page widget.
    Converted from create_parts_page() function to class while
    preserving structure and behaviour.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)

        # -----------------------
        # TABLE SETUP
        # -----------------------
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "Part Name", "Status", "Progress", "ETA", "Material",
            "Layer Thickness", "Flatness", "Actions"
        ])

        self._style_table()
        self._populate_table()

        main_layout.addWidget(self.table)

    # -----------------------
    # TABLE STYLING
    # -----------------------
    def _style_table(self):
        self.table.setStyleSheet("""
            QHeaderView::section {
                background-color: #2f4056;
                color: white;
                font-weight: bold;
                height: 35px;
            }

            QTableWidget {
                background-color: #1e2a38;
                color: white;
                gridline-color: #2f4056;
            }

            QTableWidget::item:selected {
                background-color: #3a4b5c;
            }

            QTableWidget::item:alternate {
                background-color: #252f3d;
            }
        """)

        self.table.setFont(QFont("Arial", 14))
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    # -----------------------
    # SAMPLE DATA POPULATION
    # -----------------------
    def _populate_table(self):
        parts_data = [
            {"name": "Part A", "status": "Printing", "progress": 25, "eta": "00:30", "material": "Ti-6Al-4V",
             "layer": "0.04 mm", "flatness": "OK"},

            {"name": "Part B", "status": "Queued", "progress": 0, "eta": "-", "material": "316L",
             "layer": "0.00 mm", "flatness": "OK"},

            {"name": "Part C", "status": "Completed", "progress": 100, "eta": "-", "material": "BiZn2.7",
             "layer": "0.05 mm", "flatness": "OK"},
        ]

        self.table.setRowCount(len(parts_data))

        for row, part in enumerate(parts_data):
            self._add_row(row, part)

    # -----------------------
    # ROW BUILDER
    # -----------------------
    def _add_row(self, row, part):
        self.table.setItem(row, 0, QTableWidgetItem(part["name"]))

        # Status colouring
        status_item = QTableWidgetItem(part["status"])
        if part["status"] == "Printing":
            status_item.setForeground(QColor("#FFA500"))  # orange
        elif part["status"] == "Queued":
            status_item.setForeground(QColor("#5A9BF6"))  # blue
        elif part["status"] == "Completed":
            status_item.setForeground(QColor("#00FF00"))  # green
        self.table.setItem(row, 1, status_item)

        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setValue(part["progress"])
        progress_bar.setAlignment(Qt.AlignCenter)
        progress_bar.setTextVisible(True)
        progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #2f4056;
                color: white;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #00C851;
                border-radius: 5px;
            }
        """)
        self.table.setCellWidget(row, 2, progress_bar)

        # Other columns
        self.table.setItem(row, 3, QTableWidgetItem(part["eta"]))
        self.table.setItem(row, 4, QTableWidgetItem(part["material"]))
        self.table.setItem(row, 5, QTableWidgetItem(part["layer"]))
        self.table.setItem(row, 6, QTableWidgetItem(part["flatness"]))

        # Actions column
        self.table.setCellWidget(row, 7, self._create_actions(part["status"]))

    # -----------------------
    # ACTION BUTTON FACTORY
    # -----------------------
    def _create_actions(self, status):
        action_widget = QWidget()
        layout = QHBoxLayout(action_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        def make_btn(text, color):
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border-radius: 5px;
                    padding: 5px 10px;
                }}
            """)
            return btn

        if status == "Printing":
            layout.addWidget(make_btn("Pause", "#FFA500"))
            layout.addWidget(make_btn("Cancel", "#FF4D4D"))

        elif status == "Queued":
            layout.addWidget(make_btn("Start", "#00C851"))
            layout.addWidget(make_btn("Delete", "#FF4D4D"))

        elif status == "Completed":
            layout.addWidget(make_btn("Delete", "#FF4D4D"))

        return action_widget