"""
config.py

This file contains global configuration variables that store the calibration values
for the dosing and build axes of a 3D printer or similar system. These values are
used to track the positions (minimum and maximum) of the dosing and build actuators.

Global variables include:
- dosing_min_position: Minimum position of the dosing actuator.
- dosing_max_position: Maximum position of the dosing actuator.
- build_min_position: Minimum position of the build actuator.
- build_max_position: Maximum position of the build actuator.

These variables are used by the main control system to manage the positions and movements
of the actuators. The values can be saved and loaded to/from a text file to persist across
system reboots.

Key Features:
- Calibration values for the dosing and build axes.
- Easy access to these global variables throughout the project by importing this file.
- Ability to save and load calibration data from a text file to maintain the state across reboots.

Usage:
To modify or access these values in any part of your program, simply import this file:
    import config

To update the positions, update the variables directly:
    config.dosing_min_position = 0
    config.dosing_max_position += 5

To save the current positions to the text file:
    save_positions()

To load the saved positions from the text file:
    load_positions()

Important Notes:
- These values are global and mutable, which means any part of the program can modify them.
- The `save_positions()` and `load_positions()` functions are designed to handle the reading and writing
  of the values from/to a file (`calibration_data.txt`), ensuring that the calibration persists between sessions.
"""

# Global variables to store the calibration values
dosing_min_position = 0
dosing_max_position = 280 # Dosing Piston size is approximately 280mm
dosing_position = 0
dosing_motor_speed = 1000
build_min_position = 0
build_max_position = 280  # Build Piston size is approximately 280mm
build_position = 0
build_motor_speed = 1000
recoater_motor_speed = 1000
build_dosing_motor_units = 4 # Convert user-scale units to motor controller units
paused_dosing = 0
paused_build = 0