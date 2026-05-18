from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer
import random
from ui.status_card import StatusCard

class DashboardPage(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.cards = {}
        self.build_ui()
        self.start_timers()

    # -----------------------
    # UI BUILDER (was create_dashboard_page)
    # -----------------------
    def build_ui(self):
        layout = QVBoxLayout(self)

        # ----------------------
        # Status cards
        # ----------------------
        grid = QGridLayout()
        modules = ["Layer Height", "Scan Speed", "Recoater Speed", "Temperature", "Job Status"]

        dummy_values = {
            "Layer Height": "0.05 mm/layer",
            "Scan Speed": "500 mm/s",
            "Recoater Speed": "30 rpm",
            "Temperature": "200 °C",
            "Job Status": "Idle"
        }

        row, col = 0, 0
        for m in modules:
            card = StatusCard(m)
            card.set_value(dummy_values[m])
            grid.addWidget(card, row, col)
            self.cards[m] = card

            col += 1
            if col > 2:
                col = 0
                row += 1

        layout.addLayout(grid)

        # ----------------------
        # Laser Diode Array Info
        # ----------------------
        self.laser_label = QLabel("Laser: 10 W × 10 diodes")
        self.laser_label.setAlignment(Qt.AlignCenter)
        self.laser_label.setStyleSheet("font-size:16px; font-weight:bold; color:#d32f2f")
        layout.addWidget(self.laser_label)

        # ----------------------
        # Marlin Connection Status
        # ----------------------
        connection_layout = QHBoxLayout()

        self.marlin_status_label = QLabel("Marlin: Not Connected")
        self.marlin_status_label.setStyleSheet("font-size:16px; font-weight:bold; color:red")

        self.reconnect_btn = QPushButton("Connecting ......")
        self.reconnect_btn.setFixedWidth(120)
        self.reconnect_btn.clicked.connect(self.check_marlin_connection)

        connection_layout.addWidget(self.marlin_status_label)
        connection_layout.addStretch()
        connection_layout.addWidget(self.reconnect_btn)

        layout.addLayout(connection_layout)

        # ----------------------
        # Gantry X, Y, Z
        # ----------------------
        self.x_label = QLabel("X: 0.00 mm")
        self.y_label = QLabel("Y: 0.00 mm")
        self.z_label = QLabel("Z: 0.00 mm")

        for lbl in [self.x_label, self.y_label, self.z_label]:
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-size:16px;font-weight:bold")

        gantry_layout = QHBoxLayout()
        gantry_layout.addWidget(self.x_label)
        gantry_layout.addWidget(self.y_label)
        gantry_layout.addWidget(self.z_label)
        layout.addLayout(gantry_layout)

        # ----------------------
        # System status & time
        # ----------------------
        status_layout = QHBoxLayout()

        self.system_status_label = QLabel("System Status: Idle")
        self.system_status_label.setStyleSheet("font-size:16px; font-weight:bold; color:blue")

        self.time_label = QLabel("")
        self.time_label.setStyleSheet("font-size:16px; font-weight:bold; color:green")

        status_layout.addWidget(self.system_status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.time_label)

        layout.addLayout(status_layout)

        # ----------------------
        # Progress bar
        # ----------------------
        self.job_progress = QProgressBar()
        self.job_progress.setValue(0)
        self.job_progress.setFormat("Job Progress: %p%")
        layout.addWidget(self.job_progress)

        # ----------------------
        # Controls
        # ----------------------
        controls = QHBoxLayout()

        self.start_btn = QPushButton("Start")
        self.pause_btn = QPushButton("Pause")
        self.stop_btn = QPushButton("Stop")
        self.restart_btn = QPushButton("Restart")
        self.shutdown_btn = QPushButton("Shutdown")

        buttons = [
            (self.start_btn, "#2e7d32"),
            (self.pause_btn, "#f9a825"),
            (self.stop_btn, "#c62828"),
            (self.restart_btn, "#1565c0"),
            (self.shutdown_btn, "#6d1b7b")
        ]

        for b, color in buttons:
            b.setFixedHeight(60)
            b.setStyleSheet(f"background:{color}; color:white; font-size:18px; border-radius:6px;")
            controls.addWidget(b)

        layout.addLayout(controls)

        # Connect buttons
        self.start_btn.clicked.connect(self.start_print)
        self.pause_btn.clicked.connect(self.pause_print)
        self.stop_btn.clicked.connect(self.stop_print)
        self.restart_btn.clicked.connect(self.restart_machine)
        self.shutdown_btn.clicked.connect(self.shutdown_machine)

    # -----------------------
    # TIMERS (moved from function)
    # -----------------------
    def start_timers(self):
        self.timer_time = QTimer(self)
        self.timer_time.timeout.connect(self.update_time)
        self.timer_time.start(1000)

        self.timer_values = QTimer(self)
        self.timer_values.timeout.connect(self.update_dummy_values)
        self.timer_values.start(500)

    # -----------------------
    # ORIGINAL METHODS (unchanged)
    # -----------------------
    def update_dummy_values(self):
        self.cards["Layer Height"].set_value(f"{round(random.uniform(0.04, 0.06), 3)} mm/layer")
        self.cards["Scan Speed"].set_value(f"{random.randint(450, 550)} mm/s")
        self.cards["Recoater Speed"].set_value(f"{random.randint(25, 35)} rpm")
        self.cards["Temperature"].set_value(f"{random.randint(195, 205)} °C")

        if self.system_status_label.text() == "System Status: Building":
            progress = self.job_progress.value()
            if progress < 100:
                self.job_progress.setValue(progress + 1)
            else:
                self.system_status_label.setText("System Status: Idle")
                self.job_progress.setValue(0)

    # Dummy placeholders
    def check_marlin_connection(self): pass
    def update_time(self): pass
    def start_print(self): pass
    def pause_print(self): pass
    def stop_print(self): pass
    def restart_machine(self): pass
    def shutdown_machine(self): pass