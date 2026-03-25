"""
Serial transport — sends joint commands to ESP32 over UART, receives feedback.
Protocol: JSON lines, 115200 baud.

Outgoing: {"cmd":"move","joints":[j1,j2,j3,j4,j5,j6],"speed":0.5}\n
Incoming: {"joints":[...],"torques":[...],"ok":true}\n
"""

import serial
import serial.tools.list_ports
import threading
import json
import time
import queue
import logging
from typing import Optional, Callable

log = logging.getLogger("transport")


class SerialTransport:
    def __init__(
        self,
        port: str = "AUTO",
        baud: int = 115200,
        on_feedback: Optional[Callable] = None,
    ):
        self.port = port
        self.baud = baud
        self.on_feedback = on_feedback
        self._ser: Optional[serial.Serial] = None
        self._connected = False
        self._rx_thread: Optional[threading.Thread] = None
        self._tx_queue: queue.Queue = queue.Queue(maxsize=32)
        self._tx_thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self.stats = {"sent": 0, "recv": 0, "errors": 0, "latency_ms": 0.0}
        self._last_sent_time = 0.0

    # ── Connection ─────────────────────────────────────────────────────────

    @staticmethod
    def list_ports() -> list[str]:
        ports = serial.tools.list_ports.comports()
        return [p.device for p in ports]

    @staticmethod
    def auto_detect() -> Optional[str]:
        """Find first port that looks like an ESP32/Arduino."""
        keywords = ["CP210", "CH340", "FTDI", "USB", "ACM", "ttyUSB"]
        for p in serial.tools.list_ports.comports():
            desc = (p.description or "") + (p.manufacturer or "")
            if any(k.lower() in desc.lower() for k in keywords):
                return p.device
        ports = serial.tools.list_ports.comports()
        return ports[0].device if ports else None

    def connect(self, port: Optional[str] = None) -> bool:
        if port:
            self.port = port
        if self.port == "AUTO":
            detected = self.auto_detect()
            if not detected:
                log.warning("No serial port found.")
                return False
            self.port = detected
        try:
            self._ser = serial.Serial(
                self.port, self.baud, timeout=0.1, write_timeout=0.5
            )
            self._connected = True
            self._stop.clear()
            self._rx_thread = threading.Thread(target=self._rx_loop, daemon=True)
            self._tx_thread = threading.Thread(target=self._tx_loop, daemon=True)
            self._rx_thread.start()
            self._tx_thread.start()
            log.info(f"Connected to {self.port} @ {self.baud}")
            return True
        except serial.SerialException as e:
            log.error(f"Serial connect failed: {e}")
            return False

    def disconnect(self):
        self._stop.set()
        self._connected = False
        if self._ser and self._ser.is_open:
            self._ser.close()
        log.info("Disconnected.")

    @property
    def connected(self) -> bool:
        return self._connected and bool(self._ser and self._ser.is_open)

    # ── Sending ────────────────────────────────────────────────────────────

    def send_joints(self, angles_rad: list[float], speed: float = 0.5):
        """
        Queue a joint-angle command.
        speed: 0.0 (slowest) → 1.0 (max velocity).
        """
        # Convert rad → degrees for servo firmware
        angles_deg = [round(float(a) * 180 / 3.14159, 2) for a in angles_rad]
        payload = {"cmd": "move", "joints": angles_deg, "speed": round(speed, 3)}
        self._enqueue(payload)

    def send_home(self):
        self._enqueue({"cmd": "home"})

    def send_stop(self):
        # Put at front — clear queue first
        while not self._tx_queue.empty():
            try:
                self._tx_queue.get_nowait()
            except queue.Empty:
                break
        self._enqueue({"cmd": "stop"})

    def _enqueue(self, payload: dict):
        try:
            self._tx_queue.put_nowait(payload)
        except queue.Full:
            # Drop oldest
            try:
                self._tx_queue.get_nowait()
            except queue.Empty:
                pass
            self._tx_queue.put_nowait(payload)

    # ── TX loop ────────────────────────────────────────────────────────────

    def _tx_loop(self):
        while not self._stop.is_set():
            try:
                payload = self._tx_queue.get(timeout=0.05)
                if not self.connected:
                    continue
                line = json.dumps(payload) + "\n"
                self._ser.write(line.encode())
                self._last_sent_time = time.time()
                self.stats["sent"] += 1
            except queue.Empty:
                pass
            except serial.SerialException as e:
                log.error(f"TX error: {e}")
                self.stats["errors"] += 1
                self._connected = False

    # ── RX loop ────────────────────────────────────────────────────────────

    def _rx_loop(self):
        buf = ""
        while not self._stop.is_set():
            if not self.connected:
                time.sleep(0.1)
                continue
            try:
                raw = self._ser.read(256)
                if not raw:
                    continue
                buf += raw.decode(errors="replace")
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        latency = (time.time() - self._last_sent_time) * 1000
                        self.stats["recv"] += 1
                        self.stats["latency_ms"] = round(latency, 1)
                        if self.on_feedback:
                            self.on_feedback(data)
                    except json.JSONDecodeError:
                        pass
            except serial.SerialException as e:
                log.error(f"RX error: {e}")
                self._connected = False
                time.sleep(0.5)


class MockTransport:
    """
    Drop-in replacement for SerialTransport — simulates arm response.
    Perfect for dev/testing without hardware.
    """

    def __init__(self, on_feedback: Optional[Callable] = None):
        self.on_feedback = on_feedback
        self._connected = True
        self._angles = [0.0] * 6
        self.stats = {"sent": 0, "recv": 0, "errors": 0, "latency_ms": 4.0}
        self._thread = threading.Thread(target=self._simulate, daemon=True)
        self._thread.start()

    @property
    def connected(self):
        return self._connected

    def connect(self, port=None):
        return True

    def disconnect(self):
        self._connected = False

    def send_joints(self, angles_rad: list[float], speed: float = 0.5):
        # Smooth approach
        target = list(angles_rad)
        alpha = min(1.0, speed * 0.4 + 0.1)
        self._angles = [
            self._angles[i] * (1 - alpha) + target[i] * alpha
            for i in range(6)
        ]
        self.stats["sent"] += 1

    def send_home(self):
        self._angles = [0.0] * 6

    def send_stop(self):
        pass

    def _simulate(self):
        while self._connected:
            time.sleep(0.05)
            if self.on_feedback:
                self.on_feedback({
                    "joints": [round(a, 4) for a in self._angles],
                    "torques": [round(abs(a) * 0.3, 3) for a in self._angles],
                    "ok": True,
                })
            self.stats["recv"] += 1

    @staticmethod
    def list_ports():
        return ["MOCK (simulation)"]
