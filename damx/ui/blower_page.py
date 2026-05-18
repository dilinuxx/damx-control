from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QSlider
)
from PyQt5.QtCore import Qt


class BlowerPage(QWidget):
    """
    Gas Flow / Blower control page.
    Converted from create_blower_page().
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        main_layout = QVBoxLayout(self)

        # -----------------------
        # TITLE
        # -----------------------
        title = QLabel("Gas Flow / Blower System")
        title.setStyleSheet("font-size:22px; font-weight:bold; color:orange;")
        main_layout.addWidget(title)

        # Build sections
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
        slider_label.setStyleSheet("color:white; font-size:16px;")

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

        layout.addWidget(slider_label)
        layout.addWidget(self.flow_slider)

        return frame

    # -----------------------
    # CONTROL BUTTONS
    # -----------------------
    def _create_buttons(self):
        frame = QFrame()
        layout = QHBoxLayout(frame)

        def make_button(text, color, hover):
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color:{color};
                    color:white;
                    font-size:16px;
                    padding:10px;
                    border-radius:6px;
                }}
                QPushButton:hover {{
                    background-color:{hover};
                }}
            """)
            return btn

        self.start_btn = make_button("Start Blower", "#00C851", "#2ed573")
        self.stop_btn = make_button("Stop Blower", "#ff4d4d", "#ff6b6b")
        self.reset_btn = make_button("Reset Alarm", "#5A9BF6", "#74b9ff")

        layout.addWidget(self.start_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.reset_btn)

        return frame