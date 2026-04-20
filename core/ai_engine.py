import sys
import os
import base64
import numpy as np
import trimesh
from dotenv import load_dotenv
from groq import Groq
from shapely.geometry import Polygon

# --- CONFIGURATION ---
load_dotenv()
# Ensure your GROQ_API_KEY is securely stored in your .env file
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def detect_intent_groq(image_path):
    """The Vision Node: Uses Groq's LPU for near-instant classification."""
    print("⚡ Groq Architect is analyzing the image at lightspeed...")

    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')

    prompt = (
        "What is the primary geometric shape in this image? "
        "Respond with ONLY one word from this list: "
        "star, pyramid, cube, sphere, cylinder, torus, cone, or complex."
    )

    try:
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ],
                }
            ],
            temperature=0.0,
        )
        detected = response.choices[0].message.content.lower().strip(".,!? \n")
        print(f"👁️  Groq detected: {detected.upper()}")
        return detected
    except Exception as e:
        print(f"⚠️ Groq API Error: {e}")
        return "complex"


def generate_math_mesh(shape_name, out_obj):
    """Parametric Math Engine for 100% perfect educational shapes."""
    print(f"📐 Math Engine: Building a perfect 3D {shape_name}...")

    if shape_name == "sphere":
        mesh = trimesh.creation.icosphere(subdivisions=3, radius=1.0)
    elif shape_name in ["cube", "box"]:
        mesh = trimesh.creation.box()
    elif shape_name == "cylinder":
        mesh = trimesh.creation.cylinder(radius=1.0, height=2.0)
    elif shape_name == "torus":
        mesh = trimesh.creation.torus(minor_radius=0.25, major_radius=1.0)
    elif shape_name == "star":
        # Mathematical star extrusion using shapely
        n = 5
        r_outer, r_inner = 1.0, 0.4
        pts = [[r_outer if i % 2 == 0 else r_inner, i * np.pi / n - np.pi / 2] for i in range(n * 2)]
        cartesian_pts = [[r * np.cos(t), r * np.sin(t)] for r, t in pts]

        poly = Polygon(cartesian_pts)
        mesh = trimesh.creation.extrude_polygon(poly, height=0.4)
    elif shape_name in ["pyramid", "cone"]:
        sections = 4 if shape_name == "pyramid" else 32
        mesh = trimesh.creation.cone(radius=1.0, height=1.5, sections=sections)
    else:
        # BETA FALLBACK
        print("⚠️ Complex shape detected. Neural synthesis is disabled for Beta. Outputting default unit cube.")
        mesh = trimesh.creation.box()

    mesh.export(out_obj)


def make_3d():
    if len(sys.argv) < 3:
        print("Usage: python ai_engine.py <input.jpg> <output.obj>")
        return

    in_pic = sys.argv[1]
    out_obj = sys.argv[2]

    intent = detect_intent_groq(in_pic)
    generate_math_mesh(intent, out_obj)
    print(f"✅ Success! Saved geometry to {out_obj}")


if __name__ == "__main__":
    make_3d()