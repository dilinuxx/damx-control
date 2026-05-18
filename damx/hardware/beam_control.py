import socket
import time
from PyQt5.QtCore import QObject, pyqtSignal


# =========================================================
# LOW LEVEL: TCP CONTROL
# =========================================================
class BeamControl:

    def __init__(self, host="boris.shef.ac.uk", port=51003):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(5)
        self.sock.connect((self.host, self.port))

        response = self._recv()
        print("Server:", response)
        return response

    def disconnect(self):
        if self.sock:
            try:
                self.send_command("BYE")
            except:
                pass

            self.sock.close()
            self.sock = None

    def _recv(self):
        try:
            data = self.sock.recv(1024)
            return data.decode().strip()
        except socket.timeout:
            return "TIMEOUT"
        except Exception as e:
            return f"ERROR: {e}"

    def send_command(self, command):
        if not self.sock:
            raise RuntimeError("Not connected to Boris")

        formatted = f"#{len(command):03d}{command}"
        print("Sending:", formatted)

        try:
            self.sock.sendall(formatted.encode())
            response = self._recv()
            print("Response:", response)
            return response
        except Exception as e:
            return f"ERROR: {e}"

    # -----------------------
    # COMMANDS
    # -----------------------
    def ping(self):
        return self.send_command("PING")

    def build(self):
        return self.send_command("BUILD")

    def connect_device(self, device_id):
        return self.send_command(f"CONDEV{device_id:04d}")

    def disconnect_device(self, device_id):
        return self.send_command(f"DISDEV{device_id:04d}")

    def connect_all(self):
        return self.send_command("CONALL")

    def disconnect_all(self):
        return self.send_command("DISALL")

    def how_connected(self):
        return self.send_command("HOWCON")

    def set_current(self, device_id, laser_id, current_ma):
        cmd = f"SETCURR{device_id:04d}{laser_id:02d}{current_ma:04d}"
        return self.send_command(cmd)


# =========================================================
# HIGH LEVEL: ASYNC WORKER
# =========================================================
class BeamWorker(QObject):

    connected = pyqtSignal(bool)
    error = pyqtSignal(str)
    status_update = pyqtSignal(str)

    def __init__(self, host="boris.shef.ac.uk", port=51003):
        super().__init__()
        self.beam = BeamControl(host, port)
        self.running = False

    # -----------------------
    # CONNECTION
    # -----------------------
    def connect_boris(self):
        try:
            res = self.beam.connect()

            if "HELLO" in res:
                self.connected.emit(True)
                self.running = True
                self._poll_loop()
            else:
                self.error.emit(res)
                self.connected.emit(False)

        except Exception as e:
            self.error.emit(str(e))
            self.connected.emit(False)

    def disconnect_boris(self):
        self.running = False
        self.beam.disconnect()
        self.connected.emit(False)

    # -----------------------
    # LASER CONTROL
    # -----------------------
    def set_current(self, device_id, laser_id, current):
        try:
            res = self.beam.set_current(device_id, laser_id, current)

            if "ERR" in res:
                self.error.emit(res)

        except Exception as e:
            self.error.emit(str(e))

    # -----------------------
    # STATUS LOOP
    # -----------------------
    def _poll_loop(self):
        while self.running:
            try:
                res = self.beam.how_connected()
                self.status_update.emit(res)
                time.sleep(2)
            except Exception as e:
                self.error.emit(str(e))
                self.running = False