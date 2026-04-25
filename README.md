<div align="center">

<img src="https://img.shields.io/badge/version-1.2.1--beta-blueviolet?style=for-the-badge" />
<img src="https://img.shields.io/badge/python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/OpenGL-3.3%20Core-green?style=for-the-badge&logo=opengl" />
<img src="https://img.shields.io/badge/AI-Groq%20LPU-orange?style=for-the-badge" />
<img src="https://img.shields.io/badge/license-MIT-lightgrey?style=for-the-badge" />

<br/><br/>

# 🧊 SliceView

### *AI-Powered 3D Visualization & Sectional Analysis*

> A high-performance 3D visualization tool for educational and industrial inspection — combining a custom OpenGL renderer with a decoupled AI pipeline that translates 2D images into inspectable 3D geometry in near real-time, powered by Groq's LPU inference.

<br/>

---

</div>

## ✨ Features at a Glance

| Category | Feature | Description |
|----------|---------|-------------|
| 🪄 AI Engine | **AI Intent Recognition** | Translates 2D images (e.g. a photo of a donut) into 3D primitives (e.g. a torus) via Llama-4-Scout Vision |
| 🔪 Analysis | **Precision Sectional Clipping** | Dynamic clipping plane engine using `Ax + By + Cz + D = 0`, evaluated per-fragment in the shader |
| 🔄 Analysis | **Auto-Scan Mode** | Sine-wave oscillation of the clipping plane for automated internal structure inspection |
| 🎮 Workspace | **Dynamic 3D Control** | Full translation, rotation, scaling, and reflection via an ImGui Dark Mode dashboard |
| 💡 Lighting | **Sculptural Lighting** | Real-time shading with user-defined Light Pitch and Yaw for high-contrast cinematic detail |
| 🔄 System | **Master Reset** | Snap-to-default for scale, pan, rotation, and camera orbit in a single click |

<br/>

---

## 🛠️ Tech Stack

```
SliceView
├── Language        → Python 3.9+
├── Graphics API    → Modern OpenGL 3.3 (Core Profile)
├── Window Mgmt     → GLFW
├── GUI             → Dear ImGui (pyimgui) — custom Dark Mode theme
├── AI Inference    → Groq LPU Cloud API
│   └── Model       → meta-llama/llama-4-scout-17b-16e-instruct (Vision)
├── Math / Geometry → NumPy · Shapely · Trimesh
└── Distribution    → PyInstaller (One-Dir GUI + One-File AI Worker)
```

<br/>

---

## 🏗️ Architecture

SliceView runs on a **dual-process architecture** to keep the GUI fluid during AI inference latency.

```
┌─────────────────────────────────────────────────┐
│               Main Process  (main.exe)           │
│                                                  │
│  OpenGL Renderer ──► ImGui Dashboard             │
│        │                    │                    │
│        │             User triggers               │
│        │             AI Generate                 │
│        │                    │                    │
│        │       subprocess call                   │
│        │         + threading.Thread              │
│        │         (async monitor)                 │
│        │                    │                    │
│        │                    ▼                    │
│        │   ┌────────────────────────────────┐   │
│        │   │   AI Worker  (ai_engine.exe)   │   │
│        │   │                                │   │
│        │   │  Groq Vision API               │   │
│        │   │  (Llama-4-Scout)               │   │
│        │   │       │                        │   │
│        │   │       ▼                        │   │
│        │   │  Parametric Mesh Synthesis     │   │
│        │   │  (NumPy · Shapely · Trimesh)   │   │
│        │   │       │                        │   │
│        │   │       ▼                        │   │
│        │   │  Writes  output.obj  to disk   │   │
│        │   └───────────────┬────────────────┘   │
│        │                   │  filesystem         │
│        ◄───────────────────┘  (bridge)           │
│  Parses .obj → uploads                          │
│  vertices to GPU buffer                          │
└─────────────────────────────────────────────────┘
```

> The bridge is **filesystem-based**: the AI worker writes a `.obj` file to disk, which the main process parses and uploads to the GPU buffer via a custom `obj_parser`.

<br/>

---

## 📁 Production File Structure

```
SliceView/
│
├── main.exe                      # Compiled GUI application (One-Dir mode)
├── .env                          # External config  →  GROQ_API_KEY=...
│
├── _internal/                    # PyInstaller runtime DLLs & libraries
│
├── assets/                       # Read-only resource directory
│   ├── icon.png                  # Window icon
│   ├── icon.ico                  # Windows metadata icon
│   └── models/
│       └── HumanHeart_OBJ.obj    # Default startup mesh
│
└── ai_engine/
    └── ai_engine.exe             # Standalone AI worker (One-File mode)
```

> **Source-only** (`core/` directory — not shipped in the binary):
>
> ```
> core/
> ├── ai_engine.py     # Groq Vision + parametric mesh logic
> ├── renderer.py      # OpenGL draw calls & shader management
> ├── math_engine.py   # Matrix transforms (rotation, projection)
> └── obj_parser.py    # Custom vertex / normal / index extraction
> ```

<br/>

---

## 🚀 Getting Started

### For Users — Windows Executable

1. **Download** the latest `SliceView_Windows.zip` from the [Releases](../../releases) tab.
2. **Extract** the folder — keep all contents together, do not move files individually.
3. **Create a `.env` file** in the root directory (next to `main.exe`):

```env
GROQ_API_KEY=your_groq_api_key_here
```

> 💡 Get a free Groq API key at [console.groq.com](https://console.groq.com).

4. **Run** `main.exe`.

> ⚠️ If you see `[WinError 2]`, verify that `ai_engine/ai_engine.exe` is present in its subfolder. If you see `[WinError 5]` (Access Denied), ensure `main.exe` is not already running before recompiling.

---

### For Developers — From Source

**Requirements:** Python 3.9+, OpenGL-capable GPU

```bash
# 1. Clone the repository
git clone https://github.com/k-shopnil/SliceView.git
cd SliceView

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key
echo GROQ_API_KEY=your_key_here > .env

# 5. Run
python main.py
```

<br/>

---

## 🎮 Interface & Controls

```
┌──────────────┬──────────────┬───────────────┬─────────────────┐
│   AI Panel   │    Visuals   │   Slice Ctrl  │     System      │
├──────────────┼──────────────┼───────────────┼─────────────────┤
│  [Generate]  │  Mesh Color  │ Slice Toggle  │  Master Reset   │
│  Image Input │  (RGB live)  │  Auto Scan    │  Light Pitch    │
│              │              │  Plane Pos    │  Light Yaw      │
└──────────────┴──────────────┴───────────────┴─────────────────┘
```

| Section | Control | Description |
|---------|---------|-------------|
| **AI** | Generate | Sends an image to Groq Vision → classifies geometric intent → synthesizes a 3D mesh |
| **Visuals** | Mesh Color | Real-time vertex color modification via RGB picker |
| **Analysis** | Slice Toggle | Enable / disable the fragment-shader clipping plane |
| **Analysis** | Auto Scan | Oscillates the clipping plane via a sine wave for automated inspection |
| **Analysis** | Plane Position | Manually position the clipping plane along the chosen axis |
| **Lighting** | Light Pitch | Adjust the vertical angle of the scene light source |
| **Lighting** | Light Yaw | Adjust the horizontal angle of the scene light source |
| **System** | Master Reset | Resets scale, pan, rotation, and camera orbit to factory defaults |

<br/>

---

## ⚙️ Technical Details

### Clipping Plane — Fragment Shader

The sectional analysis is computed per-fragment in GLSL. Any fragment with a negative signed distance to the plane is discarded:

$$\text{distance} = \vec{n} \cdot \vec{v} + h$$

where $\vec{n}$ is the plane normal, $\vec{v}$ is the vertex world position, and $h$ is the plane offset. The general plane equation is:

$$Ax + By + Cz + D = 0$$

### PyInstaller Frozen Path Resolution

A `resource_path()` helper bridges development paths and the PyInstaller `_MEIPASS` temp environment:

```python
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)
```

### Windows Subprocess — No Terminal Flash

The AI worker is launched with `CREATE_NO_WINDOW` to suppress the console popup on spawn:

```python
subprocess.Popen([...], creationflags=0x08000000)
```

### Viewport Far Plane

A far-plane distance of **1000.0 units** prevents z-clipping on large or dense meshes.

<br/>

---

## 🗺️ Roadmap

- [x] Groq LPU vision-to-mesh pipeline (Llama-4-Scout)
- [x] Fragment shader clipping plane with sine-wave auto-scan
- [x] Decoupled dual-process architecture (GUI + AI Worker)
- [x] Filesystem OBJ bridge with async thread monitor
- [x] Master reset system
- [x] Dynamic lighting (pitch + yaw)
- [ ] Export current mesh as `.stl` / `.glb`
- [ ] Cross-section measurement annotations
- [ ] Multi-mesh comparison viewport
- [ ] Linux & macOS builds
- [ ] Local LLM fallback (Ollama)

<br/>

---

## 🛠️ Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `[WinError 2]` | `ai_engine.exe` not found in its subfolder | Verify `ai_engine/ai_engine.exe` exists; check pathing in `main.py` |
| `[WinError 5]` Access Denied | Recompiling while `main.exe` is still running | Close the application fully before recompiling |
| `UnicodeEncodeError` | Emoji characters printed to a CP1252 Windows console | Use plain text tags like `[SUCCESS]` instead of emoji in print/log statements |
| Blank Viewport | Scale or distance value out of range | Hit **Master Reset** to re-center the mesh |

<br/>

---

## 🤝 Contributing

Contributions, bug reports, and feature requests are welcome!

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit following [Conventional Commits](https://www.conventionalcommits.org/): `git commit -m "feat: add your feature"`
4. Push and open a Pull Request

<br/>

---

## 📜 License

This project is licensed under the **MIT License** — see the [`LICENSE`](LICENSE) file for details.

<br/>

---

<div align="center">

Developed by **Shopnil**

*Graphic Designer · Aspiring ML Engineer & Data Analyst · BUBT*

[![GitHub](https://img.shields.io/badge/GitHub-k--shopnil-black?style=flat-square&logo=github)](https://github.com/k-shopnil)

<br/>

*Found SliceView useful? Drop a ⭐ — it means a lot!*

</div>
