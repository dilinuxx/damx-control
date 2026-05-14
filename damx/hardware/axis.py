"""
Axis Motion Control Interface
=============================

This module provides a high-level motion-control interface for operating
Cartesian machine axes through Marlin firmware using G-code commands.

The implementation abstracts low-level motion commands into reusable
Python methods for incremental positioning and homing operations. It is
designed for laboratory automation systems, robotic platforms, and
digital fabrication equipment requiring programmable axis control.

Features
--------
- Relative incremental motion control
- Positive and negative movement along X, Y, and Z axes
- Configurable movement step size
- Machine homing operations using Marlin `G28`
- Integration with graphical user interface (GUI) step selectors

The module uses relative positioning (`G91`) for controlled incremental
movement and restores absolute positioning mode (`G90`) after each
operation to maintain predictable machine-state behavior.

Classes
-------
AxisControl
    High-level interface for Cartesian axis movement and homing.

Dependencies
------------
This module requires:
- A controller object capable of transmitting G-code commands
- A GUI-compatible step selector object implementing `currentText()`

Example
-------
- >>> axis = AxisControl(controller, step_selector)
- >>> axis.move_x_plus()
- >>> axis.move_z_minus()
- >>> axis.home_all()

Notes
-----
Movement distances are dynamically obtained from the user-interface step
selector and interpreted as machine units configured in Marlin firmware
(typically millimeters).

Care should be taken to ensure that all commanded movements remain within
the safe operating limits of the mechanical system.
"""

# axis.py

class AxisControl:

    def __init__(self, controller, step_selector):
        self.controller = controller
        self.step_selector = step_selector

    def get_step(self):
        text = self.step_selector.currentText()
        return float(text.split()[0])

    def move_x_plus(self):
        step = self.get_step()
        self.controller.send_gcode(f"G91\nG0 X{step}\nG90\n")

    def move_x_minus(self):
        step = self.get_step()
        self.controller.send_gcode(f"G91\nG0 X-{step}\nG90\n")

    def move_y_plus(self):
        step = self.get_step()
        self.controller.send_gcode(f"G91\nG0 Y{step}\nG90\n")

    def move_y_minus(self):
        step = self.get_step()
        self.controller.send_gcode(f"G91\nG0 Y-{step}\nG90\n")

    def move_z_plus(self):
        step = self.get_step()
        self.controller.send_gcode(f"G91\nG0 Z{step}\nG90\n")

    def move_z_minus(self):
        step = self.get_step()
        self.controller.send_gcode(f"G91\nG0 Z-{step}\nG90\n")

    def home_all(self):
        self.controller.send_gcode("G28\n")