# Cogist

🧠 A Beautiful Mind Mapping Tool with Intelligent Layout Algorithms

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![PySide6 6.8+](https://img.shields.io/badge/PySide6-6.8+-green.svg)](https://doc.qt.io/qtforpython-6/)
[![Changelog](https://img.shields.io/badge/changelog-latest-purple.svg)](CHANGELOG.md)

## ✨ Core Features

### 🎨 Professional Curve Rendering
- Gradient curve with varying line width (10→2 pixels)
- Smart edge anchor point selection
- Smooth S-shaped Bezier curves
- Auto-matching curve colors to branches
- High-performance rendering with path caching

### 🧩 Intelligent Layout Algorithm
- Center-radial layout with balanced distribution
- Automatic node overlap prevention
- Real-time adjustment on drag
- Configurable spacing levels (Compact/Normal/Relaxed/Spacious)

### 🎯 Perfect Interaction Experience
- Drag parent node - children follow
- Keyboard navigation (arrow keys for panning)
- View zoom (+/-/0 keys)
- Real-time curve updates
- Undo/Redo support (Ctrl+Z/Y)
- Node editing (Tab, Enter, Delete, Space)

### 🎭 Advanced Style System
- Role-based styling (Root/Primary/Secondary/Tertiary)
- Template + Color Scheme separation
- Customizable shapes, borders, backgrounds
- Font decorations (Italic, Underline, Strikethrough)
- Real-time preview in Settings Panel
- Save and load custom templates

## 🛠️ Tech Stack

- **Python 3.13+**
- **PySide6 6.8+** (Qt for Python)
- **QGraphicsView Framework** (2D graphics rendering)
- **uv** (Modern Python package manager)

## 📦 Installation

```bash
# Using uv (recommended)
uv install

# Or using pip
pip install pyside6 qdarkstyle qt-material
```

## 🚀 Quick Start

```bash
# Using uv (recommended)
uv run cogist

# Or run main.py directly
uv run python main.py
```

### Keyboard Shortcuts

- **Arrow keys** - Pan canvas
- **+ / =** - Zoom in
- **-** - Zoom out
- **0** - Reset view
- **Space** - Edit node text
- **Tab** - Add child node
- **Enter** - Add sibling node
- **Delete** - Delete selected node
- **Ctrl/Cmd + Z** - Undo
- **Ctrl/Cmd + Y** - Redo

## 📁 Project Structure

```
cogist/
├── main.py                 # Main application entry point
├── pyproject.toml          # Project configuration
├── README.md               # Project documentation
├── LICENSE                 # License file
├── CHANGELOG.md            # Version history
├── docs/                   # 📚 Documentation center
│   ├── INDEX.md                    # Documentation index
│   ├── ARCHITECTURE.md             # Architecture design
│   ├── DESIGN_PHILOSOPHY.md        # Design philosophy
│   ├── PRODUCT_STRATEGY.md         # Product strategy
│   ├── ROADMAP.md                  # Development roadmap
│   └── zh-CN/                      # Chinese documentation
├── cogist/                 # Source code package
│   ├── domain/             # Domain layer (entities, value objects, styles, layout)
│   │   ├── entities/       # Node, Edge entities
│   │   ├── styles/         # Style system (Template, ColorScheme, RoleBasedStyle)
│   │   ├── layout/         # Layout algorithms and registry
│   │   └── colors/         # Color theme definitions
│   ├── application/        # Application layer (services, commands)
│   │   ├── services/       # MindMapService, NodeService
│   │   └── commands/       # Command pattern (AddNode, DeleteNode, EditText)
│   ├── presentation/       # Presentation layer (UI components)
│   │   ├── items/          # QGraphicsItem implementations (NodeItem, EdgeItem)
│   │   ├── dialogs/        # Dialogs (StylePanel with Simple/Advanced modes)
│   │   └── widgets/        # Custom widgets
│   └── infrastructure/     # Infrastructure layer (persistence, plugins)
│       ├── repositories/   # Data persistence
│       ├── io/             # Serialization (JSON)
│       └── plugins/        # Plugin system
└── tests/                  # Unit tests
```

## 🎯 Key Features

### Main Application (`main.py`)

**Core Functionality:**
- Smart curve connection with automatic edge anchor selection
- Gradient line width curves for professional appearance
- Child node following when dragging parent
- Keyboard navigation (pan + zoom)
- Branch color differentiation
- High-performance rendering with path caching
- Undo/Redo support (Ctrl+Z/Y)
- Node editing (Tab, Enter, Delete, Space)
- File save/load in `.cgs` format (JSON-based ZIP container)

**Settings Panel:**
- Dual-mode design: Simple Mode (placeholder) + Advanced Mode (full features)
- Layer-based style editing (Root/Level 1/Level 2/Level 3+)
- Real-time preview of all style changes
- Customizable shapes, borders, backgrounds, fonts
- Font decorations: Italic, Underline, Strikethrough
- Template and Color Scheme management

**Run:**
```bash
uv run python main.py
# or
uv run cogist
```

## 🔧 Development Guide

### Architecture Overview

Cogist follows a **Domain-Driven Design (DDD)** with four-layer architecture:

1. **Domain Layer** - Core business logic (entities, styles, layout algorithms)
2. **Application Layer** - Business orchestration (services, commands)
3. **Infrastructure Layer** - Technical implementation (persistence, serialization)
4. **Presentation Layer** - User interface (Qt widgets, graphics items)

### Add New Layout

```python
from cogist.domain.layout import BaseLayout

class CustomLayout(BaseLayout):
    def calculate_positions(self, root_node):
        # Implement your layout algorithm
        # Return dict mapping node_id -> (x, y) positions
        pass
```

### Customize Node Style

```python
from cogist.presentation.items.node_item import NodeItem

class CustomNodeItem(NodeItem):
    def paint(self, painter, option, widget):
        # Custom drawing logic
        super().paint(painter, option, widget)
```

### Extend Style Templates

```python
from cogist.domain.styles import Template, RoleBasedStyle, NodeRole

# Create custom template
template = Template(
    name="my_template",
    description="My custom template",
    role_styles={
        NodeRole.ROOT: RoleBasedStyle(...),
        NodeRole.PRIMARY: RoleBasedStyle(...),
        # ...
    }
)
```

## 📸 Screenshots

After running the program, you can experience:
- Center-radial layout with balanced node distribution
- Color-coded nodes for different branches
- Gradient curves connecting parent-child nodes
- Interactive drag and zoom functionality
- Real-time style preview in Settings Panel
- Professional appearance with customizable templates

## 📝 License

This project uses the **MIT License**, but includes important third-party dependency license notices:

### Your Rights
- Free to use (including commercial use)
- Free to modify and distribute
- Free to keep code closed source
- ⚠️ Must comply with PySide6's LGPL license

### Third-Party Licenses
This project depends on **PySide6 (Qt for Python)**, which uses the **LGPL-3.0** license.
See the [LICENSE](LICENSE) file for compliance requirements.

In simple terms:
- You can use Cogist to develop closed-source commercial software
- ⚠️ You cannot modify PySide6 without open-sourcing those modifications
- ⚠️ You must allow users to replace the PySide6 library

See the [LICENSE](LICENSE) file for the complete license text.

---

**Cogist** - Map Your Thinking 🧠

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![PySide6 6.8+](https://img.shields.io/badge/PySide6-6.8+-green.svg)](https://doc.qt.io/qtforpython-6/)
[![Changelog](https://img.shields.io/badge/changelog-latest-purple.svg)](CHANGELOG.md)

