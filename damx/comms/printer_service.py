"""
Printer Service (Qt Communication Layer)
========================================

This module implements a Qt-based communication service that acts as a
runtime bridge between the user interface layer and a Marlin-based
hardware controller.

The service is responsible for non-blocking serial communication,
periodic heartbeat polling, and lightweight parsing of firmware status
messages. It operates above the low-level `MarlinController` transport
layer and below the graphical user interface, providing a reactive
event-driven interface via Qt signals.

Responsibilities
----------------
- Periodic heartbeat transmission to the firmware (non-blocking QTimer)
- Asynchronous reading of serial data from Marlin firmware
- Incremental buffering and parsing of incoming messages
- Emission of structured data updates to the UI layer
- Emission of debug/logging messages for runtime diagnostics

Signal Interface
-----------------
data_updated(dict)
    Emitted when parsed telemetry data is successfully extracted from
    firmware responses.

log(str)
    Emits diagnostic or debugging messages for UI or console display.

Design Notes
-------------
The service uses a QTimer-based polling loop instead of blocking reads
to ensure responsiveness within the Qt event loop. Incoming serial data
is buffered incrementally to handle partial message fragments, with
message boundaries inferred from firmware "ok" responses.

The communication pattern is designed for Marlin-style streaming
protocols where commands are acknowledged asynchronously.

Dependencies
------------
- PyQt5 (QObject, QTimer, pyqtSignal)
- A controller implementing a `send_gcode()` method and exposing a
  `serial.Serial`-like interface (`ser` attribute)

Example
-------
- >>> service = PrinterService(controller)
- >>> service.start()

Notes
-----
This module assumes that firmware responses may be asynchronous and
non-deterministic in timing. As such, parsing logic is intentionally
defensive and tolerant to partial or malformed messages.
"""

from PyQt5.QtCore import QObject, pyqtSignal, QTimer
import time
import utils.config as config

class PrinterService(QObject):
    data_updated = pyqtSignal(dict)   # send parsed data to UI
    log = pyqtSignal(str)             # optional debug signal

    def __init__(self, controller, poll_interval=config.HEARTBEAT_INTERVAL_MS):
        """
        :param controller: MarlinController
        :param poll_interval: milliseconds (Qt uses ms!)
        """
        super().__init__()
        self.controller = controller
        self.poll_interval = poll_interval

        self.timer = QTimer()
        self.timer.timeout.connect(self.heartbeat)

        # Initialize the buffer here
        self._rx_buffer = ""
        self.paused = False

    # -----------------------
    # START / STOP (NON-BLOCKING)
    # -----------------------
    def start(self):
        self.timer.start(self.poll_interval)

    def stop(self):
        self.timer.stop()

    # -----------------------
    # HEARTBEAT (NON-BLOCKING)
    # -----------------------
    def heartbeat(self):
        if self.paused:
            return

        if not self.controller or not self.controller.ser or not self.controller.ser.is_open:
            self.log.emit("Printer not connected.")
            return

        if self.controller.send_gcode(config.HEARTBEAT_COMMAND):
            self.log.emit("Heartbeat sent")

            start_time = time.time()

            while time.time() - start_time < config.HEARTBEAT_READ_WINDOW_S:
                if self.controller.ser.in_waiting:
                    # Read raw bytes, NOT readline
                    chunk = self.controller.ser.read(self.controller.ser.in_waiting).decode(errors="ignore")
                    self._rx_buffer += chunk

                    # Process complete messages ending with "ok"
                    while "ok" in self._rx_buffer:
                        msg, self._rx_buffer = self._rx_buffer.split("ok", 1)
                        msg = msg.strip()

                        if msg:
                            self.log.emit(f"[RX] {msg}")

                            data = self.parse_status(msg)
                            if data:
                                self.data_updated.emit(data)
                else:
                    break
        else:
            self.log.emit("Failed to send heartbeat")

    def pause(self):
        self.paused = True
        # Clear Python's internal string processing buffer
        self._rx_buffer = ""

        # Flush the physical hardware serial buffers
        if self.controller and self.controller.ser and self.controller.ser.is_open:
            self.controller.ser.reset_input_buffer()
            self.controller.ser.reset_output_buffer()

        self.log.emit("PrinterService paused and serial buffers flushed.")

    def resume(self):
        self.paused = False
        self.log.emit("PrinterService resumed")

    # -----------------------
    # PARSE STATUS RESPONSE
    # -----------------------
    def parse_status(self, line):
        data = {}

        try:
            # Normalize common formatting issues
            line = line.replace("ok", " ok")

            if "O2:" in line:
                o2_part = line.split("O2:", 1)[1].strip()
                if o2_part:
                    try:
                        data["o2"] = float(o2_part.split()[0])
                    except (ValueError, IndexError):
                        pass  # incomplete or malformed

            if "P:" in line:
                p_part = line.split("P:", 1)[1].strip()
                if p_part:
                    try:
                        data["pressure"] = float(p_part.split()[0])
                    except (ValueError, IndexError):
                        pass

        except Exception as e:
            self.log.emit(f"Parse error: {e}")

        return data