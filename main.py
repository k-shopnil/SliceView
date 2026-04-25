# =========================================================
# SliceView Beta v1.2.1 - One-Dir Production Edition
# =========================================================
import sys
import os
import subprocess
import threading
import math
import numpy as np
import ctypes

# --- Windows Taskbar Icon Fix ---
try:
    myappid = 'shopnil.sliceview.v1.2.1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

import glfw
from OpenGL.GL import *
import imgui
from imgui.integrations.glfw import GlfwRenderer
import tkinter as tk
from tkinter import filedialog
from PIL import Image
import trimesh

from core.obj_parser import load_obj
from core.math_engine import identity, translate, rotate_x, rotate_y, rotate_z, perspective, look_at, \
    scale as create_scale_matrix
from core.renderer import Renderer

# --- Global State & Reset Logic ---
DEFAULT_STATE = {
    "scale": 1.0,
    "pan": [0.0, 0.0, 0.0],
    "rotation_deg": [0.0, 0.0, 0.0],
    "reflect": [False, False, False],
    "cam_radius": 10.0,
    "cam_orbit_deg": [0.0, 15.0],
    "plane_h": 0.0,
    "plane_angles_deg": [90.0, 0.0],
    "slicing_active": True,
    "auto_scan": False,
    "color": [0.8, 0.2, 0.3],
    "light_angles_deg": [45.0, 45.0],
}

state = {
    "current_model_name": "None",
    "is_generating": False,
    "pending_obj_path": None,
    "ai_status_msg": "",
    **DEFAULT_STATE
}


def reset_to_default():
    for key, value in DEFAULT_STATE.items():
        state[key] = value if not isinstance(value, list) else list(value)


# --- Helper for Paths in One-Dir mode ---
def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(".")


# --- Dialog Functions ---
def open_file_dialog():
    root = tk.Tk();
    root.withdraw();
    root.call('wm', 'attributes', '.', '-topmost', True)
    path = filedialog.askopenfilename(filetypes=[("OBJ Files", "*.obj"), ("All Files", "*.*")])
    root.destroy();
    return path if path else None


def open_image_dialog():
    root = tk.Tk();
    root.withdraw();
    root.call('wm', 'attributes', '.', '-topmost', True)
    path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg"), ("All Files", "*.*")])
    root.destroy();
    return path if path else None


def draw_knob(label, value, v_min, v_max, radius=25.0):
    imgui.begin_group()
    pos = imgui.get_cursor_screen_pos()
    draw_list = imgui.get_window_draw_list()
    center = (pos[0] + radius, pos[1] + radius)
    imgui.invisible_button(label, radius * 2.0, radius * 2.0)
    value_changed = False
    if imgui.is_item_active() and imgui.is_mouse_dragging(imgui.MOUSE_BUTTON_LEFT):
        delta_y = imgui.get_io().mouse_delta[1]
        value -= delta_y * ((v_max - v_min) / 200.0)
        value = max(v_min, min(v_max, value))
        value_changed = True
    bg_color = imgui.get_color_u32_rgba(0.15, 0.15, 0.18, 1.0)
    draw_list.add_circle_filled(center[0], center[1], radius, bg_color)
    t = (value - v_min) / (v_max - v_min)
    angle = math.radians(135.0 + (t * 270.0))
    end_x, end_y = center[0] + math.cos(angle) * (radius * 0.75), center[1] + math.sin(angle) * (radius * 0.75)
    line_color = imgui.get_color_u32_rgba(0.0, 1.0, 1.0, 1.0) if imgui.is_item_active() else imgui.get_color_u32_rgba(
        0.7, 0.7, 0.7, 1.0)
    draw_list.add_line(center[0], center[1], end_x, end_y, line_color, thickness=3.0)
    imgui.same_line(radius * 2.5)
    imgui.set_cursor_pos((imgui.get_cursor_pos()[0], imgui.get_cursor_pos()[1] + radius * 0.5))
    imgui.text(f"{label}: {value:.1f}")
    imgui.end_group()
    return value_changed, value


def run_ai_worker(image_path):
    state["is_generating"] = True
    state["ai_status_msg"] = "AI pipeline analyzing..."
    base = get_base_path()
    output_obj = os.path.join(base, "generated_mesh.obj")

    if getattr(sys, 'frozen', False):
        # Path to the standalone ai_engine.exe inside your dist folder
        ai_executable = os.path.join(base, "ai_engine", "ai_engine.exe")
        cmd = [ai_executable, image_path, output_obj]
    else:
        ai_executable = os.path.join("core", "ai_engine.py")
        cmd = [sys.executable, ai_executable, image_path, output_obj]

    try:
        CREATE_NO_WINDOW = 0x08000000
        # CWD=BASE ensures the AI engine finds the .env sitting next to main.exe
        subprocess.run(cmd, check=True, capture_output=True, text=True,
                       cwd=base, creationflags=CREATE_NO_WINDOW if os.name == 'nt' else 0)

        state["pending_obj_path"] = output_obj
        state["ai_status_msg"] = "Generation Success!"
    except Exception as e:
        print(f"AI Error: {e}")
        state["ai_status_msg"] = "Error! Check console."
    finally:
        state["is_generating"] = False


def angles_to_vector(pitch_deg, yaw_deg):
    p, y = math.radians(pitch_deg), math.radians(yaw_deg)
    return [math.cos(p) * math.sin(y), math.sin(p), math.cos(p) * math.cos(y)]


def main():
    if not glfw.init(): return
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3);
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE);
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
    window = glfw.create_window(1280, 720, "SliceView Beta v1.2.1", None, None)

    # --- Icon Loader ---
    try:
        icon_path = os.path.join(get_base_path(), "assets", "icon.png")
        icon_img = Image.open(icon_path)
        glfw.set_window_icon(window, 1, [icon_img])
    except:
        pass

    glfw.make_context_current(window);
    glEnable(GL_DEPTH_TEST);
    glDisable(GL_CULL_FACE)
    imgui.create_context();
    impl = GlfwRenderer(window);
    renderer = Renderer()

    # --- Startup Model ---
    default_model = os.path.join(get_base_path(), "assets", "models", "HumanHeart_OBJ.obj")
    if os.path.exists(default_model):
        renderer.set_data(load_obj(default_model));
        state["current_model_name"] = os.path.basename(default_model)

    while not glfw.window_should_close(window):
        glfw.poll_events();
        impl.process_inputs()

        if state["pending_obj_path"]:
            try:
                renderer.set_data(load_obj(state["pending_obj_path"]))
                state["current_model_name"] = "AI_Generated.obj"
            except:
                pass
            state["pending_obj_path"] = None

        glClearColor(0.08, 0.08, 0.1, 1.0);
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        imgui.new_frame()
        imgui.set_next_window_size(450, 750, imgui.FIRST_USE_EVER)
        imgui.begin("INSPECTION DASHBOARD", flags=imgui.WINDOW_NO_COLLAPSE)

        if imgui.button("🔄 Reset Entire 3D Workspace", width=-1):
            reset_to_default()
        imgui.separator()

        imgui.text_colored("DATA MANAGEMENT:", 0.0, 1.0, 1.0)
        if imgui.button("📂 Load .OBJ"):
            path = open_file_dialog()
            if path: renderer.set_data(load_obj(path)); state["current_model_name"] = os.path.basename(path)
        imgui.same_line()
        if imgui.button("🪄 AI Generate") and not state["is_generating"]:
            img = open_image_dialog()
            if img: threading.Thread(target=run_ai_worker, args=(img,), daemon=True).start()

        imgui.text(f"Loaded: {state['current_model_name']}")
        if state["is_generating"]:
            chars = "|/-\\"
            c = chars[int(glfw.get_time() * 10) % 4]
            imgui.text_colored(f"[{c}] {state['ai_status_msg']}", 1.0, 0.8, 0.0, 1.0)
        elif state["ai_status_msg"]:
            imgui.text_colored(state["ai_status_msg"], 0.4, 1.0, 0.4, 1.0)

        if imgui.collapsing_header("1. VISUALS & LIGHTING", flags=imgui.TREE_NODE_DEFAULT_OPEN)[0]:
            _, state["color"] = imgui.color_edit3("Mesh Color", *state["color"])
            _, state["light_angles_deg"][0] = draw_knob("Light Pitch", state["light_angles_deg"][0], -90, 90)
            _, state["light_angles_deg"][1] = draw_knob("Light Yaw", state["light_angles_deg"][1], -180, 180)

        if imgui.collapsing_header("2. 3D TRANSFORMATIONS", flags=imgui.TREE_NODE_DEFAULT_OPEN)[0]:
            _, state["scale"] = imgui.drag_float("Scale", state["scale"], 0.05, 0.01, 100.0)
            _, state["pan"] = imgui.drag_float3("Pan", *state["pan"], 0.05)
            _, state["rotation_deg"] = imgui.drag_float3("Rotation", *state["rotation_deg"], 1.0)
            imgui.text("Mirroring:")
            _, state["reflect"][0] = imgui.checkbox("X", state["reflect"][0]);
            imgui.same_line()
            _, state["reflect"][1] = imgui.checkbox("Y", state["reflect"][1]);
            imgui.same_line()
            _, state["reflect"][2] = imgui.checkbox("Z", state["reflect"][2])
            imgui.separator()
            _, state["cam_radius"] = imgui.slider_float("Dist", state["cam_radius"], 1.0, 150.0)
            _, state["cam_orbit_deg"][0] = draw_knob("Azimuth", state["cam_orbit_deg"][0], -180, 180)
            _, state["cam_orbit_deg"][1] = draw_knob("Elevation", state["cam_orbit_deg"][1], -89, 89)

        if imgui.collapsing_header("3. SECTIONAL ANALYSIS", flags=imgui.TREE_NODE_DEFAULT_OPEN)[0]:
            _, state["slicing_active"] = imgui.checkbox("Slicing Engine Enabled", state["slicing_active"])

            if imgui.button("Top"): state["plane_angles_deg"] = [90.0, 0.0]; imgui.same_line()
            if imgui.button("Side"): state["plane_angles_deg"] = [0.0, 90.0]; imgui.same_line()
            if imgui.button("Front"): state["plane_angles_deg"] = [0.0, 0.0]

            _, state["plane_angles_deg"][0] = imgui.slider_float("Pitch", state["plane_angles_deg"][0], -180, 180)
            _, state["plane_angles_deg"][1] = imgui.slider_float("Yaw", state["plane_angles_deg"][1], -180, 180)
            _, state["plane_h"] = imgui.slider_float("Offset", state["plane_h"], -5.0, 5.0)
            _, state["auto_scan"] = imgui.checkbox("Auto Scan", state["auto_scan"])

        imgui.end()

        # Rendering View
        if state["auto_scan"]: state["plane_h"] = np.sin(glfw.get_time()) * 2.0
        m_reflect = identity()
        for i in range(3):
            if state["reflect"][i]: m_reflect[i, i] = -1.0
        m_rot = rotate_z(np.radians(state["rotation_deg"][2])) @ rotate_y(
            np.radians(state["rotation_deg"][1])) @ rotate_x(np.radians(state["rotation_deg"][0]))
        model = translate(*state["pan"]) @ m_rot @ m_reflect @ create_scale_matrix(state["scale"])
        az, el = np.radians(state["cam_orbit_deg"][0]), np.radians(state["cam_orbit_deg"][1])
        cam = [state["cam_radius"] * np.cos(el) * np.sin(az), state["cam_radius"] * np.sin(el),
               state["cam_radius"] * np.cos(el) * np.cos(az)]
        view = look_at(cam, [0, 0, 0], [0, 1, 0])
        proj = perspective(np.radians(45), 1280 / 720, 0.1, 1000.0)

        # Off-slicing logic
        clip_h = state["plane_h"] if state["slicing_active"] else 999.0

        if renderer.vertex_count > 0:
            renderer.draw(model, view, proj,
                          angles_to_vector(state["plane_angles_deg"][0], state["plane_angles_deg"][1]), clip_h,
                          state["color"], angles_to_vector(state["light_angles_deg"][0], state["light_angles_deg"][1]))

        imgui.render();
        impl.render(imgui.get_draw_data());
        glfw.swap_buffers(window)

    impl.shutdown();
    glfw.terminate()


if __name__ == "__main__":
    main()