"""
Glove Controller — reads IMU (MPU6050 / ICM-42688) data from wrist MCU.
Protocol: JSON over Serial (same as arm but different port).

Expected JSON from glove MCU:
  {"ax":0.1,"ay":9.7,"az":0.3,"gx":0.01,"gy":0.0,"gz":0.0,
   "pinch":false,"fist":false,"point":false}

Computes:
  • Orientation quaternion via Madgwick filter
  • Wrist position (relative, via double integration with drift correction)
  • Gesture recognition (pinch = set waypoint, fist = execute, point = stop)
"""

import numpy as np
import threading
import serial
import json
import time
import logging
from dataclasses import dataclass, field
from typing import Optional, Callable

log = logging.getLogger("glove")


# ─── Madgwick AHRS filter ─────────────────────────────────────────────────────

class MadgwickFilter:
    """
    Lightweight Madgwick AHRS.
    beta: algorithm gain (higher = faster convergence, noisier).
    """

    def __init__(self, beta: float = 0.1, sample_rate: float = 50.0):
        self.beta = beta
        self.dt = 1.0 / sample_rate
        self.q = np.array([1.0, 0.0, 0.0, 0.0])   # w x y z

    def update(self, accel: np.ndarray, gyro: np.ndarray) -> np.ndarray:
        q = self.q
        ax, ay, az = accel / (np.linalg.norm(accel) + 1e-10)
        gx, gy, gz = gyro

        # Gradient descent step
        q1, q2, q3, q4 = q
        _2q1 = 2 * q1; _2q2 = 2 * q2; _2q3 = 2 * q3; _2q4 = 2 * q4
        _4q1 = 4 * q1; _4q2 = 4 * q2; _4q3 = 4 * q3
        _8q2 = 8 * q2; _8q3 = 8 * q3
        q1q1 = q1 * q1; q2q2 = q2 * q2; q3q3 = q3 * q3; q4q4 = q4 * q4

        s1 = _4q1 * q3q3 + _2q3 * ax + _4q1 * q2q2 - _2q2 * ay
        s2 = _4q2 * q4q4 - _2q4 * ax + 4*q1q1*q2 - _2q1*ay - _4q2 + _8q2*q2q2 + _8q2*q3q3 + _4q2*az
        s3 = 4*q1q1*q3 + _2q1*ax + _4q3*q4q4 - _2q4*ay - _4q3 + _8q3*q2q2 + _8q3*q3q3 + _4q3*az
        s4 = 4*q2q2*q4 - _2q2*ax + 4*q3q3*q4 - _2q3*ay
        norm_s = np.sqrt(s1**2 + s2**2 + s3**2 + s4**2) + 1e-10
        s1 /= norm_s; s2 /= norm_s; s3 /= norm_s; s4 /= norm_s

        # Rate of change of quaternion from gyroscope
        qDot1 = 0.5 * (-q2*gx - q3*gy - q4*gz) - self.beta * s1
        qDot2 = 0.5 * ( q1*gx + q3*gz - q4*gy) - self.beta * s2
        qDot3 = 0.5 * ( q1*gy - q2*gz + q4*gx) - self.beta * s3
        qDot4 = 0.5 * ( q1*gz + q2*gy - q3*gx) - self.beta * s4

        q += self.dt * np.array([qDot1, qDot2, qDot3, qDot4])
        self.q = q / (np.linalg.norm(q) + 1e-10)
        return self.q

    def to_euler(self) -> np.ndarray:
        """Returns [roll, pitch, yaw] in radians."""
        q = self.q
        w, x, y, z = q
        roll  = np.arctan2(2*(w*x + y*z), 1 - 2*(x*x + y*y))
        pitch = np.arcsin(np.clip(2*(w*y - z*x), -1, 1))
        yaw   = np.arctan2(2*(w*z + x*y), 1 - 2*(y*y + z*z))
        return np.array([roll, pitch, yaw])


# ─── Gesture recogniser ───────────────────────────────────────────────────────

class GestureType:
    NONE    = "none"
    PINCH   = "pinch"    # set waypoint
    FIST    = "fist"     # execute trajectory
    POINT   = "point"    # emergency stop
    WAVE    = "wave"     # wave motion mode


@dataclass
class GestureEvent:
    gesture: str
    timestamp: float = field(default_factory=time.time)
    position: Optional[np.ndarray] = None   # XYZ at gesture moment


# ─── Glove pose ───────────────────────────────────────────────────────────────

@dataclass
class GlovePose:
    quaternion: np.ndarray = field(default_factory=lambda: np.array([1., 0., 0., 0.]))
    euler: np.ndarray = field(default_factory=lambda: np.zeros(3))
    accel: np.ndarray = field(default_factory=lambda: np.zeros(3))
    gyro: np.ndarray = field(default_factory=lambda: np.zeros(3))
    gesture: str = GestureType.NONE
    timestamp: float = field(default_factory=time.time)


# ─── Main glove reader ────────────────────────────────────────────────────────

class GloveController:
    def __init__(
        self,
        port: str = "AUTO",
        baud: int = 115200,
        on_pose: Optional[Callable[[GlovePose], None]] = None,
        on_gesture: Optional[Callable[[GestureEvent], None]] = None,
    ):
        self.port = port
        self.baud = baud
        self.on_pose = on_pose
        self.on_gesture = on_gesture

        self.filter = MadgwickFilter(beta=0.08, sample_rate=50.0)
        self.pose = GlovePose()
        self._prev_gesture = GestureType.NONE
        self._connected = False
        self._ser: Optional[serial.Serial] = None
        self._stop = threading.Event()

        # Waypoints set by glove
        self.waypoints: list[np.ndarray] = []

    def connect(self, port: Optional[str] = None) -> bool:
        if port:
            self.port = port
        if self.port == "AUTO":
            # Find second serial port (arm uses first)
            from core.transport import SerialTransport
            ports = SerialTransport.list_ports()
            self.port = ports[1] if len(ports) > 1 else (ports[0] if ports else None)
            if not self.port:
                log.warning("No glove port found.")
                return False
        try:
            self._ser = serial.Serial(self.port, self.baud, timeout=0.1)
            self._connected = True
            self._stop.clear()
            t = threading.Thread(target=self._read_loop, daemon=True)
            t.start()
            log.info(f"Glove connected: {self.port}")
            return True
        except Exception as e:
            log.error(f"Glove connect failed: {e}")
            return False

    def disconnect(self):
        self._stop.set()
        self._connected = False
        if self._ser and self._ser.is_open:
            self._ser.close()

    @property
    def connected(self):
        return self._connected

    def _read_loop(self):
        buf = ""
        while not self._stop.is_set() and self._connected:
            try:
                raw = self._ser.read(256)
                if not raw:
                    continue
                buf += raw.decode(errors="replace")
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    self._parse(line.strip())
            except Exception as e:
                log.error(f"Glove RX: {e}")
                time.sleep(0.1)

    def _parse(self, line: str):
        if not line:
            return
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            return

        accel = np.array([d.get("ax", 0), d.get("ay", 9.81), d.get("az", 0)])
        gyro  = np.array([d.get("gx", 0), d.get("gy", 0), d.get("gz", 0)])

        q = self.filter.update(accel, gyro)
        euler = self.filter.to_euler()

        gesture = GestureType.NONE
        if d.get("pinch"):   gesture = GestureType.PINCH
        elif d.get("fist"):  gesture = GestureType.FIST
        elif d.get("point"): gesture = GestureType.POINT
        elif d.get("wave"):  gesture = GestureType.WAVE

        self.pose = GlovePose(
            quaternion=q.copy(),
            euler=euler.copy(),
            accel=accel.copy(),
            gyro=gyro.copy(),
            gesture=gesture,
        )

        if self.on_pose:
            self.on_pose(self.pose)

        # Gesture event — only on leading edge
        if gesture != GestureType.NONE and gesture != self._prev_gesture:
            evt = GestureEvent(gesture=gesture)
            log.info(f"Gesture: {gesture}")
            if self.on_gesture:
                self.on_gesture(evt)
        self._prev_gesture = gesture


class MockGloveController:
    """Simulates glove input with synthetic IMU motion (sine waves)."""

    def __init__(
        self,
        on_pose: Optional[Callable] = None,
        on_gesture: Optional[Callable] = None,
    ):
        self.on_pose = on_pose
        self.on_gesture = on_gesture
        self._connected = True
        self._t = 0.0
        self.pose = GlovePose()
        self.waypoints: list[np.ndarray] = []
        t = threading.Thread(target=self._loop, daemon=True)
        t.start()

    @property
    def connected(self):
        return self._connected

    def connect(self, port=None):
        return True

    def disconnect(self):
        self._connected = False

    def _loop(self):
        while self._connected:
            self._t += 0.02
            roll  = 0.4 * np.sin(self._t * 0.7)
            pitch = 0.3 * np.sin(self._t * 1.1)
            yaw   = 0.5 * np.sin(self._t * 0.4)
            self.pose = GlovePose(
                euler=np.array([roll, pitch, yaw]),
                quaternion=np.array([1, 0, 0, 0]),
            )
            if self.on_pose:
                self.on_pose(self.pose)
            time.sleep(0.02)
