import re
import time
from PyQt5.QtWidgets import QLabel
import utils.config as config


class BuildExecutor:

    def __init__(self):
        super().__init__()
        self.paused = False
        self.abort = False

    def _wait_if_paused(self):
        while self.paused:
            time.sleep(0.1)
    # ============================================================
    # LOAD / PARSE SLICER GCODE FILE
    # ============================================================
    def load_build_file(self, filepath):

        layers = []
        current_layer = None

        with open(filepath, "r") as f:

            for raw in f:

                line = raw.strip()

                # ---------------- LAYER START ----------------
                if line.startswith("; ===== Layer"):

                    match = re.search(r'Layer\s+(\d+)\s+Z=([-\d\.]+)', line)

                    if match:

                        if current_layer:
                            layers.append(current_layer)

                        current_layer = {
                            "layer": int(match.group(1)),
                            "z": float(match.group(2)),
                            "commands": [],
                            "scan_time": 0.0,
                        }

                # ---------------- FIX 1: CAPTURE ALL G1 MOTION ----------------
                elif line.startswith("G1"):

                    if current_layer is not None:
                        current_layer["commands"].append(line)

                # ---------------- LAYER TIME ----------------
                elif "; Layer Time:" in line:

                    if current_layer is not None:

                        time_match = re.search(r'Layer Time:\s+([-\d\.]+)', line)

                        if time_match:
                            current_layer["scan_time"] = float(time_match.group(1))

        if current_layer:
            layers.append(current_layer)

        print(f"[PARSER] Parsed {len(layers)} layers.")
        return layers

    # ============================================================
    # MAP PART COORDS TO MACHINE COORDS
    # ============================================================
    def map_to_machine_coords(self, line):

        x_match = re.search(r'X([-\d\.]+)', line)
        y_match = re.search(r'Y([-\d\.]+)', line)

        if x_match:
            x_val = float(x_match.group(1))
            machine_x = config.CUBE_CENTER_X + x_val

            line = re.sub(
                r'X([-\d\.]+)',
                f'X{machine_x:.4f}',
                line
            )

        if y_match:
            y_val = float(y_match.group(1))
            machine_y = config.CUBE_CENTER_Y + y_val

            line = re.sub(
                r'Y([-\d\.]+)',
                f'Y{machine_y:.4f}',
                line
            )

        return line

    # ============================================================
    # TRANSLATE DIODE COMMAND
    # ============================================================
    def translate_diode_command(self, line):

        diode_match = re.search(r'(DIODE\d+)', line)

        diode_cmd = ""

        if diode_match:

            diode = diode_match.group(1)

            DIODE_MAP = {
                "DIODE1": "M1001",
                "DIODE2": "M1002",
                "DIODE3": "M1003",
                "DIODE4": "M1004",
                "DIODE5": "M1005",
                "DIODE6": "M1006",
                "DIODE7": "M1007",
                "DIODE8": "M1008",
                "DIODE9": "M1009",
                "DIODE10": "M1010",
            }

            diode_cmd = DIODE_MAP.get(diode, "")
            line = line.replace(diode, "").strip()

        return diode_cmd, line


    # ============================================================
    # POWDER CYCLE (UNCHANGED LOGIC, ONLY SAFETY ORDERING FIX)
    # ============================================================
    def execute_powder_cycle(self, layer_number):

        print(f"[LAYER {layer_number}] Starting powder cycle.")

        # DOSING UP
        self.controller.send_gcode(f"{config.TOOL_DOSING_PISTON}\n")
        self.controller.wait_for_ok()
        self._wait_if_paused()

        self.controller.send_gcode("M17\n"); self.controller.wait_for_ok()
        self._wait_if_paused()
        self.controller.send_gcode("G91\n"); self.controller.wait_for_ok()
        self._wait_if_paused()
        self.controller.send_gcode("M83\n"); self.controller.wait_for_ok()
        self._wait_if_paused()

        dose_move_val = (
            config.DIRECTION_DOSE_UP
            * config.LAYER_THICKNESS_MM
            * config.build_dosing_motor_units
        )

        self.controller.send_gcode(f"G1 E{dose_move_val:.3f} F{config.FEEDRATE_PISTONS}\n")
        self.controller.wait_for_ok()

        self.controller.send_gcode("M400\n")
        self.controller.wait_for_ok()

        config.dosing_position += config.DIRECTION_DOSE_UP * config.LAYER_THICKNESS_MM

        # BUILD DOWN
        self.controller.send_gcode(f"{config.TOOL_BUILD_PISTON}\n")
        self.controller.wait_for_ok()

        self.controller.send_gcode("M17\n"); self.controller.wait_for_ok()
        self.controller.send_gcode("G91\n"); self.controller.wait_for_ok()
        self.controller.send_gcode("M83\n"); self.controller.wait_for_ok()

        build_move_val = (
            config.DIRECTION_BUILD_DOWN
            * config.LAYER_THICKNESS_MM
            * config.build_dosing_motor_units
        )

        self.controller.send_gcode(f"G1 E{build_move_val:.3f} F{config.FEEDRATE_PISTONS}\n")
        self.controller.wait_for_ok()

        self.controller.send_gcode("M400\n")
        self.controller.wait_for_ok()

        config.build_position += config.DIRECTION_BUILD_DOWN * config.LAYER_THICKNESS_MM

        self.controller.send_gcode("G90\n"); self.controller.wait_for_ok()
        self.controller.send_gcode("M82\n"); self.controller.wait_for_ok()

        # RECOATER
        self.controller.send_gcode("G91\n"); self.controller.wait_for_ok()

        self.controller.send_gcode(
            f"G0 {config.RECOATER_AXIS}{config.RECOATER_SWEEP_DISTANCE} F{config.FEEDRATE_RECOATER}\n"
        )
        self.controller.wait_for_ok()

        self.controller.send_gcode(
            f"G0 {config.RECOATER_AXIS}{-config.RECOATER_SWEEP_DISTANCE} F{config.FEEDRATE_RECOATER}\n"
        )
        self.controller.wait_for_ok()

        self.controller.send_gcode("M400\n")
        self.controller.wait_for_ok()

    # ============================================================
    # FIX 2: LASER EXECUTION NOW MATCHES START_PRINT BEHAVIOUR
    # ============================================================
    def execute_scan_layer(self, layer):

        layer_number = layer["layer"]

        print(f"[LAYER {layer_number}] Starting laser exposure.")

        self.controller.send_gcode("G90\n")
        self.controller.wait_for_ok()

        # IMPORTANT FIX: force laser-safe state consistency per line
        for raw_cmd in layer["commands"]:

            diode_cmd, motion_cmd = self.translate_diode_command(raw_cmd)

            if diode_cmd:
                self.controller.send_gcode(diode_cmd + "\n")
                #self.controller.wait_for_ok()

            # FIX 3: ignore empty motion lines safely
            motion_cmd = motion_cmd.strip()
            if not motion_cmd:
                continue

            # =====================================================
            # MAP LOCAL PART COORDS -> MACHINE COORDS
            # =====================================================
            motion_cmd = self.map_to_machine_coords(motion_cmd)
            self.controller.send_gcode(motion_cmd + "\n")
            self.controller.wait_for_ok()

        self.controller.send_gcode("M400\n")
        self.controller.wait_for_ok()

        print(f"[LAYER {layer_number}] Laser exposure complete.")


    # ============================================================
    # MACHINE INIT (UNCHANGED BUT SAFE ORDERING)
    # ============================================================
    def initialize_machine(self):

        self.printer_service.pause()
        if hasattr(self, "system_status_label"):
            self.system_status_label.setText("System Status: Building")

        time.sleep(config.INIT_DRAIN_COOLDOWN_S)

        if self.controller.ser and self.controller.ser.is_open:
            self.controller.ser.reset_input_buffer()
            self.controller.ser.reset_output_buffer()

        self.printing = True

        self.controller.send_gcode("M17\n"); self.controller.wait_for_ok()
        self.controller.send_gcode("G90\n"); self.controller.wait_for_ok()
        self.controller.send_gcode("M82\n"); self.controller.wait_for_ok()

        print("[INIT] Machine initialized.")


    # ============================================================
    # SHUTDOWN
    # ============================================================
    def shutdown_machine(self):

        self.printing = False
        self.printer_service.resume()
        if hasattr(self, "system_status_label"):
            self.system_status_label.setText("System Status: Idle")

        print("[COMPLETE] Build cycle concluded safely.")


    # ============================================================
    # MAIN ENTRYPOINT
    # ============================================================
    def start_print(self):

        try:
            self.initialize_machine()

            layers = self.load_build_file(config.BUILD_FILE)

            if not layers:
                print("[ERROR] No valid layers found.")
                return

            print(f"[START] Beginning {len(layers)}-layer build cycle.")

            for layer in layers:

                self._wait_if_paused()
                if self.abort:
                    print("[ABORT] Build stopped.")
                    return

                layer_number = layer["layer"]

                print(f"\n[LAYER {layer_number}] ----------------")

                if not layer["commands"]:
                    print(f"[LAYER {layer_number}] No scan vectors. Skipping.")
                    continue

                self.execute_powder_cycle(layer_number)
                self.execute_scan_layer(layer)

            print("[COMPLETE] All layers executed successfully.")

        except Exception as e:
            print(f"[FATAL ERROR] {str(e)}")

        finally:
            self.shutdown_machine()