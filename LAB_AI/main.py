"""
6-DOF ARM Controller — Main Application
────────────────────────────────────────
Built with Dear PyGui. Runs entirely local, no browser needed.

Layout:
  ┌──────────────┬────────────────────┬────────────────┐
  │  CONNECTION  │   3D DIGITAL TWIN  │  AI DIAGNOSTIC │
  │  JOINT SLDR  │   (OpenGL canvas)  │  ANOMALY LOG   │
  │  GLOVE       ├────────────────────┤                │
  │  STATUS      │  TRAJECTORY PLAN   │                │
  └──────────────┴────────────────────┴────────────────┘
"""

import dearpygui.dearpygui as dpg
import numpy as np
import threading
import time
import sys
import os
import logging

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.arm_model     import ArmModel, CartesianPose, forward_kinematics
from core.transport     import SerialTransport, MockTransport
from ai.motion_engine   import AIMotionEngine, MotionMode
from glove.glove_controller import MockGloveController, GestureType

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
log = logging.getLogger("app")

# ─── Colour palette ───────────────────────────────────────────────────────────
C_BG        = (18, 18, 22, 255)
C_PANEL     = (28, 28, 35, 255)
C_ACCENT    = (120, 86, 230, 255)       # purple
C_ACCENT2   = (46, 196, 154, 255)       # teal
C_WARN      = (239, 159, 39, 255)       # amber
C_DANGER    = (226, 75, 74, 255)        # red
C_TEXT      = (220, 218, 210, 255)
C_MUTED     = (130, 128, 120, 255)
C_GREEN     = (100, 200, 120, 255)
C_GRID      = (40, 40, 52, 255)

JOINT_NAMES = ["Base", "Shoulder", "Elbow", "Wrist Roll", "Wrist Pitch", "EE"]


class ArmApp:

    def __init__(self, mock: bool = True):
        self.arm   = ArmModel()
        self.ai    = AIMotionEngine(self.arm)

        if mock:
            self.transport = MockTransport(on_feedback=self._on_feedback)
            self.glove     = MockGloveController(
                on_pose=self._on_glove_pose,
                on_gesture=self._on_gesture,
            )
        else:
            self.transport = SerialTransport(on_feedback=self._on_feedback)
            from glove.glove_controller import GloveController
            self.glove = GloveController(
                on_pose=self._on_glove_pose,
                on_gesture=self._on_gesture,
            )

        self._executing = False
        self._traj_thread: threading.Thread | None = None
        self._waypoint_a: np.ndarray | None = None
        self._waypoint_b: np.ndarray | None = None
        self._mode = MotionMode.SPLINE
        self._mirror_mode = False
        self._glove_euler = np.zeros(3)
        self._feedback_angles = np.zeros(6)
        self._feedback_torques = np.zeros(6)
        self._anomaly_buf: list[str] = []
        self._last_update = time.time()

    # ── Feedback handlers ─────────────────────────────────────────────────

    def _on_feedback(self, data: dict):
        if "joints" in data:
            angles_deg = np.array(data["joints"], dtype=float)
            self._feedback_angles = np.radians(angles_deg)
            self.arm.update_joints(self._feedback_angles)
        if "torques" in data:
            self._feedback_torques = np.array(data["torques"], dtype=float)
        self.ai.check_state(self._feedback_angles, self._feedback_torques)

    def _on_glove_pose(self, pose):
        self._glove_euler = pose.euler.copy()
        if self._mirror_mode:
            # Map wrist roll/pitch/yaw → arm joints 3,4,5
            target = self.arm.state.angles.copy()
            target[3] = np.clip(pose.euler[0] * 1.2, -np.pi, np.pi)
            target[4] = np.clip(pose.euler[1] * 1.2, -np.pi/2, np.pi/2)
            target[5] = np.clip(pose.euler[2] * 0.8, -np.pi, np.pi)
            self.transport.send_joints(target, speed=0.7)

    def _on_gesture(self, evt):
        if evt.gesture == GestureType.PINCH:
            self._set_waypoint()
        elif evt.gesture == GestureType.FIST:
            self._execute_trajectory()
        elif evt.gesture == GestureType.POINT:
            self._emergency_stop()

    # ── GUI build ─────────────────────────────────────────────────────────

    def build(self):
        dpg.create_context()
        self._apply_theme()

        with dpg.window(tag="main", label="6-DOF ARM Controller",
                        no_title_bar=True, no_move=True, no_resize=True):

            with dpg.table(header_row=False, borders_innerV=True,
                           tag="root_table"):
                dpg.add_table_column(init_width_or_weight=260)
                dpg.add_table_column(init_width_or_weight=480)
                dpg.add_table_column(init_width_or_weight=260)

                with dpg.table_row():
                    # ── LEFT PANEL ──────────────────────────────────────
                    with dpg.table_cell():
                        self._build_left_panel()

                    # ── CENTRE PANEL ────────────────────────────────────
                    with dpg.table_cell():
                        self._build_centre_panel()

                    # ── RIGHT PANEL ─────────────────────────────────────
                    with dpg.table_cell():
                        self._build_right_panel()

        dpg.create_viewport(
            title="6-DOF ARM Controller",
            width=1020, height=760,
            min_width=800, min_height=600,
        )
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main", True)

    def _build_left_panel(self):
        dpg.add_text("CONNECTION", color=C_MUTED)
        dpg.add_separator()

        dpg.add_text("Port:", color=C_MUTED)
        ports = self.transport.list_ports() if hasattr(self.transport, "list_ports") else ["MOCK"]
        dpg.add_combo(ports, default_value=ports[0] if ports else "",
                      tag="port_combo", width=-1)
        with dpg.group(horizontal=True):
            dpg.add_button(label="Connect", tag="btn_connect",
                           callback=self._cb_connect, width=90)
            dpg.add_button(label="Disconnect", callback=self._cb_disconnect, width=90)
        dpg.add_text("● MOCK", tag="conn_status", color=C_ACCENT2)

        dpg.add_spacer(height=8)
        dpg.add_text("JOINT CONTROL", color=C_MUTED)
        dpg.add_separator()

        # Joint sliders
        for i, name in enumerate(JOINT_NAMES):
            lo, hi = -180, 180
            dpg.add_slider_float(
                label=name,
                tag=f"j{i}",
                min_value=lo, max_value=hi,
                default_value=0.0,
                width=-1,
                callback=self._cb_joint_slider,
                user_data=i,
            )

        dpg.add_spacer(height=4)
        with dpg.group(horizontal=True):
            dpg.add_button(label="Home", callback=self._cb_home, width=80)
            dpg.add_button(label="STOP", callback=self._emergency_stop,
                           width=80, tag="btn_stop")

        dpg.add_spacer(height=8)
        dpg.add_text("GLOVE INPUT", color=C_MUTED)
        dpg.add_separator()
        dpg.add_text("Status: disconnected", tag="glove_status", color=C_MUTED)
        dpg.add_text("R: 0.00  P: 0.00  Y: 0.00", tag="glove_euler", color=C_TEXT)
        dpg.add_checkbox(label="Mirror mode", tag="mirror_chk",
                         callback=lambda s, v: setattr(self, "_mirror_mode", v))

        dpg.add_spacer(height=8)
        dpg.add_text("WAYPOINTS", color=C_MUTED)
        dpg.add_separator()
        with dpg.group(horizontal=True):
            dpg.add_button(label="Set A", callback=self._set_waypoint_a, width=80)
            dpg.add_button(label="Set B", callback=self._set_waypoint_b, width=80)
        dpg.add_text("A: —", tag="wp_a_text", color=C_TEXT)
        dpg.add_text("B: —", tag="wp_b_text", color=C_TEXT)

    def _build_centre_panel(self):
        dpg.add_text("3D DIGITAL TWIN", color=C_MUTED)
        dpg.add_separator()

        # 3D arm drawing via DrawList
        with dpg.drawlist(width=460, height=380, tag="draw3d"):
            pass  # filled each frame

        dpg.add_spacer(height=6)
        dpg.add_text("TRAJECTORY PLANNER", color=C_MUTED)
        dpg.add_separator()

        with dpg.group(horizontal=True):
            dpg.add_text("Mode:", color=C_MUTED)
            dpg.add_combo(
                ["spline", "linear", "wave", "arc"],
                default_value="spline", tag="mode_combo",
                width=110,
                callback=lambda s, v: setattr(self, "_mode", v),
            )
            dpg.add_text("Duration:", color=C_MUTED)
            dpg.add_input_float(tag="duration_input", default_value=2.0,
                                width=70, min_value=0.3, max_value=30.0)

        with dpg.group(horizontal=True):
            dpg.add_text("Wave amp:", color=C_MUTED)
            dpg.add_slider_float(tag="wave_amp", min_value=0, max_value=0.5,
                                 default_value=0.1, width=120)
            dpg.add_text("Freq:", color=C_MUTED)
            dpg.add_slider_float(tag="wave_freq", min_value=0.1, max_value=5.0,
                                 default_value=1.0, width=100)

        with dpg.group(horizontal=True):
            dpg.add_button(label="▶ Execute A→B", callback=self._execute_trajectory,
                           width=130, tag="btn_execute")
            dpg.add_button(label="◼ Stop", callback=self._emergency_stop, width=70)
            dpg.add_text("", tag="exec_status", color=C_ACCENT2)

        dpg.add_spacer(height=4)
        # EE position readout
        with dpg.group(horizontal=True):
            dpg.add_text("EE: ", color=C_MUTED)
            dpg.add_text("x=0.000  y=0.000  z=0.000", tag="ee_pose", color=C_TEXT)

    def _build_right_panel(self):
        dpg.add_text("AI DIAGNOSTICS", color=C_MUTED)
        dpg.add_separator()

        dpg.add_text("Velocity scale:", color=C_MUTED)
        dpg.add_progress_bar(tag="vel_scale_bar", default_value=1.0, width=-1)
        dpg.add_text("1.00×", tag="vel_scale_txt", color=C_TEXT)

        dpg.add_spacer(height=4)
        dpg.add_text("Joint limits:", color=C_MUTED)
        for i in range(6):
            dpg.add_progress_bar(tag=f"jlim_{i}", default_value=0.0,
                                 width=-1, overlay=JOINT_NAMES[i])

        dpg.add_spacer(height=4)
        dpg.add_text("Torque load:", color=C_MUTED)
        for i in range(6):
            dpg.add_progress_bar(tag=f"torq_{i}", default_value=0.0,
                                 width=-1, overlay=JOINT_NAMES[i])

        dpg.add_spacer(height=4)
        dpg.add_text("ANOMALY LOG", color=C_MUTED)
        dpg.add_separator()
        dpg.add_child_window(tag="anomaly_window", height=200, border=False)
        with dpg.group(tag="anomaly_log", parent="anomaly_window"):
            dpg.add_text("No anomalies.", tag="no_anom", color=C_MUTED)

        dpg.add_spacer(height=4)
        dpg.add_text("SERIAL STATS", color=C_MUTED)
        dpg.add_separator()
        dpg.add_text("TX: 0  RX: 0  Err: 0", tag="serial_stats", color=C_TEXT)
        dpg.add_text("Latency: 0ms", tag="latency_txt", color=C_TEXT)

    # ── Theme ─────────────────────────────────────────────────────────────

    def _apply_theme(self):
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg,     C_BG)
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg,      C_PANEL)
                dpg.add_theme_color(dpg.mvThemeCol_PopupBg,      C_PANEL)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg,      C_PANEL)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered,(40, 40, 52, 255))
                dpg.add_theme_color(dpg.mvThemeCol_Button,        C_ACCENT)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (140,106,250,255))
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive,  (90, 66, 180,255))
                dpg.add_theme_color(dpg.mvThemeCol_Text,          C_TEXT)
                dpg.add_theme_color(dpg.mvThemeCol_Header,        C_ACCENT)
                dpg.add_theme_color(dpg.mvThemeCol_CheckMark,     C_ACCENT2)
                dpg.add_theme_color(dpg.mvThemeCol_SliderGrab,    C_ACCENT2)
                dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive,(60,220,180,255))
                dpg.add_theme_color(dpg.mvThemeCol_PlotHistogram,  C_ACCENT)
                dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 10)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding,  6)
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding,  12, 12)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing,    8, 6)
        dpg.bind_theme(global_theme)

        # Stop button red
        with dpg.theme() as stop_theme:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button,        C_DANGER)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (246,95,94,255))
        dpg.bind_item_theme("btn_stop", stop_theme)

    # ── Callbacks ─────────────────────────────────────────────────────────

    def _cb_connect(self):
        port = dpg.get_value("port_combo")
        ok = self.transport.connect(port if port != "MOCK (simulation)" else None)
        if ok:
            dpg.set_value("conn_status", "● CONNECTED")
            dpg.configure_item("conn_status", color=C_GREEN)
        else:
            dpg.set_value("conn_status", "✕ FAILED")
            dpg.configure_item("conn_status", color=C_DANGER)

    def _cb_disconnect(self):
        self.transport.disconnect()
        dpg.set_value("conn_status", "● DISCONNECTED")
        dpg.configure_item("conn_status", color=C_MUTED)

    def _cb_joint_slider(self, sender, value, user_data):
        i = user_data
        q = self.arm.state.angles.copy()
        q[i] = np.radians(value)
        self.transport.send_joints(q, speed=0.6)

    def _cb_home(self):
        self.transport.send_home()
        for i in range(6):
            dpg.set_value(f"j{i}", 0.0)

    def _emergency_stop(self, *_):
        self._executing = False
        self.transport.send_stop()
        dpg.set_value("exec_status", "STOPPED")
        dpg.configure_item("exec_status", color=C_DANGER)

    def _set_waypoint(self):
        self._set_waypoint_a() if self._waypoint_a is None else self._set_waypoint_b()

    def _set_waypoint_a(self, *_):
        self._waypoint_a = self.arm.state.angles.copy()
        ee = self.arm.get_ee_pose()
        dpg.set_value("wp_a_text", f"A: {ee.x:.3f}, {ee.y:.3f}, {ee.z:.3f}")

    def _set_waypoint_b(self, *_):
        self._waypoint_b = self.arm.state.angles.copy()
        ee = self.arm.get_ee_pose()
        dpg.set_value("wp_b_text", f"B: {ee.x:.3f}, {ee.y:.3f}, {ee.z:.3f}")

    def _execute_trajectory(self, *_):
        if self._waypoint_a is None or self._waypoint_b is None:
            dpg.set_value("exec_status", "Set A and B first!")
            return
        if self._executing:
            return

        mode = dpg.get_value("mode_combo")
        duration = dpg.get_value("duration_input")
        wave_amp = dpg.get_value("wave_amp")
        wave_freq = dpg.get_value("wave_freq")

        traj = self.ai.build_trajectory(
            q_start=self._waypoint_a,
            q_end=self._waypoint_b,
            duration=duration,
            mode=mode,
            wave_amp=wave_amp,
            wave_freq=wave_freq,
        )

        def run():
            self._executing = True
            dpg.set_value("exec_status", "● EXECUTING")
            dpg.configure_item("exec_status", color=C_ACCENT2)
            t_start = time.time()
            anom_before = len(self.ai.anomalies)
            dt = traj.total_duration / len(traj.samples)
            for sample in traj.samples:
                if not self._executing:
                    break
                self.transport.send_joints(list(sample), speed=0.8)
                # Sync sliders
                for i in range(6):
                    dpg.set_value(f"j{i}", round(np.degrees(sample[i]), 1))
                time.sleep(dt)
            t_end = time.time()
            self.ai.record_completed_motion(
                planned_duration=traj.total_duration,
                actual_duration=t_end - t_start,
                anomaly_count=len(self.ai.anomalies) - anom_before,
            )
            self._executing = False
            dpg.set_value("exec_status", "✓ Done")
            dpg.configure_item("exec_status", color=C_GREEN)

        self._traj_thread = threading.Thread(target=run, daemon=True)
        self._traj_thread.start()

    # ── 3D rendering ──────────────────────────────────────────────────────

    def _draw_arm(self):
        dpg.delete_item("draw3d", children_only=True)
        W, H = 460, 380
        cx, cy = W // 2, H // 2 + 40  # canvas centre

        # Projection: simple orthographic, view from side
        SCALE = 320   # pixels per metre

        def proj(x, y, z):
            # isometric-ish: X→right, Z→up, Y→depth (squished)
            px = cx + (x - y * 0.3) * SCALE
            py = cy - (z + y * 0.15) * SCALE
            return (px, py)

        # Grid
        for gx in range(-3, 4):
            x = gx * 0.1
            p0 = proj(x, -0.3, 0)
            p1 = proj(x,  0.3, 0)
            dpg.draw_line(p0, p1, color=C_GRID, thickness=1, parent="draw3d")
        for gy in range(-3, 4):
            y = gy * 0.1
            p0 = proj(-0.3, y, 0)
            p1 = proj( 0.3, y, 0)
            dpg.draw_line(p0, p1, color=C_GRID, thickness=1, parent="draw3d")

        # Draw arm segments
        frames = self.arm.get_all_frames()
        positions = [f[:3, 3] for f in frames]
        limit_flags = self.arm.is_near_joint_limit()

        prev = proj(*positions[0])
        for i in range(1, len(positions)):
            curr = proj(*positions[i])
            # Colour by limit proximity
            colour = C_DANGER if (i - 1 < len(limit_flags) and limit_flags[i-1]) else C_ACCENT2
            # Bone
            dpg.draw_line(prev, curr, color=colour, thickness=4, parent="draw3d")
            # Joint circle
            dpg.draw_circle(prev, 7, color=C_ACCENT, fill=C_ACCENT, parent="draw3d")
            prev = curr

        # EE marker
        dpg.draw_circle(prev, 10, color=C_ACCENT, fill=(0,0,0,0),
                        thickness=2, parent="draw3d")
        dpg.draw_circle(prev, 4, color=(255,255,255,200), fill=(255,255,255,200),
                        parent="draw3d")

        # Waypoints
        if self._waypoint_a is not None:
            from core.arm_model import forward_kinematics as fk
            Ta, _ = fk(self._waypoint_a)
            pa = proj(*Ta[:3, 3])
            dpg.draw_circle(pa, 8, color=C_ACCENT2, fill=C_ACCENT2, parent="draw3d")
            dpg.draw_text((pa[0]+10, pa[1]-8), "A", color=C_ACCENT2,
                          size=14, parent="draw3d")

        if self._waypoint_b is not None:
            from core.arm_model import forward_kinematics as fk
            Tb, _ = fk(self._waypoint_b)
            pb = proj(*Tb[:3, 3])
            dpg.draw_circle(pb, 8, color=C_WARN, fill=C_WARN, parent="draw3d")
            dpg.draw_text((pb[0]+10, pb[1]-8), "B", color=C_WARN,
                          size=14, parent="draw3d")

    # ── Update loop ───────────────────────────────────────────────────────

    def _update_ui(self):
        now = time.time()
        if now - self._last_update < 0.05:   # 20 Hz UI update
            return
        self._last_update = now

        # 3D arm
        self._draw_arm()

        # EE pose
        ee = self.arm.get_ee_pose()
        dpg.set_value("ee_pose",
                      f"x={ee.x:.3f}  y={ee.y:.3f}  z={ee.z:.3f}  "
                      f"rx={np.degrees(ee.rx):.1f}°")

        # Glove
        if self.glove.connected:
            dpg.set_value("glove_status", "Status: ● connected")
            dpg.configure_item("glove_status", color=C_GREEN)
            e = self._glove_euler
            dpg.set_value("glove_euler",
                          f"R:{np.degrees(e[0]):+.1f}°  "
                          f"P:{np.degrees(e[1]):+.1f}°  "
                          f"Y:{np.degrees(e[2]):+.1f}°")

        # AI velocity scale
        vs = self.ai.velocity_scale
        dpg.set_value("vel_scale_bar", min(vs / 1.5, 1.0))
        dpg.set_value("vel_scale_txt", f"{vs:.2f}×")

        # Joint limit bars
        lim = self.arm.is_near_joint_limit()
        for i, (lo, hi) in enumerate([(-np.pi, np.pi)] * 6):
            a = float(self._feedback_angles[i]) if i < len(self._feedback_angles) else 0.0
            pct = (a - lo) / (hi - lo)
            dpg.set_value(f"jlim_{i}", float(np.clip(pct, 0, 1)))

        # Torque bars
        MAX_T = [2.0, 8.0, 6.0, 2.0, 2.0, 1.5]
        for i in range(6):
            t = float(self._feedback_torques[i]) if i < len(self._feedback_torques) else 0.0
            dpg.set_value(f"torq_{i}", float(np.clip(abs(t) / MAX_T[i], 0, 1)))

        # Anomaly log
        anomalies = self.ai.recent_anomalies(8)
        if anomalies:
            if dpg.does_item_exist("no_anom"):
                dpg.delete_item("no_anom")
            # Add new anomalies not yet shown
            for a in anomalies[-3:]:
                msg = f"[{a.kind}] {a.message}"
                if msg not in self._anomaly_buf:
                    self._anomaly_buf.append(msg)
                    colour = C_DANGER if a.kind in ("torque_spike","singularity") else C_WARN
                    dpg.add_text(msg, color=colour, parent="anomaly_log",
                                 wrap=240)
                    if len(self._anomaly_buf) > 30:
                        self._anomaly_buf.pop(0)

        # Serial stats
        s = self.transport.stats
        dpg.set_value("serial_stats",
                      f"TX: {s['sent']}  RX: {s['recv']}  Err: {s['errors']}")
        dpg.set_value("latency_txt", f"Latency: {s['latency_ms']:.0f}ms")

    # ── Run ───────────────────────────────────────────────────────────────

    def run(self):
        self.build()
        while dpg.is_dearpygui_running():
            self._update_ui()
            dpg.render_dearpygui_frame()
        dpg.destroy_context()


# ─── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="6-DOF ARM Controller")
    parser.add_argument("--real", action="store_true",
                        help="Connect to real hardware (default: mock/simulation)")
    args = parser.parse_args()

    app = ArmApp(mock=not args.real)
    app.run()
