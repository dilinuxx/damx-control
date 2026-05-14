"""
Chamber Hardware Abstraction Layer (HAL)
========================================

This module implements a hardware abstraction layer (HAL) for controlling
an environmental process chamber through Marlin firmware using G-code
commands transmitted over a serial interface.

The abstraction layer provides high-level methods for operating chamber
subsystems including:

- Vacuum pump control
- Vacuum valve actuation
- Argon gas flow management
- Chamber purge operations
- Chamber venting and sealing sequences

The implementation encapsulates low-level Marlin `M42` pin-control
commands behind descriptive Python methods, improving readability,
maintainability, and system safety in automated workflows.

The module is intended for laboratory automation systems, inert-atmosphere
processing chambers, powder-handling platforms, and other digital
fabrication environments requiring programmable environmental control.

Classes
-------
ChamberControl
    High-level interface for chamber pneumatic and gas-handling operations.

Dependencies
------------
This module requires an initialized controller object capable of sending
G-code commands to a Marlin-compatible firmware controller.

Example
-------
- >>> chamber = ChamberControl(controller)
- >>> chamber.start_purge()
- >>> chamber.vacuum_on()

Notes
-----
The implementation assumes that Marlin firmware is configured to allow
direct GPIO pin manipulation using the `M42` command. Pin assignments
must correspond to the target hardware configuration.
"""

# chamber.py

class ChamberControl:

    def __init__(self, controller):
        self.controller = controller

    def send(self, gcode):
        self.controller.send_gcode(gcode + "\n")

    # ---------------------------
    # VACUUM PUMP (P8)
    # ---------------------------
    def vacuum_on(self):
        self.send("M42 P8 S255")

    def vacuum_off(self):
        self.send("M42 P8 S0")

    # ---------------------------
    # VACUUM VALVE (P59)
    # ---------------------------
    def vacuum_valve_open(self):
        self.send("M42 P59 S255")

    def vacuum_valve_close(self):
        self.send("M42 P59 S0")

    # ---------------------------
    # ARGON PUMP (P7)
    # ---------------------------
    def argon_on(self):
        self.send("M42 P7 S255")

    def argon_off(self):
        self.send("M42 P7 S0")

    # ---------------------------
    # ARGON INLET VALVE (P58)
    # ---------------------------
    def argon_inlet_open(self):
        self.send("M42 P58 S255")

    def argon_inlet_close(self):
        self.send("M42 P58 S0")

    # ---------------------------
    # ARGON OUTLET VALVE (P57)
    # ---------------------------
    def argon_outlet_open(self):
        self.send("M42 P57 S255")

    def argon_outlet_close(self):
        self.send("M42 P57 S0")

    # ---------------------------
    # SYSTEM OPERATIONS (Optional logic)
    # ---------------------------
    def start_purge(self):
        # Example purge sequence (adjust to your system)
        self.argon_on()
        self.argon_inlet_open()
        self.argon_outlet_open()

    def stop_purge(self):
        self.argon_inlet_close()
        self.argon_outlet_close()
        self.argon_off()

    def vent_chamber(self):
        self.vacuum_off()
        self.vacuum_valve_close()
        self.argon_inlet_open()

    def seal_chamber(self):
        self.argon_inlet_close()
        self.argon_outlet_close()
        self.vacuum_valve_close()