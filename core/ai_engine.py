import sys
import os
import base64
import numpy as np
import trimesh
from dotenv import load_dotenv
from groq import Groq
from shapely.geometry import Polygon

# --- BULLETPROOF CONFIG ---
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
    env_path = os.path.join(base_dir, "..", ".env")
else:
    env_path = ".env"

load_dotenv(env_path)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# --- MANUAL GEOMETRY FALLBACKS (If library fails) ---
def manual_dodecahedron():
    """Manual Golden Ratio vertex math for Dodecahedron"""
    phi = (1 + np.sqrt(5)) / 2
    pts = []
    for i in [-1, 1]:
        for j in [-1, 1]:
            for k in [-1, 1]: pts.append([i, j, k])
            pts.append([0, i * phi, j / phi])
            pts.append([i / phi, 0, j * phi])
            pts.append([i * phi, j / phi, 0])
    return trimesh.ConvexHull(pts).to_mesh()


def generate_regular_polygon(n_sides, radius=1.0):
    angles = np.linspace(0, 2 * np.pi, n_sides, endpoint=False)
    vertices = [[radius * np.cos(a), radius * np.sin(a)] for a in angles]
    return Polygon(vertices)


# --- THE BRAIN (STRONGER PROMPT) ---
def detect_intent_groq(image_path):
    with open(image_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode('utf-8')

    # Tell the AI exactly what we expect
    prompt = (
        "Identify the 3D geometric shape. You MUST choose one: "
        "star, pyramid, cube, sphere, cylinder, torus, cone, rod, plate, "
        "pentagon, hexagon, octagon, dodecahedron, diamond, cross, crescent. "
        "Return ONLY the word."
    )

    try:
        res = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": [{"type": "text", "text": prompt},
                                                   {"type": "image_url",
                                                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}]}],
            temperature=0.0
        )
        return res.choices[0].message.content.lower()
    except:
        return "complex"


# --- THE ENGINE (FLEXIBLE MATCHING) ---
def generate_math_mesh(raw_intent, out_obj):
    # THE FIX: Partial matching. If the AI says 'A hexagon', we find 'hexagon'.
    intent = raw_intent.lower()
    print(f"[DEBUG] AI Said: '{intent}'")

    mesh = None

    # Priority matching
    if "rod" in intent:
        mesh = trimesh.creation.cylinder(radius=0.05, height=6.0)
    elif "plate" in intent:
        mesh = trimesh.creation.box(extents=(4.0, 3.0, 0.1))
    elif "hexagon" in intent:
        mesh = trimesh.creation.extrude_polygon(generate_regular_polygon(6), height=0.5)
    elif "pentagon" in intent:
        mesh = trimesh.creation.extrude_polygon(generate_regular_polygon(5), height=0.5)
    elif "octagon" in intent:
        mesh = trimesh.creation.extrude_polygon(generate_regular_polygon(8), height=0.5)
    elif "dodecahedron" in intent:
        mesh = manual_dodecahedron()
    elif "diamond" in intent or "gemstone" in intent:
        # Octahedron vertex math
        mesh = trimesh.creation.uv_sphere(radius=1.0, count=[4, 2])
    elif "star" in intent:
        n = 5
        pts = [[1.0 if i % 2 == 0 else 0.4, i * np.pi / n - np.pi / 2] for i in range(n * 2)]
        c_pts = [[r * np.cos(t), r * np.sin(t)] for r, t in pts]
        mesh = trimesh.creation.extrude_polygon(Polygon(c_pts), height=0.4)
    elif "cross" in intent:
        # Simple plus shape logic
        b1 = trimesh.creation.box(extents=[2, 0.5, 0.5])
        b2 = trimesh.creation.box(extents=[0.5, 2, 0.5])
        mesh = trimesh.util.concatenate([b1, b2])
    elif "torus" in intent:
        mesh = trimesh.creation.torus(minor_radius=0.25, major_radius=1.0)
    elif "cylinder" in intent:
        mesh = trimesh.creation.cylinder(radius=1.0, height=2.0)
    elif "sphere" in intent:
        mesh = trimesh.creation.icosphere(subdivisions=3)
    elif "pyramid" in intent:
        mesh = trimesh.creation.cone(radius=1.0, height=1.5, sections=4)
    elif "cone" in intent:
        mesh = trimesh.creation.cone(radius=1.0, height=1.5, sections=32)
    else:
        # Final fallback
        mesh = trimesh.creation.box()

    mesh.fix_normals()
    mesh.export(out_obj)


if __name__ == "__main__":
    if len(sys.argv) > 2:
        generate_math_mesh(detect_intent_groq(sys.argv[1]), sys.argv[2])