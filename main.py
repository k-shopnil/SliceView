# ==========================================
# main.py (Cross-Platform Edition)
# ==========================================
import sys

import glfw
from OpenGL.GL import *
import numpy as np
import math
import imgui
from imgui.integrations.glfw import GlfwRenderer
import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog

from core.obj_parser import load_obj
from core.math_engine import identity, translate, rotate_x, rotate_y, rotate_z, perspective, look_at, \
    scale as create_scale_matrix
from core.renderer import Renderer

# --- Cross-Platform File Dialogs ---
def open_file_dialog():
    """Works on Windows, Mac, and Linux"""
    root = tk.Tk()
    root.withdraw() # Hide the main tkinter window
    # Force window to front
    root.call('wm', 'attributes', '.', '-topmost', True)
    file_path = filedialog.askopenfilename(
        title="Select a 3D Model",
        filetypes=[("OBJ Files", "*.obj"), ("All Files", "*.*")]
    )
    root.destroy()
    return file_path if file_path else None

def open_image_dialog():
    """Works on Windows, Mac, and Linux"""
    root = tk.Tk()
    root.withdraw()
    root.call('wm', 'attributes', '.', '-topmost', True)
    file_path = filedialog.askopenfilename(
        title="Select a 2D Image",
        filetypes=[("Images", "*.png *.jpg *.jpeg"), ("All Files", "*.*")]
    )
    root.destroy()
    return file_path if file_path else None

# ... [KEEP ALL YOUR OTHER FUNCTIONS EXACTLY AS THEY WERE: draw_knob, run_ai_worker, angles_to_vector, main] ...
# (Just replace the two dialog functions at the top of the file)

def draw_knob(label, value, v_min, v_max, radius=25.0):
    """Custom ImGui Knob Widget."""
    imgui.begin_group()
    pos = imgui.get_cursor_screen_pos()
    draw_list = imgui.get_window_draw_list()
    center = (pos[0] + radius, pos[1] + radius)

    imgui.invisible_button(label, radius * 2.0, radius * 2.0)
    value_changed = False

    if imgui.is_item_active() and imgui.is_mouse_dragging(imgui.MOUSE_BUTTON_LEFT):
        delta_y = imgui.get_io().mouse_delta[1]
        step = (v_max - v_min) / 200.0
        value -= delta_y * step
        if value > v_max: value = v_min
        if value < v_min: value = v_max
        value_changed = True

    bg_color = imgui.get_color_u32_rgba(0.15, 0.15, 0.18, 1.0)
    draw_list.add_circle_filled(center[0], center[1], radius, bg_color)

    border_color = imgui.get_color_u32_rgba(0.3, 0.3, 0.4, 1.0)
    draw_list.add_circle(center[0], center[1], radius, border_color, thickness=2.0)

    t = (value - v_min) / (v_max - v_min)
    angle = math.radians(135.0 + (t * 270.0))

    end_x = center[0] + math.cos(angle) * (radius * 0.75)
    end_y = center[1] + math.sin(angle) * (radius * 0.75)

    line_color = imgui.get_color_u32_rgba(0.0, 1.0, 1.0, 1.0) if imgui.is_item_active() else imgui.get_color_u32_rgba(
        0.7, 0.7, 0.7, 1.0)
    draw_list.add_line(center[0], center[1], end_x, end_y, line_color, thickness=3.0)

    imgui.same_line(radius * 2.5)
    cursor_y = imgui.get_cursor_pos()[1]
    imgui.set_cursor_pos((imgui.get_cursor_pos()[0], cursor_y + radius * 0.5))
    imgui.text(f"{label}: {value:.1f}°")
    imgui.end_group()
    return value_changed, value



# --- Academic & Intuitive Global State ---
state = {
    "current_model_name": "None",
    "scale": 1.0,
    "pan": [0.0, 0.0, 0.0],
    "rotation_deg": [0.0, 0.0, 0.0],
    "reflect": [False, False, False],
    "cam_radius": 5.0,
    "cam_orbit_deg": [0.0, 15.0],
    "plane_h": 0.0,
    "plane_angles_deg": [90.0, 0.0],
    "auto_scan": False,
    "color": [0.8, 0.2, 0.3],
    "light_angles_deg": [45.0, 45.0],

    # --- AI Integration States ---
    "is_generating": False,
    "pending_obj_path": None,
    "ai_status_msg": ""
}


def run_ai_worker(image_path):
    """The async thread that talks to your microservice without freezing the UI."""
    state["is_generating"] = True
    state["ai_status_msg"] = "AI pipeline analyzing..."

    # Save the output directly to the project root
    output_obj = os.path.join(os.getcwd(), "generated_mesh.obj")

    try:
        # Calls the ai_engine.py exactly as you configured it
        subprocess.run(
            [sys.executable, "core/ai_engine.py", image_path, output_obj],
            check=True,
            capture_output=True,
            text=True
        )
        # Tell the main thread that the file is ready to be loaded
        state["pending_obj_path"] = output_obj
        state["ai_status_msg"] = "Generation Success!"
    except subprocess.CalledProcessError as e:
        print(f"AI Pipeline Error:\n{e.stderr}\n{e.stdout}")
        state["ai_status_msg"] = "Error! Check console."

    state["is_generating"] = False


def angles_to_vector(pitch_deg, yaw_deg):
    pitch = math.radians(pitch_deg)
    yaw = math.radians(yaw_deg)
    x = math.cos(pitch) * math.sin(yaw)
    y = math.sin(pitch)
    z = math.cos(pitch) * math.cos(yaw)
    return [x, y, z]


def main():
    if not glfw.init(): return

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)

    window = glfw.create_window(1280, 720, "SliceView Beta v1.2.1", None, None)
    glfw.make_context_current(window)
    glEnable(GL_DEPTH_TEST)
    glDisable(GL_CULL_FACE)

    imgui.create_context()
    impl = GlfwRenderer(window)

    renderer = Renderer()

    default_model = "assets/models/HumanHeart_OBJ.obj"
    if os.path.exists(default_model):
        renderer.set_data(load_obj(default_model))
        state["current_model_name"] = os.path.basename(default_model)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()

        # --- AI THREAD CHECKER ---
        # If the background thread finished generating an object, load it here safely on the main thread
        if state["pending_obj_path"]:
            try:
                renderer.set_data(load_obj(state["pending_obj_path"]))
                state["current_model_name"] = "AI_Generated.obj"

                # Reset rotations/scale for the new model
                state["scale"] = 1.0
                state["rotation_deg"] = [0.0, 0.0, 0.0]
                state["pan"] = [0.0, 0.0, 0.0]
            except Exception as e:
                print(f"Failed to load generated mesh into viewer: {e}")
            state["pending_obj_path"] = None

        glClearColor(0.08, 0.08, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # --- IMGUI INTERFACE ---
        imgui.new_frame()
        imgui.set_next_window_size(450, 750, imgui.FIRST_USE_EVER)
        imgui.set_next_window_position(20, 20, imgui.FIRST_USE_EVER)

        imgui.begin("INSPECTION DASHBOARD", flags=imgui.WINDOW_NO_COLLAPSE)

        # --- FILE LOADER SECTION ---
        imgui.text_colored("DATA MANAGEMENT:", 0.0, 1.0, 1.0)

        # Standard 3D Load
        if imgui.button("📂 Load .OBJ"):
            new_file = open_file_dialog()
            if new_file:
                try:
                    renderer.set_data(load_obj(new_file))
                    state["current_model_name"] = os.path.basename(new_file)
                except Exception as e:
                    print(f"Failed to load file: {e}")

        imgui.same_line()

        # New AI Generator Button
        if imgui.button("🪄 AI Generate from 2D"):
            if not state["is_generating"]:
                img_path = open_image_dialog()
                if img_path:
                    # Start the background microservice
                    threading.Thread(target=run_ai_worker, args=(img_path,), daemon=True).start()

        imgui.text(f"Loaded: {state['current_model_name']}")

        # --- ASYNC SPINNER UI ---
        if state["is_generating"]:
            # Animated spinner driven by the GLFW clock
            spinner = "|/-\\"
            idx = int(glfw.get_time() * 10) % 4
            imgui.text_colored(f"[{spinner[idx]}] {state['ai_status_msg']}", 1.0, 0.8, 0.0, 1.0)
        elif state["ai_status_msg"]:
            # Show success/fail text for a moment after it finishes
            color = (0.4, 1.0, 0.4, 1.0) if "Success" in state["ai_status_msg"] else (1.0, 0.3, 0.3, 1.0)
            imgui.text_colored(state["ai_status_msg"], *color)

        imgui.separator()
        imgui.spacing()

        # --- VISUALS SECTION ---
        if imgui.collapsing_header("1. VISUALS & LIGHTING", flags=imgui.TREE_NODE_DEFAULT_OPEN)[0]:
            _, state["color"] = imgui.color_edit3("Mesh Color", *state["color"])
            imgui.text("Dynamic Lighting Angle:")
            _, state["light_angles_deg"][0] = draw_knob("Light Pitch", state["light_angles_deg"][0], -90.0, 90.0)
            _, state["light_angles_deg"][1] = draw_knob("Light Yaw", state["light_angles_deg"][1], -180.0, 180.0)

        # --- 3D TRANSFORMATIONS ---
        if imgui.collapsing_header("2. 3D TRANSFORMATIONS & CAMERA", flags=imgui.TREE_NODE_DEFAULT_OPEN)[0]:
            _, state["scale"] = imgui.drag_float("Uniform Scaling", state["scale"], 0.05, 0.01, 100.0)
            _, state["pan"] = imgui.drag_float3("Translation", *state["pan"], 0.05)
            _, state["rotation_deg"] = imgui.drag_float3("Rotation", *state["rotation_deg"], 1.0)

            imgui.text("Reflection (Mirroring):")
            _, state["reflect"][0] = imgui.checkbox("Mirror X", state["reflect"][0])
            imgui.same_line()
            _, state["reflect"][1] = imgui.checkbox("Mirror Y", state["reflect"][1])
            imgui.same_line()
            _, state["reflect"][2] = imgui.checkbox("Mirror Z", state["reflect"][2])

            imgui.spacing()
            _, state["cam_radius"] = imgui.slider_float("Projection Distance", state["cam_radius"], 1.0, 50.0)
            _, state["cam_orbit_deg"][0] = draw_knob("Orbit Azimuth", state["cam_orbit_deg"][0], -180.0, 180.0)
            _, state["cam_orbit_deg"][1] = draw_knob("Orbit Elevation", state["cam_orbit_deg"][1], -89.0, 89.0)

        # --- SECTIONAL ANALYSIS ---
        if imgui.collapsing_header("3. SECTIONAL ANALYSIS (CLIPPING)", flags=imgui.TREE_NODE_DEFAULT_OPEN)[0]:
            if imgui.button("Top-Down"): state["plane_angles_deg"] = [90.0, 0.0]
            imgui.same_line()
            if imgui.button("Side-to-Side"): state["plane_angles_deg"] = [0.0, 90.0]
            imgui.same_line()
            if imgui.button("Front-to-Back"): state["plane_angles_deg"] = [0.0, 0.0]

            _, state["plane_angles_deg"][0] = imgui.slider_float("Plane Pitch", state["plane_angles_deg"][0], -180.0,
                                                                 180.0)
            _, state["plane_angles_deg"][1] = imgui.slider_float("Plane Yaw", state["plane_angles_deg"][1], -180.0,
                                                                 180.0)

            imgui.separator()
            _, state["plane_h"] = imgui.slider_float("Clipping Offset", state["plane_h"], -5.0, 5.0)
            _, state["auto_scan"] = imgui.checkbox("Automated Scan", state["auto_scan"])

        imgui.end()

        # --- THE CORE MATH ---
        if state["auto_scan"]:
            state["plane_h"] = np.sin(glfw.get_time()) * 2.0

        rot_rad = [math.radians(d) for d in state["rotation_deg"]]
        m_scale = create_scale_matrix(state["scale"])

        m_reflect = identity()
        m_reflect[0, 0] = -1.0 if state["reflect"][0] else 1.0
        m_reflect[1, 1] = -1.0 if state["reflect"][1] else 1.0
        m_reflect[2, 2] = -1.0 if state["reflect"][2] else 1.0

        m_rx = rotate_x(rot_rad[0])
        m_ry = rotate_y(rot_rad[1])
        m_rz = rotate_z(rot_rad[2])
        m_trans = translate(state["pan"][0], state["pan"][1], state["pan"][2])

        model = m_trans @ m_rz @ m_ry @ m_rx @ m_reflect @ m_scale

        r = state["cam_radius"]
        az = math.radians(state["cam_orbit_deg"][0])
        el = math.radians(state["cam_orbit_deg"][1])
        cam_x = r * math.cos(el) * math.sin(az)
        cam_y = r * math.sin(el)
        cam_z = r * math.cos(el) * math.cos(az)

        view = look_at([cam_x, cam_y, cam_z], [0.0, 0.0, 0.0], [0.0, 1.0, 0.0])
        proj = perspective(np.radians(45), 1280 / 720, 0.1, 100.0)

        plane_normal = angles_to_vector(state["plane_angles_deg"][0], state["plane_angles_deg"][1])
        light_dir = angles_to_vector(state["light_angles_deg"][0], state["light_angles_deg"][1])

        if renderer.vertex_count > 0:
            renderer.draw(model, view, proj, plane_normal, state["plane_h"], state["color"], light_dir)

        imgui.render()
        impl.render(imgui.get_draw_data())

        glfw.swap_buffers(window)

    impl.shutdown()
    glfw.terminate()


if __name__ == "__main__":
    main()