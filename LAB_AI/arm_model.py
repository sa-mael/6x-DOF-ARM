"""
6-DOF Arm Model — forward/inverse kinematics, DH parameters, joint state management.
Designed for serial servo arm (max reach ~1.0m).
"""

import numpy as np
from dataclasses import dataclass, field
from typing import Optional
import time


# ─── DH Parameters (tweak to match your physical arm) ────────────────────────
# Each row: [a, alpha, d, theta_offset]  (metres / radians)
DH_PARAMS = [
    [0.000,  np.pi/2, 0.147, 0.0],   # Joint 1 — base rotation
    [0.340,  0.000,   0.000, 0.0],   # Joint 2 — shoulder
    [0.300,  0.000,   0.000, 0.0],   # Joint 3 — elbow
    [0.000,  np.pi/2, 0.000, 0.0],   # Joint 4 — wrist roll
    [0.000, -np.pi/2, 0.130, 0.0],   # Joint 5 — wrist pitch
    [0.000,  0.000,   0.060, 0.0],   # Joint 6 — end effector
]

# Joint limits [min, max] in radians
JOINT_LIMITS = [
    [-np.pi,     np.pi   ],   # J1
    [-np.pi/2,   np.pi/2 ],   # J2
    [-np.pi*0.8, np.pi*0.8],  # J3
    [-np.pi,     np.pi   ],   # J4
    [-np.pi/2,   np.pi/2 ],   # J5
    [-np.pi,     np.pi   ],   # J6
]

# Max velocity (rad/s) per joint — for smooth motion capping
MAX_VELOCITY = [2.0, 1.5, 2.0, 3.0, 3.0, 4.0]


@dataclass
class JointState:
    angles: np.ndarray = field(default_factory=lambda: np.zeros(6))
    velocities: np.ndarray = field(default_factory=lambda: np.zeros(6))
    torques: np.ndarray = field(default_factory=lambda: np.zeros(6))
    timestamp: float = field(default_factory=time.time)

    def copy(self) -> "JointState":
        return JointState(
            angles=self.angles.copy(),
            velocities=self.velocities.copy(),
            torques=self.torques.copy(),
            timestamp=self.timestamp,
        )


@dataclass
class CartesianPose:
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    rx: float = 0.0   # roll
    ry: float = 0.0   # pitch
    rz: float = 0.0   # yaw

    def as_array(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z, self.rx, self.ry, self.rz])


def dh_matrix(a: float, alpha: float, d: float, theta: float) -> np.ndarray:
    """Standard DH transformation matrix."""
    ct, st = np.cos(theta), np.sin(theta)
    ca, sa = np.cos(alpha), np.sin(alpha)
    return np.array([
        [ct, -st*ca,  st*sa, a*ct],
        [st,  ct*ca, -ct*sa, a*st],
        [0,      sa,     ca,    d],
        [0,       0,      0,    1],
    ])


def forward_kinematics(joint_angles: np.ndarray) -> tuple[np.ndarray, list[np.ndarray]]:
    """
    Compute end-effector pose and all joint frames.
    Returns (4x4 T_ee, list of 4x4 T_i for each joint).
    """
    T = np.eye(4)
    frames = [T.copy()]
    for i, (a, alpha, d, theta_off) in enumerate(DH_PARAMS):
        theta = joint_angles[i] + theta_off
        T = T @ dh_matrix(a, alpha, d, theta)
        frames.append(T.copy())
    return T, frames


def jacobian(joint_angles: np.ndarray, eps: float = 1e-5) -> np.ndarray:
    """Numerical Jacobian (6×6) via central differences."""
    J = np.zeros((6, 6))
    T0, _ = forward_kinematics(joint_angles)
    p0 = T0[:3, 3]
    # Euler ZYX from rotation matrix
    r0 = _rot_to_euler(T0[:3, :3])
    x0 = np.concatenate([p0, r0])
    for i in range(6):
        dq = joint_angles.copy()
        dq[i] += eps
        T_plus, _ = forward_kinematics(dq)
        p_plus = T_plus[:3, 3]
        r_plus = _rot_to_euler(T_plus[:3, :3])
        x_plus = np.concatenate([p_plus, r_plus])
        J[:, i] = (x_plus - x0) / eps
    return J


def _rot_to_euler(R: np.ndarray) -> np.ndarray:
    """Rotation matrix → ZYX Euler angles."""
    sy = np.sqrt(R[0, 0]**2 + R[1, 0]**2)
    singular = sy < 1e-6
    if not singular:
        x = np.arctan2(R[2, 1], R[2, 2])
        y = np.arctan2(-R[2, 0], sy)
        z = np.arctan2(R[1, 0], R[0, 0])
    else:
        x = np.arctan2(-R[1, 2], R[1, 1])
        y = np.arctan2(-R[2, 0], sy)
        z = 0.0
    return np.array([x, y, z])


def inverse_kinematics(
    target_pose: np.ndarray,       # [x, y, z, rx, ry, rz]
    q_init: Optional[np.ndarray] = None,
    max_iter: int = 100,
    tol: float = 1e-4,
    damping: float = 0.05,
) -> tuple[np.ndarray, bool, float]:
    """
    Damped Least Squares IK (Levenberg-Marquardt style).
    Returns (joint_angles, converged, residual_error).
    """
    q = q_init.copy() if q_init is not None else np.zeros(6)
    for iteration in range(max_iter):
        T, _ = forward_kinematics(q)
        pos_err = target_pose[:3] - T[:3, 3]
        euler_curr = _rot_to_euler(T[:3, :3])
        ori_err = target_pose[3:] - euler_curr
        # Wrap orientation error to [-π, π]
        ori_err = (ori_err + np.pi) % (2 * np.pi) - np.pi
        err = np.concatenate([pos_err, ori_err * 0.3])   # weight orientation less
        residual = np.linalg.norm(err)
        if residual < tol:
            return _clamp_joints(q), True, residual
        J = jacobian(q)
        # Damped least squares
        JJT = J @ J.T
        dq = J.T @ np.linalg.solve(JJT + damping**2 * np.eye(6), err)
        # Step size with line search
        step = min(0.3, 0.5 / (np.linalg.norm(dq) + 1e-9))
        q = q + step * dq
        q = _clamp_joints(q)
    T, _ = forward_kinematics(q)
    residual = np.linalg.norm(target_pose[:3] - T[:3, 3])
    return q, residual < 2e-3, residual


def _clamp_joints(q: np.ndarray) -> np.ndarray:
    result = q.copy()
    for i, (lo, hi) in enumerate(JOINT_LIMITS):
        result[i] = np.clip(result[i], lo, hi)
    return result


class ArmModel:
    """High-level arm model — wraps FK/IK, tracks joint state history."""

    def __init__(self):
        self.state = JointState()
        self.history: list[JointState] = []
        self._max_history = 500

    def update_joints(self, angles: np.ndarray):
        prev = self.state.copy()
        dt = time.time() - prev.timestamp
        self.state.angles = _clamp_joints(np.array(angles, dtype=float))
        if dt > 0:
            self.state.velocities = (self.state.angles - prev.angles) / dt
        self.state.timestamp = time.time()
        self.history.append(prev)
        if len(self.history) > self._max_history:
            self.history.pop(0)

    def get_ee_pose(self) -> CartesianPose:
        T, _ = forward_kinematics(self.state.angles)
        r = _rot_to_euler(T[:3, :3])
        return CartesianPose(
            x=T[0, 3], y=T[1, 3], z=T[2, 3],
            rx=r[0], ry=r[1], rz=r[2],
        )

    def get_all_frames(self) -> list[np.ndarray]:
        _, frames = forward_kinematics(self.state.angles)
        return frames

    def solve_ik(self, target: CartesianPose) -> tuple[np.ndarray, bool]:
        q, ok, err = inverse_kinematics(
            target.as_array(), q_init=self.state.angles
        )
        return q, ok

    def is_near_joint_limit(self, margin: float = 0.15) -> list[bool]:
        result = []
        for i, (lo, hi) in enumerate(JOINT_LIMITS):
            a = self.state.angles[i]
            result.append(a < lo + margin or a > hi - margin)
        return result
