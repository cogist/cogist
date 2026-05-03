# Cogist Architecture Design

📋 **This document describes the layered architecture design and directory structure of Cogist**

**Quick Guide**: If you want to quickly understand the architecture, check the [Quick Overview](#-quick-overview) section.

---

## 🎯 Architecture Design Principles

### Core Design Philosophy

1. **Clear Layering** - Each layer has a single responsibility with clear boundaries
2. **Dependency Inversion** - High-level layers don't depend on low-level layers; both depend on abstractions
3. **Domain-Driven** - Business logic is the core, technology is support
4. **Extensibility First** - Easy to extend, loosely coupled
5. **Test-Friendly** - Each layer can be tested independently

---

## 🏗️ Layered Architecture Design

### 🚀 Quick Overview

**Four-Layer Architecture:**
```
┌─────────────────────────────────────┐
│   Presentation Layer (UI/Views)     │  ← QGraphicsView, Widgets
├─────────────────────────────────────┤
│   Application Layer (Orchestration)  │  ← Services, Commands
├─────────────────────────────────────┤
│   Domain Layer (Core Business)      │  ← Entities, Layout
├─────────────────────────────────────┤
│   Infrastructure Layer (Technical)   │  ← Repository, IO, Plugins
└─────────────────────────────────────┘
```

**Directory Structure (Simplified):**
```
cogist/
├── cogist/                          # Main package
│   ├── domain/                      # Domain Layer ⭐
│   ├── application/                 # Application Layer
│   ├── infrastructure/              # Infrastructure Layer
│   └── presentation/                # Presentation Layer
├── docs/                            # Documentation
├── tests/                           # Tests
└── examples/                        # Examples
```

**Core Ideas:**
- **Domain Driven** - Domain-driven design, business logic as the core
- **Dependency Inversion** - Dependency inversion, high-level doesn't depend on low-level
- **Separation of Concerns** - Separation of concerns, each layer has a single responsibility
- **Extension Friendly** - Extensibility first, easy to customize

---

### Overall Architecture (Four Layers)

```
┌─────────────────────────────────────────┐
│         Presentation Layer              │  ← Presentation Layer (UI/Views)
│    (Qt Widgets / QGraphicsView)         │
├─────────────────────────────────────────┤
│          Application Layer              │  ← Application Layer (Business Orchestration)
│   (Controllers / Services / Commands)   │
├─────────────────────────────────────────┤
│            Domain Layer                 │  ← Domain Layer (Core Business)
│   (Entities / Value Objects / Layout)   │
├─────────────────────────────────────────┤
│         Infrastructure Layer            │  ← Infrastructure Layer (Technical Implementation)
│  (Repository / IO / Plugins / Utils)    │
└─────────────────────────────────────────┘
```

---

### Detailed Layer Responsibilities

#### 1️⃣ **Presentation Layer**
**Responsibility:** User interface and interaction

**Important Principles:**
- ✅ **Contains drawing strategies** - connectors, borders belong to this layer (because they depend on Qt)
- ✅ **Thin UI Layer** - No business logic, only responsible for display and user input
- ❌ **Does not directly call layout algorithms** - Coordinated through Application Layer

**Components:**

**Views:**
- **Main Window** - Main window frame
- **MindMapView** - Mind map view (QGraphicsView)
  - Location: `cogist/presentation/views/mindmap_view.py`
  - Responsibility: UI rendering, user interaction, delegates layout calculation to Application Layer

**Items (Graphics Items):**
- **NodeItem** - Node graphics item (DefaultNodeItem)
- **EdgeItem** - Edge graphics item (DefaultEdgeItem)

**Rendering Strategies:** ⭐
- **ConnectorStrategy** - Edge style strategies
  - BezierConnector - Bezier curves
  - OrthogonalConnector - Orthogonal edges
  - StraightConnector - Straight lines
  - Location: `cogist/presentation/connectors/`
  
- **BorderStrategy** - Border decoration strategies
  - DecorativeBorder - Decorative borders
  - ContainerBorder - Container borders
  - Location: `cogist/presentation/borders/`

> ⚠️ **Why are connectors/borders in Presentation Layer?**
> 
> Because they are **drawing strategies**, not business logic:
> - They depend on Qt API (QPainterPath, QPen, QBrush, etc.)
> - Their responsibility is "how to draw", not "what are the business rules"
> - After moving, Domain Layer is completely pure, can be tested and reused independently

**Widgets:**
- **Toolbar** - Toolbar
- **MenuBar** - Menu bar
- **Dialogs** - Dialogs (edit, settings, etc.)
- **StylePanel** - Style panel

**Adapters:**
- **QtNodeProvider** - Qt node provider

**Dependencies:** 
- ↓ Application Layer (calls Application Service)
- → Qt Framework (PySide6)

**Characteristics:**
- No business logic
- Only responsible for display and user input
- Thin UI layer

---

#### 2️⃣ **Application Layer**
**Responsibility:** Business process orchestration and coordination

**Components:**
- **MindMapService** - Mind map service (create, save, export)
- **NodeService** - Node operation service (add, delete, edit)
- **LayoutService** - Layout service (execute layout algorithms)
- **ExportService** - Export service (PNG/SVG/Markdown)
- **ImportService** - Import service (Markdown/Default)
- **Command Pattern** - Command pattern implementation
  - AddNodeCommand
  - DeleteNodeCommand
  - EditTextCommand
  - MoveNodeCommand
  - StyleChangeCommand

**Dependencies:**
- ↓ Domain Layer (calls Domain Entities)
- → Infrastructure Layer (uses Repository)

**Characteristics:**
- Stateless
- Orchestrates domain objects to complete use cases
- Transaction management
- Permission validation

---

#### 3️⃣ **Domain Layer**
**Responsibility:** Core business logic and rules

**Important Principles:**
- ✅ **Pure without dependencies** - Does not depend on any UI framework (Qt, PySide6, etc.)
- ✅ **Pure business logic** - Only contains entities, value objects, algorithms
- ❌ **Does not contain drawing strategies** - connectors, borders belong to Presentation Layer

**Components:**

**Entities:**
- **MindMap** - Mind map root entity
- **Node** - Node entity
- **Edge** - Edge entity
- **Style** - Style value object
- **Position** - Position value object

**Value Objects:**
- **NodeId** - Node ID
- **NodeText** - Node text
- **Color** - Color value
- **BoundingBox** - Bounding box

**Layout Algorithms:**

Layout algorithms are core components of the domain layer, responsible for calculating node positions.

**BaseLayout Interface Design:**

```python
class BaseLayout(ABC):
    @abstractmethod
    def layout(
        self,
        root_node: Node,              # Tree structure entry point
        canvas_width: float = 1200.0,
        canvas_height: float = 800.0,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Execute layout for tree structures
        
        Applicable to: Default, Tree, Radial, Fishbone, Org Chart and other tree layouts
        """
        pass
    
    def layout_graph(
        self,
        nodes: list[Node],            # All nodes
        edges: list[Edge],            # All edges
        canvas_width: float = 1200.0,
        canvas_height: float = 800.0,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Execute layout for general graph structures (optional)
        
        Default implementation: fallback to tree-based layout
        Subclasses can override to support graph structure layouts
        
        Applicable to: Force-Directed, Concept Map, Flowchart and other graph layouts
        """
        if nodes:
            self.layout(nodes[0], canvas_width, canvas_height, context)
```

**Supported Layout Types:**

| Layout Type | Structure | Interface | Example |
|------------|-----------|-----------|---------|
| Default | Tree | `layout()` | Left-right balanced mind map |
| Tree | Tree | `layout()` | Vertical/horizontal tree |
| Radial | Tree | `layout()` | Radial layout |
| **Fishbone** | **Tree** | **`layout()`** | **Fishbone diagram (cause-effect analysis)** |
| Timeline | Tree | `layout()` | Timeline |
| Org Chart | Tree | `layout()` | Organizational chart |
| Force-Directed | Graph | `layout_graph()` | Force-directed network graph |
| Concept Map | Graph | `layout_graph()` | Concept map (may have cycles) |
| Flowchart | DAG | `layout_graph()` | Flowchart |

> 📖 **Detailed Design**: Complete architecture design of the layout system see [LAYOUT_ARCHITECTURE.md](LAYOUT_ARCHITECTURE.md)

**When to implement `layout_graph()`?**

✅ **Not needed** - If the layout is a tree structure (has clear root node and parent-child relationships)
- Examples: Default, Tree, Radial, Fishbone, Timeline, Org Chart

⚠️ **Needed** - If the layout is a graph structure (may have multiple parents, cycles, no root)
- Examples: Force-Directed, Concept Map, Network Diagram, Flowchart

**Services (Domain Services):**
- **LayoutManager** - Layout manager
- **NodeValidator** - Node validator

**Dependencies:**
- → No external dependencies (pure business logic)

**Characteristics:**
- Core value of the project
- Independent of UI and technical details
- Highly testable
- High stability

---

#### 4️⃣ **Infrastructure Layer**
**Responsibility:** Technical implementation and external dependencies

**Components:**

**Repositories:**
- **MindMapRepository** - Mind map persistence
- **PluginRepository** - Plugin management

**IO (Input/Output):**
- **JSONSerializer** - JSON serialization
- **MarkdownExporter** - Markdown export
- **ImageExporter** - Image export (PNG/SVG)
- **PDFExporter** - PDF export

**Plugins:**
- **PluginManager** - Plugin manager
- **PluginLoader** - Plugin loader
- **BasePlugin** - Plugin base class

**Utils:**
- **EventBus** - Event bus
- **Logger** - Logging
- **Config** - Configuration management
- **Clipboard** - Clipboard

**Dependencies:**
- → Domain Layer (implements Repository interface)
- → Third-party libraries (Qt, Numpy, Pandas, etc.)

**Characteristics:**
- Technical detail implementation
- Volatile (changes with tech stack)
- Replaceable (e.g., JSON→XML)

---

## 📁 Recommended Directory Structure

### Full Version (Production-Ready)

```
cogist/
│
├── 📄 README.md
├── 📄 pyproject.toml
├── 📄 uv.lock
├── 📄 .gitignore
│
├── 📁 cogist/                       # Main package
│   ├── __init__.py
│   │
│   ├── 📁 domain/                   # Domain Layer ⭐ Core
│   │   ├── __init__.py
│   │   ├── entities/                # Entities
│   │   │   ├── __init__.py
│   │   │   ├── mindmap.py          # MindMap entity
│   │   │   ├── node.py             # Node entity
│   │   │   ├── edge.py             # Edge entity
│   │   │   └── style.py            # Style value object
│   │   │
│   │   ├── value_objects/           # Value objects
│   │   │   ├── __init__.py
│   │   │   ├── position.py         # Position
│   │   │   ├── bounding_box.py     # BoundingBox
│   │   │   └── color.py            # Color
│   │   │
│   │   ├── layout/                  # Layout algorithms
│   │   │   ├── __init__.py
│   │   │   ├── base_layout.py      # Layout base class
│   │   │   ├── default_layout.py   # Default layout
│   │   │   ├── tree_layout.py      # Tree layout
│   │   │   ├── force_layout.py     # Force-directed layout
│   │   │   └── radial_layout.py    # Radial layout
│   │   │
│   │   └── services/                # Domain services
│   │       ├── __init__.py
│   │       ├── layout_manager.py   # Layout management
│   │       └── node_validator.py   # Node validation
│   │
│   ├── 📁 application/              # Application Layer
│   │   ├── __init__.py
│   │   ├── services/                # Application services
│   │   │   ├── __init__.py
│   │   │   ├── mindmap_service.py  # Mind map service
│   │   │   ├── node_service.py     # Node service
│   │   │   ├── layout_service.py   # Layout service
│   │   │   ├── export_service.py   # Export service
│   │   │   └── import_service.py   # Import service
│   │   │
│   │   └── commands/                # Command pattern
│   │       ├── __init__.py
│   │       ├── base_command.py     # Command base class
│   │       ├── add_node_command.py
│   │       ├── delete_node_command.py
│   │       ├── edit_text_command.py
│   │       └── move_node_command.py
│   │
│   ├── 📁 infrastructure/           # Infrastructure Layer
│   │   ├── __init__.py
│   │   ├── repositories/           # Repositories
│   │   │   ├── __init__.py
│   │   │   ├── mindmap_repository.py
│   │   │   └── plugin_repository.py
│   │   │
│   │   ├── io/                     # IO operations
│   │   │   ├── __init__.py
│   │   │   ├── json_serializer.py
│   │   │   ├── markdown_exporter.py
│   │   │   ├── image_exporter.py
│   │   │   └── pdf_exporter.py
│   │   │
│   │   ├── plugins/                # Plugin system (reserved extension point, not implemented yet)
│   │   │   ├── __init__.py
│   │   │   └── README.md           # Note: Evaluate after v1.0+ before implementing
│   │   │
│   │   └── utils/                  # Utilities
│   │       ├── __init__.py
│   │       ├── event_bus.py
│   │       ├── logger.py
│   │       ├── config.py
│   │       └── clipboard.py
│   │
│   └── 📁 presentation/            # Presentation Layer
│       ├── __init__.py
│       ├── main_window.py          # Main window
│       │
│       ├── 📁 views/               # Views
│       │   ├── __init__.py
│       │   └── mindmap_view.py     # Mind map view ⭐
│       │
│       ├── 📁 items/               # Graphics items
│       │   ├── __init__.py
│       │   ├── node_item.py        # DefaultNodeItem
│       │   └── edge_item.py        # DefaultEdgeItem
│       │
│       ├── 📁 connectors/          # Edge drawing strategies ⭐
│       │   ├── __init__.py
│       │   ├── base.py             # ConnectorStrategy base class
│       │   ├── bezier_connector.py # Bezier curves
│       │   ├── orthogonal_connector.py  # Orthogonal edges
│       │   └── straight_connector.py    # Straight lines
│       │
│       ├── 📁 borders/             # Border decoration strategies ⭐
│       │   ├── __init__.py
│       │   ├── base.py             # BorderStrategy base class
│       │   ├── decorative_lines.py # Decorative lines
│       │   └── container_borders.py # Container borders
│       │
│       ├── 📁 widgets/             # Custom widgets
│       │   ├── __init__.py
│       │   ├── toolbar.py
│       │   ├── menubar.py
│       │   ├── property_panel.py
│       │   └── outline_view.py
│       │
│       ├── 📁 dialogs/             # Dialogs
│       │   ├── __init__.py
│       │   ├── edit_dialog.py
│       │   ├── settings_dialog.py
│       │   └── about_dialog.py
│       │
│       └── 📁 adapters/            # Adapters
│           ├── __init__.py
│           └── qt_node_provider.py
│
├── 📁 api/                         # Python API (optional)
│   ├── __init__.py
│   └── mindmap_api.py             # Exposed API
│
├── 📁 tests/                       # Tests
│   ├── __init__.py
│   ├── unit/                      # Unit tests
│   │   ├── test_domain/
│   │   ├── test_application/
│   │   └── test_infrastructure/
│   ├── integration/               # Integration tests
│   └── e2e/                       # End-to-end tests
│
├── 📁 examples/                    # Examples
│   ├── basic_usage.py
│   ├── batch_processing.py
│   └── plugin_demo.py
│
├── 📁 docs/                        # Documentation
│   ├── INDEX.md
│   ├── PRODUCT_STRATEGY.md
│   ├── TECHNICAL_IMPLEMENTATION.md
│   ├── ARCHITECTURE.md            # This document
│   └── CONTRIBUTING.md
│
├── 📁 templates/                   # Templates
│   ├── default.json
│   ├── dark.json
│   └── light.json
│
├── 📁 plugins/                     # Third-party plugins (user installed)
│   └── community/
│
├── 📄 main.py                      # Entry point
├── 📄 default_layout_demo.py       # Demo file (preserved)
└── 📄 features_demo.py             # Feature demo (to be created)
```

---

## 🔗 Inter-Layer Communication Patterns

### Dependency Graph

```
┌─────────────┐
│   UI Layer   │
│ (Widgets)   │
└──────┬──────┘
       │ Calls
       ↓
┌─────────────┐
│ Application │
│ (Services)  │
└──────┬──────┘
       │ Uses
       ↓
┌─────────────┐
│  Domain     │
│ (Entities)  │
└──────┬──────┘
       │ Implements
       ↓
┌─────────────┐
│ Infrastruct │
│ (Repository)│
└─────────────┘
```

### Typical Call Chain

**Scenario: User double-clicks to edit a node**

```python
# 1. UI Layer: Capture double-click event
class NodeItem(QGraphicsRectItem):
    def mouseDoubleClickEvent(self, event):
        # Get application layer service
        service = self.app.node_service
        # Call application layer
        service.edit_node(self.node)

# 2. Application Layer: Orchestrate business process
class NodeService:
    def edit_node(self, node):
        # Create edit dialog
        dialog = EditDialog(node.text)
        if dialog.exec() == QDialog.Accepted:
            # Create command
            command = EditTextCommand(node, dialog.new_text)
            # Execute command (via undo stack)
            self.undo_stack.push(command)

# 3. Domain Layer: Execute business logic
class EditTextCommand(QUndoCommand):
    def redo(self):
        # Modify domain object
        self.node.text = self.new_text
        # Trigger domain event
        self.node.notify_changed()

# 4. Infrastructure Layer: Persistence
class MindMapRepository:
    def save(self, mindmap):
        # JSON serialization
        data = JSONSerializer.serialize(mindmap)
        # Write to file
        file.write(data)
```

---

## 🎯 Key Design Decisions

### 1. Why Choose Four-Layer Architecture?

**Advantages:**
- ✅ Clear responsibilities, easy to understand
- ✅ Decoupled layers, easy to test
- ✅ Independent domain layer, stable business logic
- ✅ Replaceable infrastructure (e.g., JSON→XML)

**Comparison with Other Architectures:**
- **MVC**: Suitable for GUI apps, but business logic easily mixes into Controller
- **MVVM**: Suitable for data binding, but Python Qt doesn't support it
- **Hexagonal**: More abstract, steep learning curve
- **Four-Layer**: Balances clarity and complexity

---

### 2. Domain-Driven Design (DDD) Trade-offs

**DDD Parts Adopted:**
- ✅ Entity - Node, MindMap
- ✅ Value Object - Position, Color
- ✅ Service - LayoutManager
- ✅ Repository - MindMapRepository

**DDD Parts Not Adopted:**
- ❌ Aggregate Root - Over-engineering
- ❌ Domain Event - Not needed initially
- ❌ CQRS - Too complex

**Reason:**
> Keep it simple, introduce as needed, avoid over-engineering

---

### 3. Command Pattern

**Why Need Command Pattern?**

1. **Undo/Redo Support** - Natural fit
2. **Operation History** - Easy debugging
3. **Batch Operations** - Combine multiple commands
4. **Macro Commands** - Record user operations

**Implementation Example:**

```python
# Command base class
class Command(QUndoCommand):
    def __init__(self, name=""):
        super().__init__(name)
    
    def undo(self):
        raise NotImplementedError
    
    def redo(self):
        raise NotImplementedError

# Concrete command
class AddNodeCommand(Command):
    def __init__(self, parent_node, new_node):
        super().__init__("Add Node")
        self.parent_node = parent_node
        self.new_node = new_node
    
    def redo(self):
        self.parent_node.add_child(self.new_node)
    
    def undo(self):
        self.parent_node.remove_child(self.new_node)

# Usage
undo_stack = QUndoStack()
undo_stack.push(AddNodeCommand(parent, child))
# User can Ctrl+Z to undo
```

---

### 4. Plugin System Design

**Plugin Architecture:**

```python
# Plugin interface (abstract base class)
class Plugin(ABC):
    @abstractmethod
    def on_load(self):
        pass
    
    @abstractmethod
    def get_menu_items(self):
        pass

# Plugin manager
class PluginManager:
    def __init__(self):
        self.plugins = []
    
    def register(self, plugin: Plugin):
        self.plugins.append(plugin)
        plugin.on_load()
    
    def load_all(self, plugin_dir):
        for module in discover_modules(plugin_dir):
            plugin_class = find_plugin_class(module)
            plugin = plugin_class(self.app)
            self.register(plugin)
```

**Plugin Example:**

```python
# LaTeX Plugin
class LaTeXPlugin(Plugin):
    def on_load(self):
        print("LaTeX plugin loaded")
    
    def get_menu_items(self):
        return [
            {"text": "Insert Formula", "callback": self.insert_latex}
        ]
    
    def insert_latex(self):
        formula = get_formula_from_user()
        render_latex(formula)
```

---

## 📊 Module Dependencies

### Dependency Matrix

| Module | domain | application | infrastructure | presentation |
|--------|--------|-------------|----------------|--------------|
| **domain** | - | ❌ | ❌ | ❌ |
| **application** | ✅ | - | ❌ | ❌ |
| **infrastructure** | ✅ | ✅ | - | ❌ |
| **presentation** | ❌ | ✅ | ❌ | - |

**Rules:**
- ✅ Can depend on
- ❌ Cannot depend on (would cause circular dependency)

---

### Physical Organization

**Option A: By Layer (Recommended)**
```
cogist/
├── domain/
├── application/
├── infrastructure/
└── presentation/
```
**Pros:** Clear hierarchy, follows architecture  
**Cons:** Cross-layer modifications require opening multiple directories

---

**Option B: By Feature**
```
cogist/
├── mindmap/        # Contains all mind map related code from all layers
│   ├── entity.py
│   ├── service.py
│   ├── repository.py
│   └── view.py
├── node/
│   ├── entity.py
│   ├── service.py
│   └── view.py
└── layout/
    ├── algorithm.py
    └── view.py
```
**Pros:** Feature cohesion, convenient modification  
**Cons:** Hierarchy less clear

---

**Recommendation: Option A (By Layer)**
- Follows DDD principles
- Clear layer boundaries
- Easy to understand and maintain

---

## 🔄 Architecture Evolution Roadmap

### Current State (v0.5+)
```
Complete four-layer architecture + API + SDK
```
**Goal:** Ecosystem building

---

## 📝 Summary

### Architecture Design Highlights

1. **Four-Layer Architecture** - Clear layer boundaries
2. **Domain-Driven** - Business logic as the core
3. **Command Pattern** - Supports undo/redo
4. **Plugin System** - Easy to extend
5. **Progressive Evolution** - From simple to complex

### Next Steps

1. ✅ Understand architecture design
2. ✅ Create basic directory structure
3. ✅ Implement domain layer entities
4. ✅ Implement application layer services
5. ✅ Refactor existing code to new architecture

---

**Last Updated**: 2026-05-03  
**Status**: Architecture design completed
