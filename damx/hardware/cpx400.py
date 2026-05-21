import socket
import time


class CPX400DP:
    """
    TCP/IP driver for TTi CPX400DP (LXI, port 9221).
    """

    def __init__(self, ip: str, port: int = 9221, delay: float = 0.05, timeout: float = 2.0, retries: int = 3):
        self.ip = ip
        self.port = port
        self.delay = delay
        self.timeout = timeout
        self.retries = retries

    def _send(self, cmd: str, expect_reply=None) -> str:
        cmd = cmd.strip()
        if expect_reply is None:
            expect_reply = cmd.endswith("?")

        time.sleep(self.delay)
        last_err = None

        for _ in range(self.retries):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(self.timeout)
                    s.connect((self.ip, self.port))
                    s.sendall((cmd + "\n").encode())

                    if expect_reply:
                        data = s.recv(4096)
                        return data.decode().strip()
                    else:
                        return ""

            except (ConnectionRefusedError, TimeoutError, OSError) as e:
                last_err = e
                time.sleep(self.delay)

        raise RuntimeError(f"CPX400DP not accepting connections for '{cmd}': {last_err}")

    # ------------------------------------------------------------
    # Identification
    # ------------------------------------------------------------
    def idn(self) -> str:
        return self._send("*IDN?")

    def address(self) -> str:
        return self._send("ADDRESS?")

    # ------------------------------------------------------------
    # Locking / Local
    # ------------------------------------------------------------
    def lock(self) -> int:
        return int(self._send("IFLOCK", expect_reply=True))

    def unlock(self) -> int:
        return int(self._send("IFUNLOCK", expect_reply=True))

    def go_local(self) -> None:
        self._send("LOCAL", expect_reply=False)

    # ------------------------------------------------------------
    # Voltage / Current Setpoints
    # ------------------------------------------------------------
    def set_voltage(self, channel: int, volts: float) -> None:
        """Set constant voltage on a channel (fixed at 12V for this laser)."""
        cmd = f"V{channel} {volts:.3f}"
        print(f"  → Setting V{channel} = {volts:.3f} V")
        self._send(cmd, expect_reply=False)

    def set_current(self, channel: int, amps: float) -> None:
        """Set constant current on a channel."""
        print(f"  → Setting I{channel} = {amps:.2f} A")
        self._send(f"I{channel} {amps}", expect_reply=False)

    def read_current(self, channel: int) -> float:
        response = self._send(f"I{channel}O?", expect_reply=True)
        try:
            return float(response.replace("A", ""))
        except ValueError:
            print(f"  ⚠️ Could not parse current readback for channel {channel}: '{response}'")
            return -1.0

    # ------------------------------------------------------------
    # Output Control
    # ------------------------------------------------------------
    def output_on(self, channel: int) -> None:
        print(f"  → Turning ON channel {channel}")
        self._send(f"OP{channel} 1", expect_reply=False)

    def output_off(self, channel: int) -> None:
        print(f"  → Turning OFF channel {channel}")
        self._send(f"OP{channel} 0", expect_reply=False)


# ------------------------------------------------------------
# Constant voltage (12V) with stepping current loop for laser diode
# ------------------------------------------------------------
if __name__ == "__main__":
    psu = CPX400DP("192.168.0.100")

    print("Connecting to CPX400DP...\n")
    print("IDN:", psu.idn())
    print("Address:", psu.address())

    print("\nLocking interface...")
    print("IFLOCK:", psu.lock())

    # Fixed voltage for the laser diode
    fixed_voltage = 12.0
    # Current steps in Amps
    current_steps = [0.5, 1.0, 1.5, 2.0, 2.5]

    print("\nStarting constant-voltage, stepping-current loop on BOTH channels...\n")

    for step, current in enumerate(current_steps, start=1):
        print(f"===== Step {step} / {len(current_steps)}: Setting current {current} A =====")

        # ---- CHANNEL 1 ----
        print("Channel 1:")
        psu.set_voltage(1, fixed_voltage)
        psu.set_current(1, current)
        psu.output_on(1)

        # ---- CHANNEL 2 ----
        print("Channel 2:")
        psu.set_voltage(2, fixed_voltage)
        psu.set_current(2, current)
        psu.output_on(2)

        print("  → Holding for 15 seconds...")
        time.sleep(15)

        # Read currents after hold
        i1 = psu.read_current(1)
        i2 = psu.read_current(2)
        print(f"  → Current after hold - CH1: {i1:.3f} A, CH2: {i2:.3f} A")

        print("Turning both channels OFF...")
        psu.output_off(1)
        psu.output_off(2)

        print("  → Waiting 0.5 seconds before next step...\n")
        time.sleep(0.5)

    print("Unlocking interface...")
    print("IFUNLOCK:", psu.unlock())

    print("\nReturning to LOCAL mode...")
    psu.go_local()

    print("\nDone.")