"""
Axis Motion Control Interface
=============================

This module provides a high-level motion-control interface for operating
Cartesian machine axes through Marlin firmware using G-code commands.

The implementation wraps low-level G-code motion primitives into reusable
Python methods for incremental positioning and homing operations. It is
intended for use in laboratory automation systems, robotic platforms, and
digital fabrication equipment requiring programmable axis control.

Features
--------
- Relative incremental motion control along X, Y, and Z axes
- Configurable step-size control via a GUI selector (Qt-based interface)
- Machine homing using Marlin `G28`
- Automatic restoration of absolute positioning mode (`G90`) after motion

Design Note
-----------
Each motion command temporarily switches Marlin into relative positioning
mode (`G91`) to perform an incremental move, then restores absolute mode
(`G90`). This local state encapsulation helps avoid unintended cumulative
state changes in shared or multi-command control workflows.

Classes
-------
AxisControl
    High-level interface for Cartesian axis movement and homing.

Dependencies
------------
- A controller object capable of sending G-code to Marlin firmware
- A Qt-based step selector implementing `currentText()`

Example
-------
- >>> axis = AxisControl(controller, step_selector)
- >>> axis.move_x_plus()
- >>> axis.move_z_minus()
- >>> axis.home_all()

Notes
-----
Movement distances are interpreted in the machine units configured in
Marlin firmware (typically millimeters). Users should ensure that motion
limits are enforced at the application or firmware level to prevent
mechanical collisions.
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