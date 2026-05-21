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

HEARTBEAT_INTERVAL_MS = 5000
HEARTBEAT_READ_WINDOW_S = 0.2

HEARTBEAT_COMMAND = "M621\n"

# =====================================================================
# DAM AUTOMATION CONFIGURATION SETTINGS
# =====================================================================

# 1. Print Cycle Architecture
TOTAL_LAYERS = 10                  # Total programmatic loop layers
LAYER_THICKNESS_MM = 1.0           # Height delta per layer for powder dosing/building

# 2. Hardware Tool Routing Identifiers
TOOL_BUILD_PISTON = "T0"           # Marlin extruder index for build piston
TOOL_DOSING_PISTON = "T1"          # Marlin extruder index for dosing piston
RECOATER_AXIS = "Z"                # Linear hardware axis for physical recoater travel

# 3. Hardware Feedrates (mm/min)
FEEDRATE_PISTONS = 1500            # Piston motor travel velocity
FEEDRATE_RECOATER = 8000           # Recoater blade speed

# 4. Initialization Settings (mm)
INIT_DRAIN_COOLDOWN_S = 0.2        # Serial settling delay before purge
INIT_DOSE_LOAD_DOWN_MM = 10.0      # Loading powder reservoir draw distance
INIT_DOSE_PREP_UP_MM = 1.0         # Initial push up before layer 1

# 5. Recoater Sweep Architecture (mm)
RECOATER_SWEEP_DISTANCE = 415.0    # Forward push length across powder bed

# 6. Directional Flags (Invert if mechanics change)
DIRECTION_DOSE_UP = -1.0           # Direction multiplier to lift dosing powder
DIRECTION_BUILD_DOWN = 1.0         # Direction multiplier to lower build plate

# 5. Laser Scanning & Optomechanics Profile
LASER_FEEDRATE = 3000              # Velocity during exposure (mm/min)
LASER_TRAVEL_SPEED = 6000          # Velocity during non-exposure transit moves (mm/min)

# ============================================================
# BUILD PLATE GEOMETRY
# ============================================================
BUILD_PLATE_DIAMETER_MM = 80.0
CUBE_CENTER_X = 50.0               # Center physical coordinate of your build piston bed
CUBE_CENTER_Y = 50.0               # Center physical coordinate of your build piston bed
CUBE_SIZE_MM = 2.0                 # Target dimensions of the cube wall profiles
HATCH_SPACING_MM = 0.1             # Overlap path density shift step (laser spot diameter)
BUILD_RADIUS_MM = BUILD_PLATE_DIAMETER_MM / 2.0

# 6. Laser Control Hooks (Marlin customized digital pins or hotend heaters)
LASER_ON_COMMAND = "M3 S255\n"      # Spindle/Laser PWM turn on (or M106 fan control)
LASER_OFF_COMMAND = "M5\n"          # Spindle/Laser cut-off pin command (or M107)