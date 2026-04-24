# Cogist

🧠 A Beautiful Mind Mapping Tool with Intelligent Layout Algorithms

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![PySide6 6.8+](https://img.shields.io/badge/PySide6-6.8+-green.svg)](https://doc.qt.io/qtforpython-6/)
[![Version: 0.3.7](https://img.shields.io/badge/version-0.3.7-purple.svg)](https://github.com/cogist/cogist/releases/tag/v0.3.7)
[![Changelog](https://img.shields.io/badge/changelog-latest-orange.svg)](CHANGELOG.md)

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

### 🎭 Advanced Style System (v0.3.0)
- Role-based styling (Root/Primary/Secondary/Tertiary)
- Template + Color Scheme separation
- Customizable shapes, borders, backgrounds, shadows
- Font decorations (Italic, Underline, Strikethrough)
- Real-time preview in Settings Panel
- Save and load custom templates
- Multiple connector styles (Bezier, Orthogonal, Rounded)
- Abstract spacing levels (Compact/Normal/Relaxed/Spacious)

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
├── CHANGELOG.md            # Version history (v0.3.7 latest)
├── docs/                   # 📚 Documentation center
│   ├── ARCHITECTURE.md             # Architecture design
│   ├── DESIGN_PHILOSOPHY.md        # Design philosophy
│   ├── PRODUCT_STRATEGY.md         # Product strategy
│   └── ROADMAP.md                  # Development roadmap
├── cogist/                 # Source code package
│   ├── domain/             # Domain layer (entities, styles, layout, connectors, borders)
│   │   ├── entities/       # Node, Edge entities
│   │   ├── styles/         # Style system (Template, ColorScheme, RoleBasedStyle, SpacingConfig)
│   │   │   ├── extended_styles.py  # Core style data structures
│   │   │   └── style_resolver.py   # Style resolution and serialization
│   │   ├── connectors/     # Connector algorithms (Bezier, Orthogonal, Rounded, etc.)
│   │   ├── borders/        # Border system (Container, Decorative lines)
│   │   ├── layout/         # Layout algorithms and registry
│   │   └── colors/         # Color theme definitions
│   ├── application/        # Application layer (services, commands)
│   │   ├── services/       # MindMapService, AppContext
│   │   └── commands/       # Command pattern (AddNode, DeleteNode, EditText)
│   ├── presentation/       # Presentation layer (UI components)
│   │   ├── items/          # QGraphicsItem implementations (NodeItem, EdgeItem)
│   │   ├── dialogs/        # Dialogs (StylePanelAdvanced, ActivityBar)
│   │   │   ├── style_panel_advanced.py  # Advanced style panel
│   │   │   └── style_widgets/           # Reusable style widgets
│   │   └── widgets/        # Custom widgets (ConnectorPreviews, VisualSelector, etc.)
│   └── infrastructure/     # Infrastructure layer (persistence, serialization)
│       ├── repositories/   # Data persistence
│       └── io/             # Serialization (CGS format, JSON)
└── tests/                  # Unit tests
    ├── test_extended_styles.py
    ├── test_style_serialization.py
    └── test_cgs_serializer.py
```

## 🎯 Key Features

### Main Application (`main.py`)

**Core Functionality:**
- Smart curve connection with automatic edge anchor selection
- Gradient line width curves for professional appearance (10→2px)
- Child node following when dragging parent
- Keyboard navigation (pan + zoom)
- Branch color differentiation with role-based coloring
- High-performance rendering with path caching
- Undo/Redo support (Ctrl+Z/Y)
- Node editing (Tab, Enter, Delete, Space)
- File save/load in `.cgs` format (ZIP-compressed JSON container)
- Real-time style preview with Template + ColorScheme system

**Settings Panel:**
- Advanced mode with full-featured style editing
- Role-based style editing (Root/Primary/Secondary/Tertiary)
- Real-time preview of all style changes
- Customizable shapes, borders, backgrounds, shadows, fonts
- Font decorations: Italic, Underline, Strikethrough
- Template and Color Scheme management
- Multiple connector styles (Bezier, Orthogonal, Rounded, Sharp-First Rounded)
- Node shape previews and visual selectors

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
- Color-coded nodes for different branches (Root/Primary/Secondary/Tertiary)
- Gradient curves connecting parent-child nodes
- Interactive drag and zoom functionality
- Real-time style preview in Advanced Settings Panel
- Professional appearance with customizable templates
- Multiple connector styles (Bezier, Orthogonal, Rounded, Sharp-First Rounded)
- Node shapes (Rounded Rect, Circle, Ellipse, etc.) with live previews
- Shadow effects and font decorations
- Visual selectors for shapes, connectors, and borders

## 📖 Documentation

- **[Architecture](docs/ARCHITECTURE.md)** - System architecture overview
- **[Roadmap](docs/ROADMAP.md)** - Development roadmap and future plans
- **[Changelog](CHANGELOG.md)** - Version history and release notes

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

