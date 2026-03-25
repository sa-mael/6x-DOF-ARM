# 6-DOF ARM Controller

Python control application for the 6-DOF robotic arm.
Features a real-time digital twin, AI trajectory optimizer, and IMU glove input.

---

## Stack

| Module | Technology |
|---|---|
| GUI | Dear PyGui 1.11 |
| Math / IK | NumPy + SciPy |
| Transport | pyserial (JSON lines) |
| IMU filter | Madgwick AHRS (pure Python) |
| AI engine | Cubic spline + DLS optimizer |

---

## Project structure

```
arm_controller/
├── main.py                   # Entry point — run this
├── requirements.txt
├── core/
│   ├── arm_model.py          # DH kinematics, FK/IK, joint state
│   └── transport.py          # Serial TX/RX, MockTransport for dev
├── ai/
│   └── motion_engine.py      # Trajectory planner, safety guard, motion memory
└── glove/
    └── glove_controller.py   # IMU reader, Madgwick filter, gesture recognition
```

---

## Quick start

```bash
pip install -r requirements.txt

# Simulation mode (no hardware needed)
python main.py

# Real hardware
python main.py --real
```

---

## ESP32 Serial Protocol

**Baud rate:** 115200  
**Format:** JSON lines (one packet per `\n`)

### PC → ESP32 (commands)

```json
{"cmd": "move", "joints": [0.0, 45.0, -30.0, 0.0, 0.0, 0.0], "speed": 0.5}
{"cmd": "home"}
{"cmd": "stop"}
```

- `joints` — 6 angles in **degrees**
- `speed` — 0.0 (slow) … 1.0 (max velocity)

### ESP32 → PC (feedback, 20 Hz)

```json
{"joints": [0.0, 44.8, -29.9, 0.1, 0.0, 0.0], "torques": [0.1, 2.3, 1.8, 0.2, 0.1, 0.0], "ok": true}
```

---

## Glove MCU Protocol

Same baud (115200), second serial port. The glove MCU (ESP32-C3 + MPU6050) sends:

```json
{"ax": 0.1, "ay": 9.7, "az": 0.3, "gx": 0.01, "gy": 0.0, "gz": 0.0,
 "pinch": false, "fist": false, "point": false, "wave": false}
```

| Field | Unit | Description |
|---|---|---|
| ax/ay/az | m/s² | Linear acceleration |
| gx/gy/gz | rad/s | Angular velocity |
| pinch | bool | Set waypoint (leading edge) |
| fist | bool | Execute trajectory (leading edge) |
| point | bool | Emergency stop |
| wave | bool | Enable wave motion mode |

The Madgwick AHRS filter runs on the Python side (beta=0.08, 50 Hz).

---

## DH Parameters (hard.h equivalent)

| Joint | a (m) | α (rad) | d (m) | θ offset |
|---|---|---|---|---|
| 1 Base | 0.000 | π/2 | 0.147 | 0 |
| 2 Shoulder | 0.340 | 0 | 0.000 | 0 |
| 3 Elbow | 0.300 | 0 | 0.000 | 0 |
| 4 Wrist roll | 0.000 | π/2 | 0.000 | 0 |
| 5 Wrist pitch | 0.000 | −π/2 | 0.130 | 0 |
| 6 End effector | 0.000 | 0 | 0.060 | 0 |

Edit `core/arm_model.py → DH_PARAMS` to match your actual geometry.

---

## AI Motion Engine

The engine adapts over time:

1. **Safety guard** — monitors joint limits, torque spikes, singularity proximity, oscillation.
2. **Velocity scaling** — if recent trajectories had anomalies, it slows down automatically. If clean runs happen consistently, it gradually speeds back up.
3. **Motion modes:**
   - `spline` — smooth cubic spline, zero velocity at endpoints
   - `linear` — straight interpolation in joint space
   - `wave` — sinusoidal overlay on joints 2-4
   - `arc` — arc path via intermediate waypoints
   - `mirror` — live glove mirror mode (wrist→joints 4-6)

---

## Glove gestures

| Gesture | Action |
|---|---|
| Pinch (index + thumb) | Set waypoint A (first call) or B (second call) |
| Fist | Execute A→B trajectory |
| Point (index extended) | Emergency stop |
| Wave flag in JSON | Switch to wave motion mode |

---

## Roadmap

- [ ] Calibration wizard (auto-compute DH params from known positions)
- [ ] Trajectory recording + playback
- [ ] 3D path preview overlay (draw planned trajectory on digital twin)
- [ ] Collision zones (define keep-out volumes)
- [ ] WebSocket bridge for browser-based twin (WebGL)
- [ ] Reinforcement learning for smooth gait profiles
