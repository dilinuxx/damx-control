__version__ = "2.0"

import time

"""
File: DamX_UI.py
https://www.svgrepo.com/vectors/axis/
https://fonts.google.com/icons
https://heroicons.com
ETHERNET CONNECTION
ssh pi@169.254.89.85/16
Password: damxeee

WIFI CONNECTION - EDUROAM
ssh pi@143.167.203.219
ssh pi@143.167.203.219/22
Password: damxeee

Description:
------------
This script implements a complete PyQt5-based control panel UI for the
DamX 3D printer system. The interface provides a modular
dashboard for real-time monitoring and control of various printer subsystems.

Features:
---------
1. Dashboard:
   - Displays status cards for Layer Height, Scan Speed, Recoater Speed, Temperature,
     and Job Status.
   - Shows real-time X, Y, Z gantry positions.
   - Provides Start, Pause, and Stop print controls.

2. Axis Control Page:
   - Step size selector for precise motor movement.
   - Directional control buttons for X, Y, Z axes.
   - Home All Axes functionality.

3. Chamber Environment Page:
   - Displays O₂, Argon flow, Nitrogen flow, Chamber pressure, and Humidity.

4. Beam / Laser Page:
   - Controls beam power and calibration sliders.

5. Gas Flow / Fan Page:
   - Controls Argon flow via slider interface.

6. Camera Page:
   - Displays camera feed placeholder.

7. Parts / Materials Page:
   - Shows parts queue with columns for Name, Status, Progress, ETA, Material,
     Layer Thickness, Flatness, and Action buttons (Pause/Cancel).

8. Records Page:
   - Displays system log.

9. Settings Page:
   - Placeholder for network and system settings.

Simulation & Updates:
--------------------
- Real-time updates of axes, chamber, and status cards using QTimer.
- Randomized values simulate live feedback for testing purposes.

Usage:
------
Run this script to launch the DamX Control Panel:
    python DamX_UI.py

Dependencies:
-------------
- Python 3.x
- PyQt5

Notes:
------
- This UI is structured using QStackedWidget for page navigation.
- Sidebar navigation allows switching between different modules.
- StatusCard class provides reusable card-style displays for key metrics.
"""

import sys, os
import random
import pytz
import subprocess
from datetime import datetime
#from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFrame, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QStackedWidget,
    QGridLayout, QProgressBar, QComboBox, QSlider, QTableWidget, QHeaderView, QTableWidgetItem, QTextEdit,
    QFileDialog, QMessageBox, QDialog
)
#from PyQt5.QtCore import *
from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal, QObject
#from PyQt5.QtGui import *
from PyQt5.QtGui import QIcon, QFont, QColor

# UI Pages
from ui.dashboard import DashboardPage
from ui.axis_page import AxisPage
from ui.chamber_page import ChamberPage
from ui.beam_page import BeamPage
from ui.camera_page import CameraPage
from ui.blower_page import BlowerPage
from ui.parts_page import PartsPage
from ui.records_page import RecordsPage
from ui.settings_page import SettingsPage

# Hardware
from hardware.axis import AxisControl
from hardware.chamber import ChamberControl
from hardware.beam_control import BeamControl
from hardware.beam_control import BeamWorker

# Comms
from comms.marlin_controller import MarlinController
from comms.printer_service import PrinterService

# Utils
import utils.config as config  # Import the config file

from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
import threading



# ----------------------
# Main UI
# ----------------------
class DAMXUI(QWidget):
    trigger_connect = pyqtSignal()
    trigger_disconnect = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setWindowTitle("DamX Control Panel")
        self.resize(1400, 900)

        # Folder for icons
        self.icon_folder = os.path.join(os.path.dirname(__file__), "icons")

        main_layout = QHBoxLayout(self)

        # -----------------------
        # SIDEBAR
        # -----------------------
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("background:#1e2a38")
        side_layout = QVBoxLayout()
        logo = QLabel("DamX")
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet("color:white;font-size:26px;font-weight:bold;padding:20px")
        side_layout.addWidget(logo)

        # Sidebar buttons with icons
        buttons = [
            ("Dashboard", "dashboard.svg"),
            ("Axis", "axis.svg"),
            ("Build Area", "build_area.svg"),
            ("Beam", "beam.svg"),
            ("Fan", "fan.svg"),
            ("CAM View", "cam_view.svg"),
            ("Materials", "materials.svg"),
            ("Records", "records.svg"),
            ("Settings", "settings.svg")
        ]

        self.nav_buttons = []
        for i, (name, icon_file) in enumerate(buttons):
            btn = QPushButton(name)
            btn.setFixedHeight(60)
            icon_path = os.path.join(self.icon_folder, icon_file)
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(32, 32))
            btn.setStyleSheet("""
                QPushButton{
                    color:white;
                    border:none;
                    text-align:left;
                    padding-left:15px;
                    font-size:16px;
                }
                QPushButton:hover{
                    background:#2f4056;
                }
            """)
            btn.clicked.connect(lambda checked, index=i: self.switch_page(index))
            side_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        side_layout.addStretch()
        sidebar.setLayout(side_layout)

        # -----------------------
        # MARLIN CONNECTION
        # -----------------------
        self.controller = MarlinController()
        QTimer.singleShot(2000, self.check_marlin_connection)

        # -----------------------
        # LOAD CALIBRATION VALUES
        # -----------------------
        self.controller.load_positions()

        # -----------------------
        # CHAMBER CONTROL CONNECTION
        # -----------------------
        self.chamber = ChamberControl(self.controller)

        # -----------------------
        # TIMER
        # -----------------------
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_values)
        self.printing = False
        self.progress_value = 0

        # -----------------------
        # LASER/BEAM CONTROLLER
        # -----------------------
        self.thread = QThread()
        self.worker = BeamWorker()
        self.worker.moveToThread(self.thread)
        self.thread.start()
        self.boris_connected = False

        # -----------------------
        # PAGES
        # -----------------------
        self.pages = QStackedWidget()
        self.dashboard_page = DashboardPage(self)
        self.axis_page = AxisPage(self.controller)
        self.chamber_page = ChamberPage(self.chamber)
        self.beam_page = BeamPage(
            worker=self.worker,
            trigger_connect=self.trigger_connect,
            trigger_disconnect=self.trigger_disconnect
        )
        self.camera_page = CameraPage()
        self.blower_page = BlowerPage()
        self.parts_page = PartsPage()
        self.records_page = RecordsPage()
        self.settings_page = SettingsPage()

        # Add pages to stacked widget
        self.pages.addWidget(self.dashboard_page)  # index 0
        self.pages.addWidget(self.axis_page)       # index 1
        self.pages.addWidget(self.chamber_page)    # index 2
        self.pages.addWidget(self.beam_page)       # index 3
        self.pages.addWidget(self.blower_page)     # index 4
        self.pages.addWidget(self.camera_page)     # index 5
        self.pages.addWidget(self.parts_page)      # index 6
        self.pages.addWidget(self.records_page)    # index 7
        self.pages.addWidget(self.settings_page)   # index 8

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.pages)
        self.pages.setCurrentIndex(0)

    # -----------------------
    # PAGE SWITCH
    # -----------------------
    def switch_page(self, index):
        self.pages.setCurrentIndex(index)

    # -----------------------
    # RESTART MACHINE
    # -----------------------
    # For now, just print or log — replace with actual restart logic
    def restart_machine(self):
        print("Restarting machine...")
        self.system_status_label.setText("System Status: Restarting")

    # -----------------------
    # SHUTDOWN MACHINE
    # -----------------------
    # For now, just print or log — replace with actual shutdown logic
    def shutdown_machine(self):
        print("Shutting down machine...")
        self.system_status_label.setText("System Status: Shutting Down")

    # -----------------------
    # UPDATE TIMER : Method to update time
    # -----------------------
    def update_time(self):
        bst = pytz.timezone("Europe/London")
        now = datetime.now(bst)
        self.time_label.setText(now.strftime("BST Time: %H:%M:%S"))

    # -----------------------
    # CHECK MARLIN CONNECTION
    # -----------------------
    def check_marlin_connection(self):
        connected = self.controller.find_marlin_port()
        if connected:
            self.dashboard_page.marlin_status_label.setText("Firmware: Not Connected")
            self.dashboard_page.marlin_status_label.setStyleSheet(
                "font-size:16px; font-weight:bold; color:red"
            )
            self.dashboard_page.reconnect_btn.setText("Connect")
            print("Firmware connected")
            # Update button
            self.reconnect_btn.setText("Disconnect")

            # -----------------------
            # START PRINTER SERVICE (QT VERSION)
            # -----------------------
            self.printer_service = PrinterService(self.controller, poll_interval=5000)  # ms
            self.printer_service.data_updated.connect(self.chamber_page.update_chamber_display) # Connect data → UI
            self.printer_service.log.connect(print)  # Optional: logs
            self.printer_service.start()  # Start polling (non-blocking)
        else:
            self.dashboard_page.marlin_status_label.setText("Firmware: Not Connected")
            self.dashboard_page.marlin_status_label.setStyleSheet(
                "font-size:16px; font-weight:bold; color:red"
            )
            print("Firmware not detected")
            self.dashboard_page.reconnect_btn.setText("Connect")

    # -----------------------
    # UPDATE CHAMBER DISPLAY
    # -----------------------
    def update_chamber_display(self, data):
        if "o2" in data:
            self.o2_label.setText(f"O2: {data['o2']:.2f} ppm")

        if "pressure" in data:
            self.pressure_label.setText(f"Chamber Pressure: {data['pressure']:.2f} bar")

    # -----------------------
    # LASER BUTTON TOGGLE
    # -----------------------
    def set_controls_enabled(self, enabled):
        self.power_slider.setEnabled(enabled)
        self.current_slider.setEnabled(enabled)

        for btn in self.laser_indicators:
            btn.setEnabled(enabled)

    def set_laser_style(self, btn, is_on):
        if is_on:
            btn.setStyleSheet("""
                QPushButton{
                    background-color:#00c853;
                    color:white;
                    border-radius:8px;
                    font-weight:bold;
                }
            """)
        else:
            btn.setStyleSheet("""
                QPushButton{
                    background-color:#1f6feb;
                    color:white;
                    border-radius:8px;
                    font-weight:bold;
                }
            """)

    def toggle_laser(self, index):
        if not getattr(self, "boris_connected", False):
            return

        current = self.laser_states[index]

        if current > 0:
            # TURN OFF
            self.worker.set_current(0, index, 0)
            self.laser_states[index] = 0
        else:
            # TURN ON using slider
            value = self.current_slider.value() * 100
            self.worker.set_current(0, index, value)
            self.laser_states[index] = value

        self.refresh_lasers()

    def update_current(self, value):
        if not getattr(self, "boris_connected", False):
            return

        index = self.selected_laser
        current = value * 100

        self.worker.set_current(0, index, current)
        self.laser_states[index] = current

        self.refresh_lasers()

    def refresh_lasers(self):
        for i, val in enumerate(self.laser_states):
            self.set_laser_style(self.laser_indicators[i], val > 0)

    def on_boris_connected(self, state):
        self.boris_connected = state

        if state:
            self.boris_status.setText("Status: Connected")
            self.boris_status.setStyleSheet("color:#ccffcc;")
        else:
            self.boris_status.setText("Status: Disconnected")
            self.boris_status.setStyleSheet("color:#ffcccc;")

        self.set_controls_enabled(state)

    def on_error(self, msg):
        self.boris_status.setText(f"Error: {msg}")
        self.boris_status.setStyleSheet("color:#ff6666;")

    def update_status(self, msg):
        """
        Update the UI label with the latest Boris connection status info.
        This will be called from the BeamWorker signal.
        """
        if hasattr(self, "boris_status") and self.boris_status:
            self.boris_status.setText(f"Status Info: {msg}")
            self.boris_status.setStyleSheet("color:#ccffcc; font-size:14px;")

    # -----------------------
    # SIMULATION / UPDATES
    # -----------------------
    def update_values(self):
        if self.printing:
            self.cards["Layer Height"].value.setText(str(random.randint(0,200)))
            self.cards["Scan Speed"].value.setText(str(random.randint(0,200)))
            self.cards["Recoater Speed"].value.setText("Active")
            self.cards["Temperature"].value.setText(f"{random.randint(180,220)} °C")
            self.cards["Job Status"].value.setText("Printing")

            # Gantry positions
            self.x_label.setText(f"X: {random.uniform(0,200):.2f} mm")
            self.y_label.setText(f"Y: {random.uniform(0,200):.2f} mm")
            self.z_label.setText(f"Z: {random.uniform(0,300):.2f} mm")

            # Chamber values
            self.o2_label.setText(f"O₂: {random.randint(30,80)} ppm")
            self.argon_label.setText(f"Argon Flow: {random.randint(4,6)} L/min")
            self.nitrogen_label.setText(f"Nitrogen Flow: {random.randint(0,1)} L/min")
            self.pressure_label.setText(f"Chamber Pressure: {random.randint(100,102)} bar")
            self.humidity_label.setText(f"Humidity: {random.randint(20,30)} %")

    # -----------------------
    # CONTROLS
    # -----------------------
    def start_print(self):

        # 1. Stop the Qt heartbeat timer loop
        self.printer_service.pause()
        self.system_status_label = QLabel("System Status: Building")

        # 2. Quiet the line to let Marlin finish transmitting its last active M621 block
        print("[INIT] Cool-down delay to drain active serial lines...")
        time.sleep(config.INIT_DRAIN_COOLDOWN_S)

        # 3. Purge physical hardware buffer registers
        if self.controller.ser and self.controller.ser.is_open:
            self.controller.ser.reset_input_buffer()
            self.controller.ser.reset_output_buffer()

        print(f"[START] Beginning {config.TOTAL_LAYERS}-layer build cycle with a clean serial pipe.")
        self.printing = True

        try:
            # -----------------------------------------
            # INITIALISATION SEQUENCE
            # -----------------------------------------

            # =====================================================
            # 1. Dosing piston DOWN to load material
            # =====================================================
            self.controller.send_gcode("M17\n")
            self.controller.wait_for_ok()

            self.controller.send_gcode("M82\n")  # Absolute E positioning for initialization steps
            self.controller.wait_for_ok()

            self.controller.send_gcode(f"{config.TOOL_DOSING_PISTON}\n")
            self.controller.wait_for_ok()

            self.controller.send_gcode(f"G92 E{config.dosing_position * config.build_dosing_motor_units}\n")
            self.controller.wait_for_ok()

            new_dose_position = max(config.dosing_position + config.INIT_DOSE_LOAD_DOWN_MM, 0)
            new_dose_position = float(f"{new_dose_position:.3f}")

            self.controller.send_gcode(
                f"G1 E{new_dose_position * config.build_dosing_motor_units} F{config.FEEDRATE_PISTONS}\n"
            )
            self.controller.wait_for_ok()

            self.controller.send_gcode("M400\n")  # Block until loading movement finishes
            if self.controller.wait_for_ok():
                config.dosing_position = new_dose_position
                print(f"[INIT] Dosing piston moved down to {new_dose_position}mm (load position).")
            else:
                print("[ERROR] Init load sequence failed.")
                self.printing = False
                return

            # =====================================================
            # 2. Dosing piston UP (prepare for recoating)
            # =====================================================
            self.controller.send_gcode(f"{config.TOOL_DOSING_PISTON}\n")
            self.controller.wait_for_ok()

            self.controller.send_gcode(f"G92 E{config.dosing_position * config.build_dosing_motor_units}\n")
            self.controller.wait_for_ok()

            # Direction inversion check: up push subtracts absolute positioning space
            new_dose_position = max(config.dosing_position - config.INIT_DOSE_PREP_UP_MM, 0)
            new_dose_position = float(f"{new_dose_position:.3f}")

            self.controller.send_gcode(
                f"G1 E{new_dose_position * config.build_dosing_motor_units} F{config.FEEDRATE_PISTONS}\n"
            )
            self.controller.wait_for_ok()

            self.controller.send_gcode("M400\n")
            if self.controller.wait_for_ok():
                config.dosing_position = new_dose_position
                print(f"[INIT] Dosing piston raised to {new_dose_position}mm (ready for recoater).")
            else:
                print("[ERROR] Init preparation push failed.")
                self.printing = False
                return

            # -----------------------------------------
            # MAIN BUILD LOOP — Pulls Layer Counts Dynamic
            # -----------------------------------------
            for layer in range(config.TOTAL_LAYERS):
                print(f"\n[LAYER {layer + 1}/{config.TOTAL_LAYERS}] Starting structural layer.")

                # =====================================================
                # Step 1: Dosing piston UP
                # =====================================================
                self.controller.send_gcode(f"{config.TOOL_DOSING_PISTON}\n")
                self.controller.wait_for_ok()

                self.controller.send_gcode("M17\n")
                self.controller.wait_for_ok()

                self.controller.send_gcode("G91\n")  # Motion axes relative
                self.controller.wait_for_ok()

                self.controller.send_gcode("M83\n")  # Extruder axis relative
                self.controller.wait_for_ok()

                # Calculate relative volumetric powder feed delta
                dose_move_val = config.DIRECTION_DOSE_UP * config.LAYER_THICKNESS_MM * config.build_dosing_motor_units
                self.controller.send_gcode(f"G1 E{dose_move_val:.3f} F{config.FEEDRATE_PISTONS}\n")
                self.controller.wait_for_ok()

                self.controller.send_gcode("M400\n")
                if self.controller.wait_for_ok():
                    config.dosing_position += (config.DIRECTION_DOSE_UP * config.LAYER_THICKNESS_MM)
                    print(f"[LAYER {layer + 1}] Dosing piston raised. Tracker: {config.dosing_position}mm")
                else:
                    print(f"[ERROR] Layer {layer + 1}: Dosing piston move failed.")
                    self.printing = False
                    return

                # =====================================================
                # Step 2: Recoater sweep
                # =====================================================
                self.controller.send_gcode("G91\n")
                self.controller.wait_for_ok()

                # Forward Sweep
                self.controller.send_gcode(
                    f"G0 {config.RECOATER_AXIS}{config.RECOATER_SWEEP_DISTANCE} F{config.FEEDRATE_RECOATER}\n"
                )
                self.controller.wait_for_ok()

                # Return Sweep
                self.controller.send_gcode(
                    f"G0 {config.RECOATER_AXIS}{-config.RECOATER_SWEEP_DISTANCE} F{config.FEEDRATE_RECOATER}\n"
                )
                self.controller.wait_for_ok()

                self.controller.send_gcode("M400\n")
                if self.controller.wait_for_ok():
                    print(f"[LAYER {layer + 1}] Recoater sweep complete.")
                else:
                    print(f"[ERROR] Layer {layer + 1}: Recoater sweep failed.")
                    self.printing = False
                    return

                # =====================================================
                # Step 3: Build piston DOWN
                # =====================================================
                self.controller.send_gcode(f"{config.TOOL_BUILD_PISTON}\n")
                self.controller.wait_for_ok()

                self.controller.send_gcode("M17\n")
                self.controller.wait_for_ok()

                self.controller.send_gcode("G91\n")
                self.controller.wait_for_ok()

                self.controller.send_gcode("M83\n")
                self.controller.wait_for_ok()

                # Calculate build drop delta
                build_move_val = config.DIRECTION_BUILD_DOWN * config.LAYER_THICKNESS_MM * config.build_dosing_motor_units
                self.controller.send_gcode(f"G1 E{build_move_val:.3f} F{config.FEEDRATE_PISTONS}\n")
                self.controller.wait_for_ok()

                self.controller.send_gcode("M400\n")
                if self.controller.wait_for_ok():
                    config.build_position += (config.DIRECTION_BUILD_DOWN * config.LAYER_THICKNESS_MM)
                    print(f"[LAYER {layer + 1}] Build piston lowered. Tracker: {config.build_position}mm")
                else:
                    print(f"[ERROR] Layer {layer + 1}: Build piston move failed.")
                    self.printing = False
                    return

                # Establish safe absolute positioning overrides for subsequent tracking systems
                self.controller.send_gcode("G90\n")
                self.controller.wait_for_ok()
                self.controller.send_gcode("M82\n")
                self.controller.wait_for_ok()

                # =====================================================
                # Step 4: Laser firing (placeholder)
                # =====================================================
                # =====================================================
                # Step 4: Laser Raster Exposure Pattern
                # =====================================================
                print(f"[LAYER {layer + 1}] Initiating laser exposure sequence.")

                # Force absolute coordinates for target bed placement matching
                self.controller.send_gcode("G90\n")
                self.controller.wait_for_ok()

                # Derive foundational boundary paths based on center constraints
                half_cube = config.CUBE_SIZE_MM / 2.0
                min_x = config.CUBE_CENTER_X - half_cube  # 74.0 mm
                max_x = config.CUBE_CENTER_X + half_cube  # 76.0 mm
                min_y = config.CUBE_CENTER_Y - half_cube  # 49.0 mm
                max_y = config.CUBE_CENTER_Y + half_cube  # 51.0 mm

                # 1. Travel swiftly to the start of the outer profile box
                self.controller.send_gcode(f"G0 X{min_x:.3f} Y{min_y:.3f} F{config.LASER_TRAVEL_SPEED}\n")
                self.controller.wait_for_ok()

                # 2. Trace Outer Perimeter Wall Boundary
                self.controller.send_gcode(config.LASER_ON_COMMAND)
                self.controller.wait_for_ok()

                self.controller.send_gcode(f"G1 X{max_x:.3f} Y{min_y:.3f} F{config.LASER_FEEDRATE}\n")
                self.controller.wait_for_ok()
                self.controller.send_gcode(f"G1 X{max_x:.3f} Y{max_y:.3f}\n")
                self.controller.wait_for_ok()
                self.controller.send_gcode(f"G1 X{min_x:.3f} Y{max_y:.3f}\n")
                self.controller.wait_for_ok()
                self.controller.send_gcode(f"G1 X{min_x:.3f} Y{min_y:.3f}\n")
                self.controller.wait_for_ok()

                # Extinguish laser for clean transit maneuver
                self.controller.send_gcode(config.LASER_OFF_COMMAND)
                self.controller.wait_for_ok()

                # 3. Core Hatching Density Scan Interlacing
                # Step parallel to the X-axis, shifting upward by the hatch spacing metric
                current_y = min_y + config.HATCH_SPACING_MM
                toggle_direction = True  # Zig-zag trace toggle register

                while current_y < max_y:
                    if toggle_direction:
                        # Move to start of line, fire laser, raster to the right
                        self.controller.send_gcode(f"G0 X{min_x:.3f} Y{current_y:.3f} F{config.LASER_TRAVEL_SPEED}\n")
                        self.controller.wait_for_ok()
                        self.controller.send_gcode(config.LASER_ON_COMMAND)
                        self.controller.wait_for_ok()
                        self.controller.send_gcode(f"G1 X{max_x:.3f} Y{current_y:.3f} F{config.LASER_FEEDRATE}\n")
                        self.controller.wait_for_ok()
                    else:
                        # Move to end of line, fire laser, raster backward to the left
                        self.controller.send_gcode(f"G0 X{max_x:.3f} Y{current_y:.3f} F{config.LASER_TRAVEL_SPEED}\n")
                        self.controller.wait_for_ok()
                        self.controller.send_gcode(config.LASER_ON_COMMAND)
                        self.controller.wait_for_ok()
                        self.controller.send_gcode(f"G1 X{min_x:.3f} Y{current_y:.3f} F{config.LASER_FEEDRATE}\n")
                        self.controller.wait_for_ok()

                    #self.controller.send_gcode(config.LASER_OFF_COMMAND)
                    #self.controller.wait_for_ok()

                    current_y += config.HATCH_SPACING_MM
                    toggle_direction = not toggle_direction  # Alternate direction flags

                # 4. Final Sync Check
                self.controller.send_gcode("M400\n")
                if self.controller.wait_for_ok():
                    print(f"[LAYER {layer + 1}] Laser exposure complete and synchronized.")
                else:
                    print(f"[ERROR] Layer {layer + 1}: Laser exposure tracking lost.")
                    self.printing = False
                    return

                print(f"[LAYER {layer + 1}] Laser exposure complete.")

        finally:
            self.printing = False
            self.printer_service.resume()
            print(f"[COMPLETE] {config.TOTAL_LAYERS}-layer build cycle concluded safely.")
            self.system_status_label = QLabel("System Status: Idle")

    def pause_print(self):
        print("[PAUSE] Initiating safe build pause sequence.")
        self.printing = False

        # Correctly update your existing interface element text safely
        self.system_status_label.setText("System Status: Paused")

        # 1. Kill the laser immediately first if it happens to be running
        self.controller.send_gcode(config.LASER_OFF_COMMAND)
        self.controller.wait_for_ok()

        # 2. Block until current mechanical action concludes safely
        self.controller.send_gcode("M400\n")
        self.controller.wait_for_ok()

        # 3. Request standard Marlin SD/stream pause intercept hook
        self.controller.send_gcode("M25\n")
        self.controller.wait_for_ok()

        # 4. Enforce driver holding current so heavy powder loads do not drop down
        self.controller.send_gcode("M17\n")
        self.controller.wait_for_ok()

        # Preserve state metrics
        config.paused_dosing = config.dosing_position
        config.paused_build = config.build_position

        print(
            f"[PAUSE] Build paused successfully. Stored states: Dosing={config.paused_dosing}mm, Build={config.paused_build}mm.")

    def resume_print(self):
        print("[RESUME] Resuming build cycle.")
        self.system_status_label.setText("System Status: Build")

        # 1. Ensure absolute coordinates are set for the position mapping re-sync
        self.controller.send_gcode("M82\n")
        self.controller.wait_for_ok()

        # 2. Synchronize Dosing Piston coordinate context
        self.controller.send_gcode(f"{config.TOOL_DOSING_PISTON}\n")
        self.controller.wait_for_ok()

        # CRITICAL: Always scale position mapping targets by motor step multipliers
        dose_scaled_steps = config.paused_dosing * config.build_dosing_motor_units
        self.controller.send_gcode(f"G92 E{dose_scaled_steps:.3f}\n")
        self.controller.wait_for_ok()

        # 3. Synchronize Build Piston coordinate context
        self.controller.send_gcode(f"{config.TOOL_BUILD_PISTON}\n")
        self.controller.wait_for_ok()

        build_scaled_steps = config.paused_build * config.build_dosing_motor_units
        self.controller.send_gcode(f"G92 E{build_scaled_steps:.3f}\n")
        self.controller.wait_for_ok()

        # 4. Final physical validation step
        self.controller.send_gcode("M400\n")
        self.controller.wait_for_ok()

        # Reactivate main execution loop context state
        self.printing = True
        print("[RESUME] Internal coordinate maps fully synchronized. Resuming physical automation lines.")

    def stop_print(self):
        print("[STOP] Emergency stop triggered. Aborting SLM print immediately.")

        # Instantly cut the physical loop flags on the Python execution layer
        self.printing = False
        self.timer.stop()

        self.system_status_label.setText("System Status: Idle")

        # 1. Instantly kill the exposure energy beam path
        self.controller.send_gcode(config.LASER_OFF_COMMAND)
        self.controller.wait_for_ok()

        # 2. Finish or interrupt active motion queues
        self.controller.send_gcode("M400\n")
        self.controller.wait_for_ok()

        # 3. Trigger global hardware kill signal lockouts
        self.controller.send_gcode("M0\n")
        self.controller.wait_for_ok()

        # 4. Keep steppers energized so heavy metal powder layers do not collapse down
        self.controller.send_gcode("M17\n")
        self.controller.wait_for_ok()

        # =====================================================
        # Safe Recoater Park Maneuver (Relative Retreat)
        # =====================================================
        self.controller.send_gcode("G91\n")
        self.controller.wait_for_ok()

        # Move back by a negative distance matching your configured homing zone direction
        self.controller.send_gcode(
            f"G0 {config.RECOATER_AXIS}-20.0 F{config.FEEDRATE_RECOATER}\n"
        )
        self.controller.wait_for_ok()

        self.controller.send_gcode("G90\n")
        self.controller.wait_for_ok()

        # Reset coordinate software variables safely
        config.dosing_position = 0.0
        config.build_position = 0.0

        # Update and refresh interface monitoring fields safely
        self.progress_value = 0
        for card in self.cards.values():
            card.value.setText("--")

        self.x_label.setText("X: 0.00 mm")
        self.y_label.setText("Y: 0.00 mm")
        self.z_label.setText("Z: 0.00 mm")
        self.o2_label.setText("O2: 000 ppm")
        self.argon_label.setText("Argon Flow: 0 L/min")
        self.nitrogen_label.setText("Nitrogen Flow: 0 L/min")
        self.pressure_label.setText("Chamber Pressure: 000 bar")
        self.humidity_label.setText("Humidity: 0%")

        self.cards["Job Status"].value.setText("Idle")
        self.cards["Temperature"].value.setText("--")

        print("[STOP] Print safely aborted. UI fields purged, laser disabled, pistons locked.")