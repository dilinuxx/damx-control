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

        # Legacy Step Size
        step_label = QLabel("Step Size (X/Y/Z):")
        step_label.setStyleSheet("font-size:18px;color:orange; font-weight:bold")

        step_selector = QComboBox()
        step_selector.addItems([
            "0.02 mm",
            "0.05 mm",
            "0.1 mm",
            "0.2 mm",
            "0.5 mm",
            "1 mm",
            "10 mm",
            "50 mm",
            "100 mm",
            "165 Xmax",
            "220 Ymax",
            "415 Zmax"
        ])
        step_selector.setFixedWidth(120)

        # Feed Rate options
        feed_label = QLabel("Feed Rate (X/Y):")
        feed_label.setStyleSheet("font-size:18px;color:green; font-weight:bold")

        feed_selector = QComboBox()
        feed_selector.addItems([
            "500 mm/min",
            "1000 mm/min",
            "1500 mm/min"
        ])
        feed_selector.setFixedWidth(100)

        # Recoater Speed options
        recoater_label = QLabel("Recoater Speed (Z):")
        recoater_label.setStyleSheet("font-size:18px;color:blue; font-weight:bold")

        recoater_selector = QComboBox()
        recoater_selector.addItems([
            "500 mm/min",
            "1000 mm/min",
            "1500 mm/min"
        ])
        recoater_selector.setFixedWidth(100)

        # Add widgets to layout
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

        # X Axis (Red)
        btn_x_plus = QPushButton("➡ X+")
        btn_x_minus = QPushButton("⬅ X-")

        btn_x_plus.setStyleSheet("background-color:#e74c3c;color:white")
        btn_x_minus.setStyleSheet("background-color:#e74c3c;color:white")

        # Y Axis (Green)
        btn_y_plus = QPushButton("⬆ Y+")
        btn_y_minus = QPushButton("⬇ Y-")

        btn_y_plus.setStyleSheet("background-color:#27ae60;color:white")
        btn_y_minus.setStyleSheet("background-color:#27ae60;color:white")

        # Z Axis (Blue)
        btn_z_plus = QPushButton("⬆ Z+")
        btn_z_minus = QPushButton("⬇ Z-")

        btn_z_plus.setStyleSheet("background-color:#3498db;color:white")
        btn_z_minus.setStyleSheet("background-color:#3498db;color:white")

        # Layout positions
        grid.addWidget(btn_y_plus, 0, 1)

        grid.addWidget(btn_x_minus, 1, 0)
        grid.addWidget(btn_x_plus, 1, 2)

        grid.addWidget(btn_y_minus, 2, 1)

        grid.addWidget(btn_z_plus, 0, 3)
        grid.addWidget(btn_z_minus, 2, 3)

        layout.addLayout(grid)

        # -----------------------
        # HOME BUTTON
        # -----------------------

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
        # SEPARATOR LINE BETWEEN AXIS CONTROL AND DOSING & BUILD CONTROL
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

        def movee_x_plus():
            step = get_step()
            send_gcode(f"G91\nG0 X{step}\nG90\n")

        def movee_x_minus():
            step = get_step()
            send_gcode(f"G91\nG0 X-{step}\nG90\n")

        def movee_y_plus():
            step = get_step()
            send_gcode(f"G91\nG0 Y{step}\nG90\n")

        def movee_y_minus():
            step = get_step()
            send_gcode(f"G91\nG0 Y-{step}\nG90\n")

        def movee_z_plus():
            step = get_step()
            send_gcode(f"G91\nG0 Z{step}\nG90\n")

        def movee_z_minus():
            step = get_step()
            send_gcode(f"G91\nG0 Z-{step}\nG90\n")

        def homee_all():
            send_gcode("G28\n")

        # -----------------------
        # CONNECT AXIS BUTTONS
        # -----------------------

        btn_x_plus.clicked.connect(move_x_plus)
        btn_x_minus.clicked.connect(move_x_minus)

        # KEEP ORIGINAL INVERTED LOGIC
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
        # Dosing & Build Controls Step Size
        # -----------------------

        dosing_step_layout = QHBoxLayout()

        dosing_step_label = QLabel("Dosing & Build Step Size:")
        dosing_step_label.setStyleSheet("font-size:18px;color:#e67e22; font-weight:bold")

        dosing_step_selector = QComboBox()
        dosing_step_selector.addItems([
            "10 µm",
            "20 µm",
            "30 µm",
            "40 µm",
            "50 µm",
            "100 µm",
            "200 µm",
            "500 µm",
            "1 mm",
            "10 mm",
            "50 mm",
            "100 mm",
            "200 mm",
            "270 mm"
        ])
        dosing_step_selector.setFixedWidth(120)

        # Feed rate
        dosing_feed_label = QLabel("Dosing & Build Feed Rate:")
        dosing_feed_label.setStyleSheet("font-size:18px;color:#71216B; font-weight:bold")

        dosing_feed_selector = QComboBox()
        dosing_feed_selector.addItems([
            "500 mm/min",
            "1000 mm/min",
            "1500 mm/min"
        ])
        dosing_feed_selector.setFixedWidth(100)

        dosing_step_layout.addWidget(dosing_step_label)
        dosing_step_layout.addWidget(dosing_step_selector)
        dosing_step_layout.addSpacing(15)
        dosing_step_layout.addWidget(dosing_feed_label)
        dosing_step_layout.addWidget(dosing_feed_selector)
        dosing_step_layout.addStretch()

        layout.addLayout(dosing_step_layout)

        # -----------------------
        # Dosing & Build Controls
        # -----------------------

        btn_dosing_plus = QPushButton("⬆ Dosing +")
        btn_dosing_minus = QPushButton("⬇ Dosing -")
        btn_dosing_plus_calibrate = QPushButton("⬆ Calibrate Dosing +")
        btn_dosing_minus_calibrate = QPushButton("⬇ Calibrate Dosing -")

        btn_dosing_plus.setStyleSheet("background-color:#e67e22;color:white")
        btn_dosing_minus.setStyleSheet("background-color:#e67e22;color:white")
        btn_dosing_plus_calibrate.setStyleSheet("background-color:#e67e22;color:white")
        btn_dosing_minus_calibrate.setStyleSheet("background-color:#e67e22;color:white")

        btn_build_plus = QPushButton("⬆ Build +")
        btn_build_minus = QPushButton("⬇ Build -")
        btn_build_plus_calibrate = QPushButton("⬆ Calibrate Build +")
        btn_build_minus_calibrate = QPushButton("⬇ Calibrate Build -")

        btn_build_plus.setStyleSheet("background-color:#9b59b6;color:white")
        btn_build_minus.setStyleSheet("background-color:#9b59b6;color:white")
        btn_build_plus_calibrate.setStyleSheet("background-color:#9b59b6;color:white")
        btn_build_minus_calibrate.setStyleSheet("background-color:#9b59b6;color:white")

        # Layout
        dosing_build_grid = QGridLayout()
        dosing_build_grid.setSpacing(15)

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

        # ---------------------------------
        # DOSING AND BUILD FUNCTIONS
        # ---------------------------------

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
            text = dosing_feed_selector.currentText()
            return float(text.split()[0])

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

            send_gcode(
                f"G1 E{new_plus_position * config.build_dosing_motor_units} F{feedrate}\n"
            )

            ok_received = True

            if hasattr(self, "controller"):
                ok_received = self.controller.wait_for_ok()

            if ok_received:

                config.dosing_position = new_plus_position
                update_dosing_ui()

                print(
                    f"[DEBUG] Step: {step} mm | Feedrate: {feedrate} mm/min | "
                    f"Dosing Position: {config.dosing_position} mm | "
                    f"Max Position: {config.dosing_max_position} mm"
                )

            else:
                print("[move_dose_plus] Warning: Move not confirmed by Marlin. Position not updated.")

        def move_dose_minus():

            step = get_layer_step()
            feedrate = get_dosing_feedrate()

            send_gcode("M17\n")
            send_gcode("M82\n")
            send_gcode("M400\n")
            send_gcode("T1\n")

            send_gcode(f"G92 E{config.dosing_position * config.build_dosing_motor_units}\n")

            new_minus_position = min(
                config.dosing_position + step,
                config.dosing_max_position
            )

            new_minus_position = float(f"{new_minus_position:.3f}")

            send_gcode(
                f"G1 E{new_minus_position * config.build_dosing_motor_units} F{feedrate}\n"
            )

            ok_received = True

            if hasattr(self, "controller"):
                ok_received = self.controller.wait_for_ok()

            if ok_received:

                config.dosing_position = new_minus_position
                update_dosing_ui()
                print(
                    f"[DEBUG] Step: {step} mm | Feedrate: {feedrate} mm/min | "
                    f"Dosing Position: {config.dosing_position} mm | "
                    f"Max Position: {config.dosing_max_position} mm"
                )

            else:
                print("[move_dose_minus] Warning: Move not confirmed by Marlin. Position not updated.")

        def move_build_plus():

            step = get_layer_step()
            feedrate = get_dosing_feedrate()

            send_gcode("M17\n")
            send_gcode("M82\n")
            send_gcode("M400\n")
            send_gcode("T0\n")

            send_gcode(f"G92 E{config.build_position * config.build_dosing_motor_units}\n")

            new_build_plus_position = max(
                config.build_position - step,
                0
            )

            new_build_plus_position = float(f"{new_build_plus_position:.3f}")

            send_gcode(
                f"G1 E{new_build_plus_position * config.build_dosing_motor_units} F{feedrate}\n"
            )

            ok_received = True

            if hasattr(self, "controller"):
                ok_received = self.controller.wait_for_ok()

            if ok_received:

                config.build_position = new_build_plus_position
                update_build_ui()
                print(
                    f"[DEBUG] Step: {step} mm | Feedrate: {feedrate} mm/min | "
                    f"Build Position: {config.build_position} mm | "
                    f"Max Position: {config.build_max_position} mm"
                )

            else:
                print("[move_build_plus] Warning: Move not confirmed by Marlin. Position not updated.")

        def move_build_minus():

            step = get_layer_step()
            feedrate = get_dosing_feedrate()

            send_gcode("M17\n")
            send_gcode("M82\n")
            send_gcode("M400\n")
            send_gcode("T0\n")

            send_gcode(f"G92 E{config.build_position * config.build_dosing_motor_units}\n")

            new_build_minus_position = min(
                config.build_position + step,
                config.build_max_position
            )

            send_gcode(
                f"G1 E{new_build_minus_position * config.build_dosing_motor_units} F{feedrate}\n"
            )

            ok_received = True

            if hasattr(self, "controller"):
                ok_received = self.controller.wait_for_ok()

            if ok_received:

                config.build_position = new_build_minus_position
                update_build_ui()
                print(
                    f"[DEBUG] Step: {step} mm | Feedrate: {feedrate} mm/min | "
                    f"Build Position: {config.build_position} mm | "
                    f"Max Position: {config.build_max_position} mm"
                )

            else:
                print("[move_build_minus] Warning: Move not confirmed by Marlin. Position not updated.")

        # =====================================================================
        # UI UPDATE HELPERS
        # =====================================================================
        def update_dosing_ui():

            from_top = config.dosing_position
            from_bottom = (
                    config.dosing_max_position
                    - config.dosing_position
            )

            btn_dosing_plus.setText(
                f"⬆ Dosing + [{from_bottom:.3f} mm]"
            )

            btn_dosing_minus.setText(
                f"⬇ Dosing - [{from_top:.3f} mm]"
            )

            btn_dosing_plus.setEnabled(
                from_bottom > config.dosing_min_position
            )

            btn_dosing_minus.setEnabled(
                from_top < config.dosing_max_position
            )

        def update_build_ui():

            from_top = config.build_position
            from_bottom = (
                    config.build_max_position
                    - config.build_position
            )

            btn_build_plus.setText(
                f"⬆ Build + [{from_bottom:.3f} mm]"
            )

            btn_build_minus.setText(
                f"⬇ Build - [{from_top:.3f} mm]"
            )

            btn_build_plus.setEnabled(
                from_bottom > config.build_min_position
            )

            btn_build_minus.setEnabled(
                from_top < config.build_max_position
            )

        # =====================================================================
        # DOSING CALIBRATION
        # =====================================================================
        def calibrate_dose_minus():

            # ---------------------------------------------------------
            # "This current position is X mm from TOP"
            #
            # Example:
            # 10 mm selected
            # -> current physical piston location is 10 mm below top
            # ---------------------------------------------------------

            step = get_layer_step()

            new_position = round(step, 3)

            send_gcode("M17\n")
            send_gcode("M82\n")
            send_gcode("M400\n")
            send_gcode("T1\n")

            # ---------------------------------------------------------
            # IMPORTANT:
            # Re-map Marlin's current E position to THIS coordinate
            # without physically moving the piston
            # ---------------------------------------------------------

            send_gcode(
                f"G92 E{new_position * config.build_dosing_motor_units}\n"
            )

            config.dosing_position = new_position

            update_dosing_ui()

            print(
                f"[CAL] Dosing calibrated from TOP: "
                f"{config.dosing_position:.3f} mm"
            )

        def calibrate_dose_plus():
            # ---------------------------------------------------------
            # "This current position is X mm from BOTTOM"
            #
            # Example:
            # max = 280
            # 10 mm selected
            #
            # -> current piston location becomes:
            # 280 - 10 = 270 mm from top
            # ---------------------------------------------------------

            step = get_layer_step()

            new_position = round(
                config.dosing_max_position - step,
                3
            )

            send_gcode("M17\n")
            send_gcode("M82\n")
            send_gcode("M400\n")
            send_gcode("T1\n")

            # ---------------------------------------------------------
            # Re-map Marlin coordinate system
            # WITHOUT moving hardware
            # ---------------------------------------------------------

            send_gcode(
                f"G92 E{new_position * config.build_dosing_motor_units}\n"
            )

            config.dosing_position = new_position

            update_dosing_ui()

            print(
                f"[CAL] Dosing calibrated from BOTTOM: "
                f"{step:.3f} mm"
            )

        # =====================================================================
        # BUILD CALIBRATION
        # =====================================================================

        def calibrate_build_minus():
            # ---------------------------------------------------------
            # "This current position is X mm from TOP"
            # ---------------------------------------------------------

            step = get_layer_step()

            new_position = round(step, 3)

            send_gcode("M17\n")
            send_gcode("M82\n")
            send_gcode("M400\n")
            send_gcode("T0\n")

            # ---------------------------------------------------------
            # Re-map Build piston coordinate system
            # ---------------------------------------------------------

            send_gcode(
                f"G92 E{new_position * config.build_dosing_motor_units}\n"
            )

            config.build_position = new_position

            update_build_ui()

            print(
                f"[CAL] Build calibrated from TOP: "
                f"{config.build_position:.3f} mm"
            )

        def calibrate_build_plus():

            # ---------------------------------------------------------
            # "This current position is X mm from BOTTOM"
            # ---------------------------------------------------------

            step = get_layer_step()

            new_position = round(
                config.build_max_position - step,
                3
            )

            send_gcode("M17\n")
            send_gcode("M82\n")
            send_gcode("M400\n")
            send_gcode("T0\n")

            # ---------------------------------------------------------
            # Re-map Build piston coordinate system
            # ---------------------------------------------------------

            send_gcode(
                f"G92 E{new_position * config.build_dosing_motor_units}\n"
            )

            config.build_position = new_position

            update_build_ui()

            print(
                f"[CAL] Build calibrated from BOTTOM: "
                f"{step:.3f} mm"
            )

        # =====================================================================
        # INITIAL UI UPDATE
        # =====================================================================
        update_dosing_ui()
        update_build_ui()

        # ---------------------------------
        # CONNECT DOSING AND BUILD BUTTONS
        # ---------------------------------

        btn_dosing_plus.clicked.connect(move_dose_plus)
        btn_dosing_minus.clicked.connect(move_dose_minus)

        btn_build_plus.clicked.connect(move_build_plus)
        btn_build_minus.clicked.connect(move_build_minus)

        btn_dosing_plus_calibrate.clicked.connect(calibrate_dose_plus)
        btn_dosing_minus_calibrate.clicked.connect(calibrate_dose_minus)

        btn_build_plus_calibrate.clicked.connect(calibrate_build_plus)
        btn_build_minus_calibrate.clicked.connect(calibrate_build_minus)