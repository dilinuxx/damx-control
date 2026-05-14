"""
Marlin Serial Communication Controller
======================================

This module provides a lightweight Python interface for communicating with
Marlin-based firmware controllers over a serial connection. It is designed
for laboratory automation and digital fabrication workflows where reliable
G-code transmission and machine-state synchronization are required.

The implementation automatically scans available serial ports to detect a
Marlin-compatible device, establishes communication, and exposes utility
methods for:

1. Detecting and connecting to Marlin firmware
2. Sending G-code commands over serial
3. Waiting for firmware acknowledgment responses ("ok")
4. Saving and loading calibration parameters

The controller is intended for integration into automated motion-control
systems such as powder dosing platforms, additive manufacturing devices,
or custom robotic instruments.

Key Features
------------
- Automatic serial-port discovery
- Marlin firmware verification using `M115`
- Robust timeout-based response handling
- Persistent storage of calibration positions
- Recovery handling for disconnected serial devices

Dependencies
------------
- pyserial
- time
- serial.tools.list_ports

Example
-------
- >>> controller = MarlinController()
- >>> if controller.find_marlin_port():
...     controller.send_gcode("G28\\n")
...     controller.wait_for_ok()

Notes
-----
Opening a serial connection to many Arduino-based controllers causes an
automatic device reset. Therefore, a short delay is introduced after
opening the serial port to allow firmware initialization before issuing
commands.

Author
------
Prepared for JOSS (Journal of Open Source Software) style documentation.
"""

import serial
import serial.tools.list_ports
import time

class MarlinController:

    def __init__(self):
        self.ser = None

    # -----------------------
    # FIND MARLIN PORT
    # -----------------------

    def find_marlin_port(self):

        # Stop RepetierServer before scanning ports
        import subprocess
        try:
            subprocess.run(
                ["sudo", "killall", "RepetierServer"],
                check=False,  # continue even if it's not running
                stdout=subprocess.DEVNULL,  # hide output
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            print(f"Warning: Could not kill RepetierServer: {e}")

        # Now scan for Marlin
        ports = serial.tools.list_ports.comports()

        for port in ports:
            try:
                print("Checking:", port.device)

                ser = serial.Serial(port.device, 250000, timeout=2)
                #ser = serial.Serial(port.device, 250000, timeout=2, dsrdtr=False)
                ser.dtr = False

                # Arduino resets when serial opens
                time.sleep(2)

                # flush startup messages
                ser.reset_input_buffer()

                ser.write(b"M115\n")

                start = time.time()

                while time.time() - start < 3:

                    line = ser.readline().decode(errors="ignore").strip()

                    if line:
                        print("Response:", line)

                    if "FIRMWARE_NAME" in line or "Marlin" in line:
                        print("Firmware detected on:", port.device)

                        self.ser = ser
                        return True

                ser.close()

            except Exception as e:
                print("Failed:", port.device, e)

        return False

    # -----------------------
    # SEND GCODE
    # -----------------------
    def send_gcode(self, cmd):

        if not self.ser or not self.ser.is_open:
            print(f"[{self.send_gcode.__name__}] Firmware not connected")
            return False

        try:
            self.ser.write(cmd.encode())
            print("Sent:", cmd.strip())
            return True

        except Exception as e:
            print("Connection lost:", e)
            self.ser = None
            return False

    # -----------------------
    # WAIT FOR OK RESPONSE
    # -----------------------
    def wait_for_ok(self, timeout=10):
        """
        Waits for Marlin to respond with 'ok'.
        Returns True if 'ok' is received within timeout, False otherwise.
        """
        if not self.ser or not self.ser.is_open:
            print(f"[{self.wait_for_ok.__name__}] Firmware not connected")
            return False

        start_time = time.time()
        buffer = ""

        while True:
            if time.time() - start_time > timeout:
                print("Timeout waiting for 'ok'")
                return False

            line = self.ser.readline().decode(errors="ignore").strip()
            if line:
                print("Marlin:", line)  # optional debug
                buffer += line
                if "ok" in line.lower():
                    return True

    # -----------------------
    # SAVE DOSING & BUILD CALIBRATION VALUES
    # -----------------------
    def save_positions(self):
        with open("calibration_data.txt", "w") as file:
            file.write(f"{dosing_min_position}\n")
            file.write(f"{dosing_max_position}\n")
            file.write(f"{build_min_position}\n")
            file.write(f"{build_max_position}\n")

    # -----------------------
    # LOAD DOSING & BUILD CALIBRATION VALUES
    # -----------------------
    def load_positions(self):
        global dosing_min_position, dosing_max_position, build_min_position, build_max_position
        try:
            with open("calibration_data.txt", "r") as file:
                dosing_min_position = float(file.readline().strip())
                dosing_max_position = float(file.readline().strip())
                build_min_position = float(file.readline().strip())
                build_max_position = float(file.readline().strip())
        except FileNotFoundError:
            # If no file exists, initialize to defaults (e.g., 0)
            dosing_min_position = 0
            dosing_max_position = 0
            build_min_position = 0
            build_max_position = 0
        print("Positions loaded:", dosing_min_position, dosing_max_position, build_min_position, build_max_position)
        # Print the loaded values for verification
        print(f"Loaded positions: Dosing Min: {dosing_min_position}, Dosing Max: {dosing_max_position}")
        print(f"Build Min: {build_min_position}, Build Max: {build_max_position}")