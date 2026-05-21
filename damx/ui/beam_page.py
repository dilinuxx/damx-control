from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
import time

class BeamPage(QWidget):

    def __init__(self, controller=None, worker=None, psu=None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.worker = worker
        self.psu = psu

        self.current_layer = 0
        self.is_building = False

        self.build_ui()
        self.connect_signals()

    # -----------------------
    # GCODE SENDER (AxisPage-style)
    # -----------------------
    def send_gcode(self, cmd):
        if hasattr(self, "controller") and self.controller:
            self.controller.send_gcode(cmd)
        else:
            print("GCODE:", cmd)

    # -----------------------
    # MOVE TO BUILD POSITION
    # -----------------------
    def navigate_to_build_position(self):
        try:
            self.send_gcode("G90\n")
            self.send_gcode("G0 X50 Y50 F3000\n")
            self.beam_status.setText("Moved to build position")
        except Exception as e:
            self.beam_status.setText(f"Move failed: {e}")

    # -----------------------
    # FULL CYLINDER BUILD (your original logic)
    # -----------------------
    def build_cylinder_layered(self, layer):

        if self.is_building:
            self.beam_status.setText("Build already running")
            return

        self.is_building = True
        self.beam_status.setText(f"Layer {layer}: starting cylinder")

        try:
            import math

            # -----------------------
            # MOVE TO BUILD POSITION FIRST
            # -----------------------
            self.send_gcode("G90\n")  # Absolute positioning
            self.controller.wait_for_ok()

            self.send_gcode("G0 X50 Y50 F3000\n")  # Move to start position
            self.send_gcode("M400\n")  # Wait for motion to finish
            self.controller.wait_for_ok()

            # -----------------------
            # TURN ON LASER PSU
            # -----------------------
            self.laser_on(amps=2.5)

            cx = 75.0
            cy = 50.0
            r = 1.0
            step = 0.1

            y = cy - r
            toggle = True

            while y <= cy + r:
                dy = y - cy
                inside = r ** 2 - dy ** 2
                if inside <= 0:
                    y += step
                    continue

                dx = math.sqrt(inside)
                x1 = cx - dx
                x2 = cx + dx

                # -----------------------
                # Move to start of line, laser OFF
                # -----------------------
                if toggle:
                    self.send_gcode(f"G0 X{x1:.3f} Y{y:.3f} F3000\n")
                else:
                    self.send_gcode(f"G0 X{x2:.3f} Y{y:.3f} F3000\n")

                self.send_gcode("M400\n")  # Wait for gantry to physically arrive
                self.controller.wait_for_ok()

                # -----------------------
                # Scan line with laser ON
                # -----------------------
                if toggle:
                    self.send_gcode(f"G1 X{x2:.3f} Y{y:.3f} F1200\n")
                else:
                    self.send_gcode(f"G1 X{x1:.3f} Y{y:.3f} F1200\n")

                self.send_gcode("M400\n")  # Wait until move completes
                self.controller.wait_for_ok()

                toggle = not toggle
                y += step

            # -----------------------
            # LAYER COMPLETE: TURN OFF LASER
            # -----------------------
            self.laser_off()
            self.beam_status.setText(f"Layer {layer} complete")
            self.current_layer += 1

        except Exception as e:
            self.beam_status.setText(f"Build failed: {e}")
            self.laser_off()

        finally:
            self.is_building = False

    def build_cylinder_layer(self, layer):

        if self.is_building:
            self.beam_status.setText("Build already running")
            return

        self.is_building = True
        self.beam_status.setText(f"Layer {layer}: starting cylinder")

        try:
            import math

            self.send_gcode("G90\n")
            # Turn on PSU laser at 2.5A
            self.laser_on(amps=2.5)

            cx = 50.0
            cy = 50.0
            r = 1.0
            step = 0.1

            y = cy - r
            toggle = True

            while y <= cy + r:

                dy = y - cy
                inside = r ** 2 - dy ** 2

                if inside <= 0:
                    y += step
                    continue

                dx = math.sqrt(inside)

                x1 = cx - dx
                x2 = cx + dx

                if toggle:
                    self.send_gcode(f"G0 X{x1:.3f} Y{y:.3f} F3000\n")
                    # Turn on PSU laser at 2.5A
                    self.laser_on(amps=2.5)
                    #self.send_gcode("M1001\n")  # LASER ON (Marlin)
                    self.send_gcode(f"G1 X{x2:.3f} Y{y:.3f} F1200\n")
                else:
                    self.send_gcode(f"G0 X{x2:.3f} Y{y:.3f} F3000\n")
                    # Turn on PSU laser at 2.5A
                    self.laser_on(amps=2.5)
                    #self.send_gcode("M1001\n")  # LASER ON (Marlin)
                    self.send_gcode(f"G1 X{x1:.3f} Y{y:.3f} F1200\n")

                toggle = not toggle
                y += step

            self.send_gcode("M400\n")
            self.controller.wait_for_ok()
            time.sleep(1)

            # Turn off PSU laser
            #self.send_gcode("M1002\n")  # LASER OFF (Marlin)
            self.laser_off()

            self.beam_status.setText(f"Layer {layer} complete")
            self.current_layer += 1

        except Exception as e:
            self.beam_status.setText(f"Build failed: {e}")

            # Safety: ensure PSU is off
            self.laser_off()

        finally:
            self.is_building = False

    # -----------------------
    # UI BUILD (full colours restored)
    # -----------------------
    def build_ui(self):

        self.setStyleSheet("""
            QWidget{
                background-color:#004953;
            }

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

            QPushButton:hover{
                background-color:#ffe0cc;
            }

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

        # Title
        title = QLabel("Laser / Beam Control")
        title.setStyleSheet("font-size:24px; font-weight:bold;")
        layout.addWidget(title)

        # Characterisation buttons
        samples_layout = QHBoxLayout()
        self.buildpos_btn = QPushButton("Navigate to Build Position")
        self.buildsample_btn = QPushButton("Build Samples (Layer)")
        samples_layout.addWidget(self.buildpos_btn)
        samples_layout.addWidget(self.buildsample_btn)
        layout.addLayout(samples_layout)

        # Status label
        self.beam_status = QLabel("Beam Idle")
        self.beam_status.setStyleSheet("color:#ffffff; font-size:15px;")
        layout.addWidget(self.beam_status)

        layout.addStretch()

    # -----------------------
    # SIGNAL CONNECTIONS
    # -----------------------
    def connect_signals(self):

        # Move to build position
        self.buildpos_btn.clicked.connect(self.navigate_to_build_position)

        # Build one layer (IMPORTANT: lambda)
        self.buildsample_btn.clicked.connect(
            lambda: self.build_cylinder_layer(self.current_layer)
        )

    def laser_on(self, amps=2.5):
        """Turn on PSU laser channel at fixed 12V and given current."""
        try:
            self.psu.set_voltage(1, 12.0)
            self.psu.set_current(1, amps)
            self.psu.output_on(1)
            print("Laser PSU ON at", amps, "A")
        except Exception as e:
            print("Laser ON failed:", e)

    def laser_off(self):
        """Turn off PSU laser channel."""
        try:
            self.psu.output_off(1)
            print("Laser PSU OFF")
        except Exception as e:
            print("Laser OFF failed:", e)