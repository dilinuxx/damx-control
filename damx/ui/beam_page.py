from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt


class BeamPage(QWidget):
    def __init__(self, worker, trigger_connect, trigger_disconnect, parent=None):
        super().__init__(parent)

        # Keep references (for compatibility with old code)
        self.worker = worker
        self.trigger_connect = trigger_connect
        self.trigger_disconnect = trigger_disconnect

        self.laser_states = [0] * 10
        self.selected_laser = 0
        self.laser_indicators = []

        self.build_ui()
        self.connect_signals()
        self.set_controls_enabled(False)

    # -----------------------
    # UI BUILD
    # -----------------------
    def build_ui(self):

        self.setStyleSheet("""
            QWidget{ background-color:#004953; }
            QLabel{
                font-size:16px;
                color:#ffffff;
                font-weight:bold;
            }
            QPushButton{
                background-color:#ffffff;
                color:#1f1f1f;
                font-size:14px;
                padding:8px;
                border-radius:6px;
            }
            QPushButton:hover{ background-color:#ffe0cc; }
            QSlider::groove:horizontal{
                height:8px;
                background:#ffd1b3;
                border-radius:4px;
            }
            QSlider::handle:horizontal{
                background:#1f6feb;
                width:18px;
                margin:-5px 0;
                border-radius:9px;
            }
        """)

        layout = QVBoxLayout(self)

        # TITLE
        title = QLabel("Laser / Beam Control")
        title.setStyleSheet("font-size:24px; font-weight:bold;")
        layout.addWidget(title)

        # BORIS CONNECTION
        layout.addWidget(QLabel("Boris Controller"))

        conn_layout = QHBoxLayout()
        self.connect_btn = QPushButton("Connect to Boris")
        self.disconnect_btn = QPushButton("Disconnect")

        self.boris_status = QLabel("Status: Disconnected")
        self.boris_status.setStyleSheet("color:#ffcccc; font-size:14px;")

        conn_layout.addWidget(self.connect_btn)
        conn_layout.addWidget(self.disconnect_btn)

        layout.addLayout(conn_layout)
        layout.addWidget(self.boris_status)

        # LASER ARRAY
        layout.addWidget(QLabel("Laser Diode Array"))
        grid = QGridLayout()

        for i in range(10):
            diode = QPushButton(f"L{i+1}")
            diode.setFixedSize(60, 50)
            diode.clicked.connect(lambda _, idx=i: self.toggle_laser(idx))
            self.set_laser_style(diode, False)
            grid.addWidget(diode, i // 5, i % 5)
            self.laser_indicators.append(diode)

        layout.addLayout(grid)

        # POWER
        layout.addWidget(QLabel("Beam Power (%)"))
        self.power_slider = QSlider(Qt.Horizontal)
        self.power_slider.setRange(0, 100)
        self.power_slider.setValue(60)
        layout.addWidget(self.power_slider)

        # CURRENT
        layout.addWidget(QLabel("Laser Current (A)"))
        self.current_slider = QSlider(Qt.Horizontal)
        self.current_slider.setRange(0, 50)
        self.current_slider.setValue(30)
        self.current_slider.valueChanged.connect(self.update_current)
        layout.addWidget(self.current_slider)

        # CALIBRATION
        layout.addWidget(QLabel("Calibration"))
        calib_layout = QHBoxLayout()
        self.auto_btn = QPushButton("Auto Calibrate")
        self.test_btn = QPushButton("Test Pulse")
        self.align_btn = QPushButton("Beam Align")
        calib_layout.addWidget(self.auto_btn)
        calib_layout.addWidget(self.test_btn)
        calib_layout.addWidget(self.align_btn)
        layout.addLayout(calib_layout)

        # CHILLER
        layout.addWidget(QLabel("Laser Cooling System"))
        self.chiller_status = QLabel("Temp: 18°C   Flow: 3.4 L/min   Pump: ON")
        self.chiller_status.setStyleSheet("font-size:15px;")
        layout.addWidget(self.chiller_status)

        chill_layout = QHBoxLayout()
        self.start_chiller = QPushButton("Start Chiller")
        self.stop_chiller = QPushButton("Stop Chiller")
        chill_layout.addWidget(self.start_chiller)
        chill_layout.addWidget(self.stop_chiller)
        layout.addLayout(chill_layout)

        layout.addStretch()

    # -----------------------
    # SIGNAL CONNECTIONS
    # -----------------------
    def connect_signals(self):
        self.trigger_connect.connect(self.worker.connect_boris)
        self.trigger_disconnect.connect(self.worker.disconnect_boris)

        self.connect_btn.clicked.connect(self.trigger_connect.emit)
        self.disconnect_btn.clicked.connect(self.trigger_disconnect.emit)

        self.worker.connected.connect(self.on_boris_connected)
        self.worker.error.connect(self.on_error)
        self.worker.status_update.connect(self.update_status)

    # -----------------------
    # EXISTING FUNCTIONS (kept for compatibility)
    # -----------------------
    def toggle_laser(self, idx):
        self.laser_states[idx] ^= 1
        self.set_laser_style(self.laser_indicators[idx], self.laser_states[idx])

    def set_laser_style(self, button, active):
        if active:
            button.setStyleSheet("background-color:#ff4444; color:white;")
        else:
            button.setStyleSheet("background-color:#dddddd; color:black;")

    def update_current(self, value):
        pass  # keep hook

    def on_boris_connected(self):
        self.boris_status.setText("Status: Connected")
        self.set_controls_enabled(True)

    def on_error(self, msg):
        self.boris_status.setText(f"Error: {msg}")

    def update_status(self, status):
        self.boris_status.setText(status)

    def set_controls_enabled(self, enabled):
        for widget in self.findChildren(QPushButton) + self.findChildren(QSlider):
            widget.setEnabled(enabled)
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(True)