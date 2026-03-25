"""
AI Motion Engine
────────────────
• Generates smooth trajectories between waypoints (cubic spline / SLERP)
• Enforces joint limits and velocity caps
• Detects and logs anomalies (torque spikes, singularities, oscillation)
• Learns preferred motion profiles from history (velocity scaling)
"""

import numpy as np
from scipy.interpolate import CubicSpline
from scipy.spatial.transform import Rotation, Slerp
from dataclasses import dataclass, field
from typing import Optional
import time
import logging

log = logging.getLogger("ai_engine")

# ─── Motion modes ─────────────────────────────────────────────────────────────

class MotionMode:
    LINEAR   = "linear"    # straight line in joint space
    WAVE     = "wave"      # sinusoidal offset along trajectory
    ARC      = "arc"       # arc in XZ plane
    SPLINE   = "spline"    # smooth cubic spline through waypoints
    MIRROR   = "mirror"    # glove mirror mode


@dataclass
class Waypoint:
    angles: np.ndarray
    duration: float = 1.0          # seconds to reach this waypoint
    motion_mode: str = MotionMode.SPLINE
    wave_amp: float = 0.0           # wave amplitude (rad)
    wave_freq: float = 1.0          # wave frequency (Hz)


@dataclass
class Trajectory:
    waypoints: list[Waypoint]
    total_duration: float = 0.0
    generated: bool = False
    timestamps: list[float] = field(default_factory=list)
    samples: list[np.ndarray] = field(default_factory=list)   # dense joint angles

    def __post_init__(self):
        self.total_duration = sum(w.duration for w in self.waypoints)


# ─── Anomaly types ────────────────────────────────────────────────────────────

@dataclass
class Anomaly:
    kind: str
    joint: Optional[int]
    value: float
    timestamp: float = field(default_factory=time.time)
    message: str = ""


# ─── Core engine ─────────────────────────────────────────────────────────────

class AIMotionEngine:
    SAMPLE_RATE = 50        # Hz — trajectory sample density
    TORQUE_WARN = 0.85      # fraction of max torque for warning
    VEL_WARN    = 0.90      # fraction of max velocity for warning

    def __init__(self, arm_model):
        self.arm = arm_model
        self.anomalies: list[Anomaly] = []
        self._motion_memory: list[dict] = []   # completed trajectory stats
        self._velocity_scale = 1.0             # learned scale factor
        self._oscillation_window: list[float] = []

    # ── Trajectory generation ─────────────────────────────────────────────

    def build_trajectory(
        self,
        q_start: np.ndarray,
        q_end: np.ndarray,
        duration: float = 2.0,
        mode: str = MotionMode.SPLINE,
        wave_amp: float = 0.0,
        wave_freq: float = 1.0,
        via_points: Optional[list[np.ndarray]] = None,
    ) -> Trajectory:
        """
        Generate a dense trajectory from q_start → q_end.
        Applies AI-learned velocity scaling and chosen motion mode.
        """
        duration *= (1.0 / max(self._velocity_scale, 0.3))  # AI scaling

        n = max(int(duration * self.SAMPLE_RATE), 10)
        t = np.linspace(0, duration, n)

        if via_points and len(via_points) > 0:
            all_q = [q_start] + list(via_points) + [q_end]
            n_pts = len(all_q)
            t_knots = np.linspace(0, duration, n_pts)
            cs = CubicSpline(t_knots, np.array(all_q))
            samples = cs(t)
        else:
            samples = self._interpolate(q_start, q_end, t, duration, mode)

        # Apply wave overlay
        if mode == MotionMode.WAVE and wave_amp > 0:
            for i in range(len(samples)):
                offset = wave_amp * np.sin(2 * np.pi * wave_freq * t[i])
                # Apply wave to joints 2-4 (shoulder/elbow/wrist)
                samples[i, 1] += offset
                samples[i, 2] -= offset * 0.5

        # Clamp to joint limits
        from core.arm_model import JOINT_LIMITS
        for s in samples:
            for j, (lo, hi) in enumerate(JOINT_LIMITS):
                s[j] = np.clip(s[j], lo, hi)

        # Velocity check
        samples = self._enforce_velocity_limits(samples, duration)

        wp_start = Waypoint(angles=q_start, duration=0)
        wp_end   = Waypoint(angles=q_end, duration=duration, motion_mode=mode,
                            wave_amp=wave_amp, wave_freq=wave_freq)
        traj = Trajectory(waypoints=[wp_start, wp_end], total_duration=duration)
        traj.timestamps = list(t)
        traj.samples = [s.copy() for s in samples]
        traj.generated = True
        return traj

    def _interpolate(
        self, q0: np.ndarray, q1: np.ndarray, t: np.ndarray,
        duration: float, mode: str
    ) -> np.ndarray:
        if mode == MotionMode.LINEAR:
            alpha = t / duration
            return np.outer(1 - alpha, q0) + np.outer(alpha, q1)
        else:
            # Smooth cubic spline with zero-velocity endpoints
            cs = CubicSpline([0, duration], [q0, q1],
                             bc_type=((1, np.zeros(6)), (1, np.zeros(6))))
            return cs(t)

    def _enforce_velocity_limits(
        self, samples: np.ndarray, duration: float
    ) -> np.ndarray:
        from core.arm_model import MAX_VELOCITY
        dt = duration / len(samples)
        for i in range(1, len(samples)):
            dq = samples[i] - samples[i - 1]
            for j in range(6):
                v = abs(dq[j]) / dt
                if v > MAX_VELOCITY[j]:
                    scale = MAX_VELOCITY[j] / v
                    dq[j] *= scale
            samples[i] = samples[i - 1] + dq
        return samples

    # ── Real-time monitoring ───────────────────────────────────────────────

    def check_state(self, joint_angles: np.ndarray, torques: Optional[np.ndarray] = None):
        """Call this on every feedback packet. Logs anomalies."""
        from core.arm_model import JOINT_LIMITS, MAX_VELOCITY

        # Joint limit proximity
        for j, (lo, hi) in enumerate(JOINT_LIMITS):
            margin = (hi - lo) * 0.05
            if joint_angles[j] < lo + margin or joint_angles[j] > hi - margin:
                self._log_anomaly(Anomaly(
                    kind="joint_limit",
                    joint=j,
                    value=joint_angles[j],
                    message=f"Joint {j+1} near limit ({joint_angles[j]:.3f} rad)"
                ))

        # Torque spike detection
        if torques is not None:
            MAX_T = [2.0, 8.0, 6.0, 2.0, 2.0, 1.5]  # Nm per joint
            for j, (t, mt) in enumerate(zip(torques, MAX_T)):
                if abs(t) > mt * self.TORQUE_WARN:
                    self._log_anomaly(Anomaly(
                        kind="torque_spike",
                        joint=j,
                        value=float(t),
                        message=f"Joint {j+1} torque {t:.2f} Nm ({abs(t)/mt*100:.0f}% of max)"
                    ))

        # Oscillation detection (velocity sign changes)
        state = self.arm.state
        vel_sum = float(np.sum(np.abs(state.velocities)))
        self._oscillation_window.append(vel_sum)
        if len(self._oscillation_window) > 20:
            self._oscillation_window.pop(0)
            # Count direction reversals in recent history
            signs = [np.sign(v) for v in self._oscillation_window]
            reversals = sum(1 for i in range(1, len(signs)) if signs[i] != signs[i-1])
            if reversals > 10:
                self._log_anomaly(Anomaly(
                    kind="oscillation",
                    joint=None,
                    value=float(reversals),
                    message="Possible oscillation / instability detected"
                ))

        # Singularity proximity (J2 and J3 near zero — wrist singularity)
        if abs(joint_angles[1]) < 0.05 and abs(joint_angles[2]) < 0.05:
            self._log_anomaly(Anomaly(
                kind="singularity",
                joint=None,
                value=0.0,
                message="Near shoulder singularity"
            ))

    def _log_anomaly(self, a: Anomaly):
        # Deduplicate — don't spam same anomaly within 2 seconds
        now = time.time()
        for prev in reversed(self.anomalies[-10:]):
            if prev.kind == a.kind and prev.joint == a.joint and now - prev.timestamp < 2.0:
                return
        self.anomalies.append(a)
        if len(self.anomalies) > 200:
            self.anomalies = self.anomalies[-200:]
        log.warning(f"[AI] {a.kind.upper()} — {a.message}")

    # ── Motion memory / learning ───────────────────────────────────────────

    def record_completed_motion(self, planned_duration: float, actual_duration: float,
                                 anomaly_count: int):
        """After a trajectory completes, learn from it."""
        self._motion_memory.append({
            "planned": planned_duration,
            "actual": actual_duration,
            "anomalies": anomaly_count,
        })
        if len(self._motion_memory) > 50:
            self._motion_memory.pop(0)
        self._update_velocity_scale()

    def _update_velocity_scale(self):
        if len(self._motion_memory) < 3:
            return
        recent = self._motion_memory[-10:]
        avg_anomalies = np.mean([m["anomalies"] for m in recent])
        ratio = np.mean([m["actual"] / max(m["planned"], 0.1) for m in recent])
        # If many anomalies → slow down; if running clean → allow faster
        if avg_anomalies > 3:
            self._velocity_scale = max(0.4, self._velocity_scale * 0.9)
        elif avg_anomalies < 0.5 and ratio < 1.1:
            self._velocity_scale = min(1.5, self._velocity_scale * 1.05)
        log.info(f"[AI] Velocity scale updated: {self._velocity_scale:.3f}")

    @property
    def velocity_scale(self) -> float:
        return self._velocity_scale

    def recent_anomalies(self, n: int = 10) -> list[Anomaly]:
        return self.anomalies[-n:]

    def anomaly_summary(self) -> dict:
        counts: dict[str, int] = {}
        for a in self.anomalies:
            counts[a.kind] = counts.get(a.kind, 0) + 1
        return counts
