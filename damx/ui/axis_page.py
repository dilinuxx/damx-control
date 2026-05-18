from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

import utils.config as config


class AxisPage(QWidget):
    def __init__(self, controller=None, parent=None):
        super().__init__(parent)

        self.controller = controller
        self.build_ui()

    # -----------------------
    # GCODE SENDER
    # -----------------------
    def send_gcode(self, cmd):
        if hasattr(self, "controller") and self.controller:
            self.controller.send_gcode(cmd)
        else:
            print("GCODE:", cmd)

    # -----------------------
    # BUILD UI
    # -----------------------
    def build_ui(self):

        page = self

        page.setStyleSheet("""

            QLabel{
                color:white;
            }

            QPushButton{
                font-size:16px;
                padding:12px;
                border-radius:8px;
            }

            QPushButton:hover{
                opacity:0.85;
            }

        """)

        layout = QVBoxLayout(page)

        # -----------------------
        # TITLE
        # -----------------------
        title = QLabel("Axis Control")
        title.setStyleSheet("font-size:22px;color:#2f4056; font-weight:bold")
        layout.addWidget(title)

        # -----------------------
        # STEP SIZE
        # -----------------------

        step_layout = QHBoxLayout()

        step_label = QLabel("Step Size (X/Y/Z):")
        step_label.setStyleSheet("font-size:18px;color:orange; font-weight:bold")

        step_selector = QComboBox()
        step_selector.addItems([
            "0.02 mm", "0.05 mm", "0.1 mm", "0.2 mm", "0.5 mm", "1 mm",
            "10 mm", "50 mm", "100 mm", "165 Xmax", "220 Ymax", "415 Zmax"
        ])
        step_selector.setFixedWidth(120)

        feed_label = QLabel("Feed Rate (X/Y):")
        feed_label.setStyleSheet("font-size:18px;color:green; font-weight:bold")

        feed_selector = QComboBox()
        feed_selector.addItems(["500 mm/min", "1000 mm/min", "1500 mm/min"])
        feed_selector.setFixedWidth(100)

        recoater_label = QLabel("Recoater Speed (Z):")
        recoater_label.setStyleSheet("font-size:18px;color:blue; font-weight:bold")

        recoater_selector = QComboBox()
        recoater_selector.addItems(["500 mm/min", "1000 mm/min", "1500 mm/min"])
        recoater_selector.setFixedWidth(100)

        step_layout.addWidget(step_label)
        step_layout.addWidget(step_selector)
        step_layout.addSpacing(15)
        step_layout.addWidget(feed_label)
        step_layout.addWidget(feed_selector)
        step_layout.addSpacing(15)
        step_layout.addWidget(recoater_label)
        step_layout.addWidget(recoater_selector)
        step_layout.addStretch()

        layout.addLayout(step_layout)

        # -----------------------
        # AXIS GRID
        # -----------------------

        grid = QGridLayout()
        grid.setSpacing(15)

        btn_x_plus = QPushButton("➡ X+")
        btn_x_minus = QPushButton("⬅ X-")

        btn_y_plus = QPushButton("⬆ Y+")
        btn_y_minus = QPushButton("⬇ Y-")

        btn_z_plus = QPushButton("⬆ Z+")
        btn_z_minus = QPushButton("⬇ Z-")

        btn_x_plus.setStyleSheet("background-color:#e74c3c;color:white")
        btn_x_minus.setStyleSheet("background-color:#e74c3c;color:white")

        btn_y_plus.setStyleSheet("background-color:#27ae60;color:white")
        btn_y_minus.setStyleSheet("background-color:#27ae60;color:white")

        btn_z_plus.setStyleSheet("background-color:#3498db;color:white")
        btn_z_minus.setStyleSheet("background-color:#3498db;color:white")

        grid.addWidget(btn_y_plus, 0, 1)
        grid.addWidget(btn_x_minus, 1, 0)
        grid.addWidget(btn_x_plus, 1, 2)
        grid.addWidget(btn_y_minus, 2, 1)
        grid.addWidget(btn_z_plus, 0, 3)
        grid.addWidget(btn_z_minus, 2, 3)

        layout.addLayout(grid)

        btn_home = QPushButton("🏠 Home All Axes")

        btn_home.setStyleSheet("""
            QPushButton{
                background-color:#f39c12;
                color:white;
                font-size:18px;
                padding:14px;
                border-radius:10px;
            }

            QPushButton:hover{
                background-color:#f1c40f;
            }
        """)

        layout.addWidget(btn_home)

        # -----------------------
        # SEPARATOR LINE
        # -----------------------
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #2f4056; height: 2px;")
        layout.addWidget(separator)

        # -----------------------
        # AXIS FUNCTIONS
        # -----------------------

        def get_step():
            text = step_selector.currentText()
            return float(text.split()[0])

        def get_feed():
            text = feed_selector.currentText()
            return float(text.split()[0])

        def get_recoater():
            text = recoater_selector.currentText()
            return float(text.split()[0])

        def send_gcode(cmd):
            if hasattr(self, "controller"):
                self.controller.send_gcode(cmd)
            else:
                print("GCODE:", cmd)

        def move_x_plus():
            step = get_step()
            feed = get_feed()
            send_gcode(f"G91\nG0 X{step} F{feed}\nG90\n")

        def move_x_minus():
            step = get_step()
            feed = get_feed()
            send_gcode(f"G91\nG0 X-{step} F{feed}\nG90\n")

        def move_y_plus():
            step = get_step()
            feed = get_feed()
            send_gcode(f"G91\nG0 Y{step} F{feed}\nG90\n")

        def move_y_minus():
            step = get_step()
            feed = get_feed()
            send_gcode(f"G91\nG0 Y-{step} F{feed}\nG90\n")

        def move_z_plus():
            step = get_step()
            recoater_speed = get_recoater()
            send_gcode(f"G91\nG0 Z{step} F{recoater_speed}\nG90\n")

        def move_z_minus():
            step = get_step()
            recoater_speed = get_recoater()
            send_gcode(f"G91\nG0 Z-{step} F{recoater_speed}\nG90\n")

        def home_all():
            send_gcode("G28\n")

        # -----------------------
        # CONNECT AXIS BUTTONS
        # -----------------------

        btn_x_plus.clicked.connect(move_x_plus)
        btn_x_minus.clicked.connect(move_x_minus)

        btn_y_plus.clicked.connect(move_y_minus)
        btn_y_minus.clicked.connect(move_y_plus)

        btn_z_plus.clicked.connect(move_z_plus)
        btn_z_minus.clicked.connect(move_z_minus)

        btn_home.clicked.connect(home_all)

        # -----------------------
        # DOSING & BUILD CONTROL SEPARATOR
        # -----------------------

        separator_label = QLabel("Dosing & Build Control")
        separator_label.setStyleSheet("font-size:20px;color:#2f4056; font-weight:bold")
        layout.addWidget(separator_label)

        # -----------------------
        # DOSING & BUILD STEP SIZE
        # -----------------------

        dosing_step_layout = QHBoxLayout()

        dosing_step_label = QLabel("Dosing & Build Step Size:")
        dosing_step_label.setStyleSheet("font-size:18px;color:#e67e22; font-weight:bold")

        dosing_step_selector = QComboBox()
        dosing_step_selector.addItems([
            "10 µm", "20 µm", "30 µm", "40 µm", "50 µm", "100 µm",
            "200 µm", "500 µm", "1 mm", "10 mm", "50 mm", "100 mm",
            "200 mm", "270 mm"
        ])
        dosing_step_selector.setFixedWidth(120)

        dosing_feed_label = QLabel("Dosing & Build Feed Rate:")
        dosing_feed_label.setStyleSheet("font-size:18px;color:#71216B; font-weight:bold")

        dosing_feed_selector = QComboBox()
        dosing_feed_selector.addItems(["500 mm/min", "1000 mm/min", "1500 mm/min"])
        dosing_feed_selector.setFixedWidth(100)

        dosing_step_layout.addWidget(dosing_step_label)
        dosing_step_layout.addWidget(dosing_step_selector)
        dosing_step_layout.addSpacing(15)
        dosing_step_layout.addWidget(dosing_feed_label)
        dosing_step_layout.addWidget(dosing_feed_selector)
        dosing_step_layout.addStretch()

        layout.addLayout(dosing_step_layout)

        # -----------------------
        # DOSING & BUILD CONTROLS
        # -----------------------

        btn_dosing_plus = QPushButton("⬆ Dosing +")
        btn_dosing_minus = QPushButton("⬇ Dosing -")
        btn_dosing_plus_calibrate = QPushButton("Calibrate Dosing +")
        btn_dosing_minus_calibrate = QPushButton("Calibrate Dosing -")

        btn_build_plus = QPushButton("⬆ Build +")
        btn_build_minus = QPushButton("⬇ Build -")
        btn_build_plus_calibrate = QPushButton("Calibrate Build +")
        btn_build_minus_calibrate = QPushButton("Calibrate Build -")

        btn_dosing_plus.setStyleSheet("background-color:#e67e22;color:white")
        btn_dosing_minus.setStyleSheet("background-color:#e67e22;color:white")
        btn_build_plus.setStyleSheet("background-color:#9b59b6;color:white")
        btn_build_minus.setStyleSheet("background-color:#9b59b6;color:white")

        dosing_build_grid = QGridLayout()

        dosing_build_grid.addWidget(btn_dosing_plus, 0, 1)
        dosing_build_grid.addWidget(btn_dosing_minus, 1, 1)
        dosing_build_grid.addWidget(btn_dosing_plus_calibrate, 2, 1)
        dosing_build_grid.addWidget(btn_dosing_minus_calibrate, 3, 1)

        dosing_build_grid.addWidget(btn_build_plus, 0, 2)
        dosing_build_grid.addWidget(btn_build_minus, 1, 2)
        dosing_build_grid.addWidget(btn_build_plus_calibrate, 2, 2)
        dosing_build_grid.addWidget(btn_build_minus_calibrate, 3, 2)

        layout.addLayout(dosing_build_grid)

        layout.addStretch()

        # -----------------------
        # DOSING AND BUILD FUNCTIONS
        # -----------------------

        def get_layer_step():
            text = dosing_step_selector.currentText()
            value, unit = text.split()
            value = float(value)

            if unit == "µm":
                value /= 1000
            elif unit == "mm":
                pass

            return value

        def get_dosing_feedrate():
            return float(dosing_feed_selector.currentText().split()[0])

        def move_dose_plus():
            step = get_layer_step()
            feedrate = get_dosing_feedrate()

            send_gcode("M17\n")
            send_gcode("M82\n")
            send_gcode("M400\n")
            send_gcode("T1\n")

            send_gcode(f"G92 E{config.dosing_position * config.build_dosing_motor_units}\n")

            new_plus_position = max(config.dosing_position - step, 0)
            new_plus_position = float(f"{new_plus_position:.3f}")

            send_gcode(f"G1 E{new_plus_position * config.build_dosing_motor_units} F{feedrate}\n")

            ok_received = True
            if hasattr(self, "controller"):
                ok_received = self.controller.wait_for_ok()

            if ok_received:
                config.dosing_position = new_plus_position

        def move_dose_minus():
            step = get_layer_step()
            feedrate = get_dosing_feedrate()

            send_gcode("M17\n")
            send_gcode("M82\n")
            send_gcode("M400\n")
            send_gcode("T1\n")

            send_gcode(f"G92 E{config.dosing_position * config.build_dosing_motor_units}\n")

            new_minus_position = min(config.dosing_position + step, config.dosing_max_position)
            new_minus_position = float(f"{new_minus_position:.3f}")

            send_gcode(f"G1 E{new_minus_position * config.build_dosing_motor_units} F{feedrate}\n")

            if hasattr(self, "controller"):
                self.controller.wait_for_ok()

            config.dosing_position = new_minus_position

        def move_build_plus():
            step = get_layer_step()
            feedrate = get_dosing_feedrate()

            send_gcode("M17\n")
            send_gcode("M82\n")
            send_gcode("M400\n")
            send_gcode("T0\n")

            send_gcode(f"G92 E{config.build_position * config.build_dosing_motor_units}\n")

            new_build_plus_position = max(config.build_position - step, 0)
            new_build_plus_position = float(f"{new_build_plus_position:.3f}")

            send_gcode(f"G1 E{new_build_plus_position * config.build_dosing_motor_units} F{feedrate}\n")

            if hasattr(self, "controller"):
                self.controller.wait_for_ok()

            config.build_position = new_build_plus_position

        def move_build_minus():
            step = get_layer_step()
            feedrate = get_dosing_feedrate()

            send_gcode("M17\n")
            send_gcode("M82\n")
            send_gcode("M400\n")
            send_gcode("T0\n")

            send_gcode(f"G92 E{config.build_position * config.build_dosing_motor_units}\n")

            new_build_minus_position = min(config.build_position + step, config.build_max_position)
            new_build_minus_position = float(f"{new_build_minus_position:.3f}")

            send_gcode(f"G1 E{new_build_minus_position * config.build_dosing_motor_units} F{feedrate}\n")

            if hasattr(self, "controller"):
                self.controller.wait_for_ok()

            config.build_position = new_build_minus_position

        # -----------------------
        # CALIBRATION (UNCHANGED)
        # -----------------------

        def calibrate_dose_plus():
            print(f"Maximum Dosing Position: {config.dosing_max_position} mm")

        def calibrate_dose_minus():
            print(f"Minimum Dosing Position: {config.dosing_min_position} mm")

        def calibrate_build_plus():
            print(f"Maximum Build Position: {config.build_max_position} mm")

        def calibrate_build_minus():
            print(f"Minimum Build Position: {config.build_min_position} mm")

        # -----------------------
        # CONNECT BUTTONS
        # -----------------------

        btn_dosing_plus.clicked.connect(move_dose_plus)
        btn_dosing_minus.clicked.connect(move_dose_minus)
        btn_build_plus.clicked.connect(move_build_plus)
        btn_build_minus.clicked.connect(move_build_minus)

        btn_dosing_plus_calibrate.clicked.connect(calibrate_dose_plus)
        btn_dosing_minus_calibrate.clicked.connect(calibrate_dose_minus)
        btn_build_plus_calibrate.clicked.connect(calibrate_build_plus)
        btn_build_minus_calibrate.clicked.connect(calibrate_build_minus)