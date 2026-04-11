# Cogist

🧠 A Beautiful Mind Mapping Tool with Intelligent Layout Algorithms

编织思维的图谱 - Map Your Thinking

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![PySide6 6.8+](https://img.shields.io/badge/PySide6-6.8+-green.svg)](https://doc.qt.io/qtforpython-6/)
[![Changelog](https://img.shields.io/badge/changelog-latest-purple.svg)](CHANGELOG.md)

## ✨ Core Features

### 🎨 Professional Curve Rendering
- ✅ Gradient curve with varying line width (10→2 pixels)
- ✅ Smart edge anchor point selection
- ✅ Smooth S-shaped Bezier curves
- ✅ Auto-matching curve colors to branches
- ✅ High-performance rendering with path caching

### 🧩 Intelligent Layout Algorithm
- ✅ Default-style center-radial layout
- ✅ Automatic node overlap prevention
- ✅ Balanced left/right distribution
- ✅ Real-time adjustment on drag

### 🎯 Perfect Interaction Experience
- ✅ Drag parent node - children follow
- ✅ Keyboard navigation (arrow keys for panning)
- ✅ View zoom (+/-/0 keys)
- ✅ Real-time curve updates

## 🛠️ Tech Stack

- **Python 3.13+**
- **PySide6 6.8+** (Qt for Python)
- **QGraphicsView Framework** (2D graphics view)
- **uv** (Modern Python package manager)

## 📦 Installation

```bash
# Using uv (recommended)
uv install

# Or using pip
pip install pyside6 qdarkstyle qt-material
```

## 🌍 Documentation

**English:** [docs/INDEX.md](docs/INDEX.md)  
**简体中文:** [docs/zh-CN/INDEX.md](docs/zh-CN/INDEX.md)

See [Documentation Structure](docs/README_docs.md) for details.

## 🚀 Quick Start

```bash
# Using uv (recommended)
uv install

# Run the application
uv run cogist

# Or run main.py directly
uv run python main.py
```

### Keyboard Shortcuts

- **Arrow keys** - Pan canvas
- **+ / =** - Zoom in
- **-** - Zoom out
- **0** - Reset view

## 📁 Project Structure

```
cogist/
├── main.py                 # Main application entry point
├── pyproject.toml          # Project configuration
├── README.md               # Project documentation
├── LICENSE                 # License file
├── QUICKSTART.md           # Quick start guide
├── docs/                   # 📚 Documentation center
│   ├── INDEX.md                    # Documentation index
│   ├── PRODUCT_STRATEGY.md         # Product strategy
│   ├── FEATURES.md                 # Feature requirements
│   ├── FEATURES_SUMMARY.md         # Feature summary
│   ├── TECHNICAL_IMPLEMENTATION.md # Technical implementation
│   ├── ARCHITECTURE.md             # Architecture design
│   ├── LICENSE_GUIDE.md            # License guide
│   └── ...                         # Other docs
├── cogist/                 # Source code package
│   ├── domain/             # Domain layer (entities, value objects, layout)
│   ├── presentation/       # Presentation layer (items, widgets)
│   ├── application/        # Application layer (to be added)
│   └── infrastructure/     # Infrastructure layer (to be added)
└── tests/                  # Tests (to be added)
```

## 🎯 Core Feature Demo

### Main Application (`main.py`)

**Flagship Features:**
- ✅ Smart curve connection (automatic edge anchor selection)
- ✅ Gradient line width curve (professional appearance)
- ✅ Child node following (drag parent node)
- ✅ Keyboard navigation (pan + zoom)
- ✅ Branch color differentiation
- ✅ High-performance rendering
- ✅ Undo/Redo support (Ctrl+Z/Y)
- ✅ Node editing (Tab, Enter, Delete, Space)

**Run:**
```bash
uv run python main.py
# or
uv run cogist
```

## 🔧 Development Guide

### Add New Layout

```python
class CustomLayout:
    def layout(self, root):
        # Implement your layout algorithm
        pass
```

### Customize Node Style

```python
class CustomNodeItem(NodeItem):
    def paint(self, painter, option, widget):
        # Custom drawing logic
        pass
```

## 📸 Screenshots

After running the program, you can see:
- Default Default style layout
- Color-coded nodes for different branches
- Gradient curves connecting nodes
- Drag and zoom to view effects

## 📝 License

This project uses the **MIT License**, but includes important third-party dependency license notices:

### Your Rights
- ✅ Free to use (including commercial use)
- ✅ Free to modify and distribute
- ✅ Free to keep code closed source
- ⚠️ Must comply with PySide6's LGPL license

### Third-Party Licenses
This project depends on **PySide6 (Qt for Python)**, which uses the **LGPL-3.0** license.
See the [LICENSE](LICENSE) file for compliance requirements.

In simple terms:
- ✅ You can use Cogist to develop closed-source commercial software
- ⚠️ You cannot modify PySide6 without open-sourcing those modifications
- ⚠️ You must allow users to replace the PySide6 library

See the [LICENSE](LICENSE) file for the complete license text.

---

**Cogist** - Map Your Thinking 🧠

