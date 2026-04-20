<div align="center">

<img src="https://img.shields.io/badge/version-1.2.1--beta-blueviolet?style=for-the-badge&logo=opengl" />
<img src="https://img.shields.io/badge/python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/OpenGL-3.3%2B-green?style=for-the-badge&logo=opengl" />
<img src="https://img.shields.io/badge/AI-Groq%20Cloud-orange?style=for-the-badge" />
<img src="https://img.shields.io/badge/license-MIT-lightgrey?style=for-the-badge" />

<br/><br/>

# 🧊 SliceView

### *AI-Powered 3D Visualization & Sectional Analysis*

> A high-performance 3D synthesis tool that bridges a custom OpenGL rendering engine with an agentic AI pipeline — analyzing 2D visual intent and generating parametric 3D geometry in real time via Groq's LPU inference.

<br/>

---

</div>

<br/>

## ✨ Features at a Glance

| Category | Feature | Description |
|----------|---------|-------------|
| 🪄 AI Engine | **AI-Driven 3D Synthesis** | Classify 2D images via Groq Vision and instantly synthesize mathematical 3D meshes |
| 🔪 Analysis | **Precision Sectional Clipping** | Real-time clipping planes with automated oscillating scan modes |
| 🎮 Workspace | **Dynamic 3D Control** | Full translation, rotation, scaling, and reflection via an ImGui dashboard |
| 💡 Lighting | **Advanced Light Architecture** | Adjustable pitch & yaw for cinematic, high-contrast shadow emphasis |
| 🔄 System | **Master Reset** | One-click factory reset for all transforms and camera orbits |

<br/>

---

## 🛠️ Tech Stack

```
SliceView
├── Graphics       → OpenGL (Core Profile 3.3+), GLFW
├── GUI            → Dear ImGui  (pyimgui)
├── AI Engine      → Groq Cloud API  (Llama 3 / Vision-Scout)
├── Processing     → NumPy, Trimesh, Shapely, Pillow
└── Deployment     → PyInstaller  (One-Dir + Subprocess Bridge)
```

<br/>

---

## 🚀 Getting Started

### For Users — Executable (Windows)

1. **Download** the latest `SliceView_Windows.zip` from the [Releases](../../releases) tab.
2. **Extract** the archive into a folder of your choice.
3. **Create a `.env` file** in the root directory (next to `SliceView.exe`):

```env
GROQ_API_KEY=your_groq_api_key_here
```

> 💡 Don't have a Groq API key? Get one for free at [console.groq.com](https://console.groq.com).

4. **Run** `SliceView.exe`.

---

### For Developers — From Source

**Prerequisites:** Python 3.10+, `pip`, OpenGL-capable GPU

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/SliceView.git
cd SliceView

# 2. (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your environment
cp .env.example .env
# Add your GROQ_API_KEY to the .env file

# 5. Launch
python main.py
```

<br/>

---

## 🎮 Interface & Controls

### Dashboard Overview

```
┌─────────────────────────────────────────────────────────────┐
│  SliceView  v1.2.1                                    [Beta] │
├────────────┬───────────────┬──────────────┬─────────────────┤
│  AI Panel  │  Mesh Visuals │  Slice Ctrl  │  System         │
├────────────┼───────────────┼──────────────┼─────────────────┤
│ [Generate] │  Mesh Color   │ Slice Toggle │  Master Reset   │
│  Drop Zone │  (RGB Picker) │  Auto Scan   │  Light Pitch    │
│            │               │  Plane Pos   │  Light Yaw      │
└────────────┴───────────────┴──────────────┴─────────────────┘
```

### Control Reference

| Section | Control | Action |
|---------|---------|--------|
| **Data** | AI Generate | Upload a 2D image → classify geometric intent → synthesize 3D mesh |
| **Visuals** | Mesh Color | Real-time vertex color modification via RGB picker |
| **Analysis** | Slicing Toggle | Enable / disable the clipping plane engine |
| **Analysis** | Auto Scan | Oscillate the clipping plane automatically through the mesh |
| **Analysis** | Plane Position | Manually scrub the clipping plane along the chosen axis |
| **Lighting** | Light Pitch | Adjust vertical angle of the scene light source |
| **Lighting** | Light Yaw | Adjust horizontal angle of the scene light source |
| **System** | Master Reset | Snap all transforms + camera back to factory defaults |

<br/>

---

## 🧠 How the AI Pipeline Works

```
Input Image (2D)
      │
      ▼
┌─────────────────────────┐
│  Groq Vision API        │  ← Llama Vision-Scout model
│  Geometric Intent       │     classifies shape topology
│  Classification         │
└────────────┬────────────┘
             │  intent label + parameters
             ▼
┌─────────────────────────┐
│  Parametric Mesh        │  ← NumPy + Trimesh + Shapely
│  Synthesis Engine       │     generates mathematical mesh
└────────────┬────────────┘
             │  vertex + face data
             ▼
┌─────────────────────────┐
│  OpenGL Renderer        │  ← Real-time rendering
│  + ImGui Dashboard      │     with clipping plane support
└─────────────────────────┘
```

<br/>

---

## 📁 Project Structure

```
SliceView/
│
├── main.py                  # Entry point
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variable template
│
├── core/
│   ├── renderer.py          # OpenGL rendering engine (GLFW + shaders)
│   ├── mesh_builder.py      # Parametric 3D mesh synthesis
│   └── slicer.py            # Clipping plane logic
│
├── ai/
│   ├── groq_client.py       # Groq API integration
│   └── intent_classifier.py # 2D → geometric intent pipeline
│
├── gui/
│   └── dashboard.py         # Dear ImGui panel layout
│
└── assets/
    └── shaders/             # GLSL vertex & fragment shaders
```

<br/>

---

## 🔧 Configuration

| Environment Variable | Required | Description |
|---------------------|----------|-------------|
| `GROQ_API_KEY` | ✅ Yes | Your Groq Cloud API key |
| `SLICEVIEW_LOG_LEVEL` | ❌ Optional | Set to `DEBUG` for verbose output (default: `INFO`) |
| `SLICEVIEW_WINDOW_W` | ❌ Optional | Initial window width in pixels (default: `1280`) |
| `SLICEVIEW_WINDOW_H` | ❌ Optional | Initial window height in pixels (default: `720`) |

<br/>

---

## 🗺️ Roadmap

- [x] AI-driven mesh synthesis via Groq Vision
- [x] Real-time clipping plane with auto-scan
- [x] Master reset system
- [x] Dynamic lighting controls
- [ ] Export mesh as `.obj` / `.stl`
- [ ] Multi-model comparison view
- [ ] Cross-section measurement tools
- [ ] Linux & macOS builds
- [ ] Local LLM fallback support (Ollama)

<br/>

---

## 🤝 Contributing

Contributions, bug reports, and feature requests are welcome!

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

Please follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages.

<br/>

---

## 📜 License

This project is licensed under the **MIT License** — see the [`LICENSE`](LICENSE) file for details.

<br/>

---

<div align="center">

Developed with ❤️ by **Shopnil**

*Graphic Designer & Aspiring ML Engineer · BUBT*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat-square&logo=linkedin)](https://linkedin.com)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?style=flat-square&logo=github)](https://github.com)

<br/>

*If SliceView helped you, consider giving it a ⭐ — it helps a lot!*

</div>
