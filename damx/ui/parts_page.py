import os
import re
from comms.marlin_controller import MarlinController
from comms.printer_service import PrinterService
from comms.build_executor import BuildExecutor
import utils.config as config
import threading

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
    Updated to load .gcode jobs from /damx/jobs/
    and populate table dynamically.
    """

    JOBS_DIR = os.path.join(os.path.dirname(__file__), "jobs")

    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(8)

        self.table.setHorizontalHeaderLabels([
            "Part Name",
            "Status",
            "Progress",
            "ETA",
            "Material",
            "Layer Thickness",
            "Flatness",
            "Actions"
        ])

        self._style_table()
        self._populate_table()

        main_layout.addWidget(self.table)

        self.controller = MarlinController()
        self.controller.find_marlin_port()
        self.printer_service = PrinterService(self.controller)
        self.printer_service.start()

        self.executor = BuildExecutor()
        self.executor.controller = self.controller
        self.executor.printer_service = self.printer_service

    # ---------------------------------------------------------
    # TABLE STYLING
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # LOAD JOBS FROM /damx/jobs/
    # ---------------------------------------------------------
    def _populate_table(self):

        gcode_files = [
            f for f in os.listdir(self.JOBS_DIR)
            if f.lower().endswith(".gcode")
        ]

        self.parts_data = []

        for filename in gcode_files:
            full_path = os.path.join(self.JOBS_DIR, filename)

            meta = self._parse_gcode_metadata(full_path)

            self.parts_data.append({
                "name": filename,
                "status": "Queued",
                "progress": 0,
                "eta": meta.get("eta", "-"),
                "material": meta.get("material", "Unknown"),
                "layer": meta.get("layer_height", "-"),
                "flatness": "OK",
                "path": full_path
            })

        self.table.setRowCount(len(self.parts_data))

        for row, part in enumerate(self.parts_data):
            self._add_row(row, part)

    # ---------------------------------------------------------
    # PARSE G-CODE HEADER METADATA
    # ---------------------------------------------------------
    def _parse_gcode_metadata(self, path):
        meta = {}

        try:
            with open(path, "r") as f:
                lines = f.readlines()

            # -----------------------------
            # 1. Parse HEADER metadata
            # -----------------------------
            for line in lines:
                if not line.startswith(";"):
                    break

                if "Material:" in line:
                    meta["material"] = line.split(":")[1].strip()

                if "Layer Height" in line:
                    meta["layer_height"] = line.split(":")[1].strip()

                if "Estimated Time" in line and "minutes" in line:
                    # Header ETA
                    meta["eta"] = line.split(":")[1].strip() + " min"

            # -----------------------------
            # 2. Parse FOOTER ETA
            # -----------------------------
            for line in reversed(lines):
                if "Estimated Time (minutes)" in line:
                    minutes = line.split(":")[1].strip()
                    meta["eta"] = minutes + " min"
                    break

        except Exception as e:
            print("Metadata parse error:", e)

        return meta

    # ---------------------------------------------------------
    # ADD ROW TO TABLE
    # ---------------------------------------------------------
    def _add_row(self, row, part):

        self.table.setItem(row, 0, QTableWidgetItem(part["name"]))

        # STATUS COLORING
        status_item = QTableWidgetItem(part["status"])

        if part["status"] == "Printing":
            status_item.setForeground(QColor("#FFA500"))
        elif part["status"] == "Queued":
            status_item.setForeground(QColor("#5A9BF6"))
        elif part["status"] == "Completed":
            status_item.setForeground(QColor("#00FF00"))

        self.table.setItem(row, 1, status_item)

        # PROGRESS BAR
        progress_bar = QProgressBar()
        progress_bar.setValue(part["progress"])
        progress_bar.setTextVisible(True)
        progress_bar.setAlignment(Qt.AlignCenter)

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

        # OTHER COLUMNS
        self.table.setItem(row, 3, QTableWidgetItem(part["eta"]))
        self.table.setItem(row, 4, QTableWidgetItem(part["material"]))
        self.table.setItem(row, 5, QTableWidgetItem(part["layer"]))
        self.table.setItem(row, 6, QTableWidgetItem(part["flatness"]))

        # ACTION BUTTONS
        self.table.setCellWidget(row, 7, self._create_actions(row, part["status"]))

    # ---------------------------------------------------------
    # ACTION BUTTONS
    # ---------------------------------------------------------
    def _create_actions(self, row, status):

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

        # PRINTING → Pause / Cancel
        if status == "Printing":
            pause_btn = make_btn("Pause", "#FFA500")
            cancel_btn = make_btn("Cancel", "#FF4D4D")

            pause_btn.clicked.connect(lambda: self.pause_part(row))
            cancel_btn.clicked.connect(lambda: self.cancel_part(row))

            layout.addWidget(pause_btn)
            layout.addWidget(cancel_btn)

        # QUEUED → Start / Delete
        elif status == "Queued":
            start_btn = make_btn("Start", "#00C851")
            delete_btn = make_btn("Delete", "#FF4D4D")

            start_btn.clicked.connect(lambda: self.start_part(row))
            delete_btn.clicked.connect(lambda: self.delete_part(row))

            layout.addWidget(start_btn)
            layout.addWidget(delete_btn)

        # COMPLETED → Delete
        elif status == "Completed":
            delete_btn = make_btn("Delete", "#FF4D4D")
            delete_btn.clicked.connect(lambda: self.delete_part(row))
            layout.addWidget(delete_btn)

        return action_widget

    # ---------------------------------------------------------
    # ACTION HANDLERS
    # ---------------------------------------------------------
    def start_part(self, row):
        part = self.parts_data[row]
        print(f"Start part: {part['path']}")
        part["status"] = "Printing"
        part["progress"] = 5
        self._refresh_row(row)

        # IMPORTANT: set global config (what executor actually uses)
        config.BUILD_FILE = part["path"]

        threading.Thread(
            target=self.executor.start_print,
            daemon=True
        ).start()

    def pause_part(self, row):
        print(f"Pause part at row {row}")
        # signal executor
        self.executor.paused = True
        # optional firmware pause
        self.controller.send_gcode("M0\n")
        self.parts_data[row]["status"] = "Queued"
        self._refresh_row(row)

    def cancel_part(self, row):
        print(f"Cancel part at row {row}")
        self.parts_data[row]["status"] = "Queued"
        self.parts_data[row]["progress"] = 0
        self._refresh_row(row)

    def delete_part(self, row):
        print(f"Delete part at row {row}")
        self.table.removeRow(row)

    # ---------------------------------------------------------
    # REFRESH A ROW WHEN STATUS CHANGES
    # ---------------------------------------------------------
    def _refresh_row(self, row):
        part = self.parts_data[row]
        for col in range(self.table.columnCount()):
            self.table.takeItem(row, col)
        self._add_row(row, part)

    def refresh(self):
        """Reload job list when page becomes visible."""
        self.table.clearContents()
        self._populate_table()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh()