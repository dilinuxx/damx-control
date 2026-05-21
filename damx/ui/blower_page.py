from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QSlider
)
from PyQt5.QtCore import Qt


class BlowerPage(QWidget):

    def __init__(self, blower=None, parent=None):
        super().__init__(parent)

        self.blower = blower

        main_layout = QVBoxLayout(self)

        # -----------------------
        # TITLE
        # -----------------------
        title = QLabel("Gas Flow / Blower System")
        title.setStyleSheet(
            "font-size:22px; font-weight:bold; color:orange;"
        )
        main_layout.addWidget(title)

        main_layout.addWidget(self._create_status_panel())
        main_layout.addWidget(self._create_speed_control())
        main_layout.addWidget(self._create_buttons())

        main_layout.addStretch()

    # -----------------------
    # STATUS PANEL
    # -----------------------
    def _create_status_panel(self):
        frame = QFrame()

        frame.setStyleSheet("""
            QFrame{
                background-color:#252f3d;
                border-radius:8px;
            }

            QLabel{
                color:white;
                font-size:16px;
            }
        """)

        layout = QGridLayout(frame)

        self.rpm_label = QLabel("Blower RPM: 0")
        self.flow_label = QLabel("Gas Flow: 0 m/s")
        self.filter_label = QLabel("Filter Status: OK")
        self.temp_label = QLabel("Temperature: 0°C")

        layout.addWidget(self.rpm_label, 0, 0)
        layout.addWidget(self.flow_label, 0, 1)
        layout.addWidget(self.filter_label, 1, 0)
        layout.addWidget(self.temp_label, 1, 1)

        return frame

    # -----------------------
    # SPEED CONTROL
    # -----------------------
    def _create_speed_control(self):
        frame = QFrame()

        frame.setStyleSheet("""
            QFrame{
                background-color:#252f3d;
                border-radius:8px;
            }
        """)

        layout = QVBoxLayout(frame)

        slider_label = QLabel("Blower Speed")
        slider_label.setStyleSheet(
            "color:white; font-size:16px;"
        )

        self.flow_slider = QSlider(Qt.Horizontal)

        self.flow_slider.setMinimum(0)
        self.flow_slider.setMaximum(100)
        self.flow_slider.setValue(30)

        self.flow_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #2f4056;
                height: 8px;
                border-radius:4px;
            }

            QSlider::handle:horizontal {
                background: #5A9BF6;
                width:18px;
                margin:-6px 0;
                border-radius:9px;
            }
        """)

        self.flow_slider.valueChanged.connect(
            self.update_blower_speed
        )

        layout.addWidget(slider_label)
        layout.addWidget(self.flow_slider)

        return frame

    # -----------------------
    # CONTROL BUTTONS
    # -----------------------
    def _create_buttons(self):
        frame = QFrame()
        layout = QHBoxLayout(frame)

        self.start_btn = QPushButton("Start Blower")
        self.stop_btn = QPushButton("Stop Blower")
        self.reset_btn = QPushButton("Reset Alarm")

        self.start_btn.setStyleSheet("""
            QPushButton{
                background-color:#00C851;
                color:white;
                font-size:16px;
                padding:10px;
                border-radius:6px;
            }

            QPushButton:hover{
                background-color:#2ed573;
            }
        """)

        self.stop_btn.setStyleSheet("""
            QPushButton{
                background-color:#ff4d4d;
                color:white;
                font-size:16px;
                padding:10px;
                border-radius:6px;
            }

            QPushButton:hover{
                background-color:#ff6b6b;
            }
        """)

        self.reset_btn.setStyleSheet("""
            QPushButton{
                background-color:#5A9BF6;
                color:white;
                font-size:16px;
                padding:10px;
                border-radius:6px;
            }

            QPushButton:hover{
                background-color:#74b9ff;
            }
        """)

        self.start_btn.clicked.connect(self.start_blower)
        self.stop_btn.clicked.connect(self.stop_blower)
        self.reset_btn.clicked.connect(self.reset_alarm)

        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.reset_btn)

        return frame

    # -----------------------
    # FUNCTIONS
    # -----------------------
    def start_blower(self):
        print("Blower started")

        if self.blower:
            self.blower.start()

    def stop_blower(self):
        print("Blower stopped")

        if self.blower:
            self.blower.stop()

    def reset_alarm(self):
        print("Alarm reset")

        if self.blower:
            self.blower.reset_alarm()

    def update_blower_speed(self, value):
        self.rpm_label.setText(f"Blower RPM: {value * 50}")
        self.flow_label.setText(f"Gas Flow: {value / 10:.1f} m/s")

        if self.blower:
            self.blower.set_speed(value)