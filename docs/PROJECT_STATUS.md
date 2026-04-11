# Cogist Project Status

📊 **Current Version**: v0.1.0  
📅 **Last Updated**: 2026-04-11  
🎯 **Current Goal**: Initial Release - Core Mind Mapping Functionality

**📝 For recent updates, see**: [CHANGELOG.md](../CHANGELOG.md)

---

## [0.1.0] - 2026-04-11 - Initial Release 🎉

**Focus**: Cogist - A Beautiful Mind Mapping Tool with Intelligent Layout

### Core Features Implemented:

#### ✅ Architecture
- **Four-layer DDD Architecture** - Clean separation of concerns
  - Domain Layer: Entities, Value Objects, Layout Algorithms
  - Application Layer: Services, Commands
  - Infrastructure Layer: Repositories, Serializers
  - Presentation Layer: UI Components (PySide6/Qt)

#### ✅ Domain Layer
- **Node Entity** - UUID, parent-child relationships, tree traversal
- **Edge Entity** - Node connections with styling
- **Value Objects** - Position, Color with validation
- **DefaultLayout Algorithm** - Intelligent auto-layout with:
  - Center node layout with left/right branch balance
  - Node overlap prevention (recursive avoidance mechanism)
  - Depth-based sibling spacing (60/45/35px)
  - Subtree side locking during editing

#### ✅ Presentation Layer
- **NodeItem** - QGraphicsItem with:
  - Rounded rectangle with gradient
  - Depth-based font sizing (22/18/16/14pt)
  - Automatic text wrapping
  - Dynamic height calculation
- **EdgeItem** - Bezier curve with gradient width (10→2px)
- **MindMapView** - QGraphicsView with pan, zoom, keyboard navigation

#### ✅ Application Layer
- **Command Pattern** - Full undo/redo support
  - AddNodeCommand
  - DeleteNodeCommand
  - EditTextCommand
  - CommandHistory manager
- **Services** - High-level API for mind map operations

#### ✅ Infrastructure Layer
- **JSONSerializer** - Serialize/deserialize mind maps
- **MindMapRepository** - File persistence (.mwd format)

#### ✅ User Features
- **Inline Node Editing** - Press Space to edit nodes directly
- **Keyboard Shortcuts** - Full macOS/Windows support:
  - Tab: Add child node
  - Enter: Add sibling node
  - Delete/Backspace: Remove node
  - Space: Edit node text
  - ESC: Cancel editing
  - Cmd/Ctrl+Z: Undo
  - Cmd/Ctrl+Y: Redo
- **File Operations** - Save/Load mind maps in `.mwd` format
- **Focus Management** - Smart focus recovery after operations

### Technical Stack:
- Python 3.13+
- PySide6 6.8+ (Qt for Python)
- Built with uv package manager
- Ruff for linting and formatting
- Pyright for type checking

### Project Information:
- **Name**: Cogist (formerly MindWeave, renamed 2026-04-11)
- **License**: MIT License for project code + LGPL-3.0 compliance for PySide6 dependency
- **Architecture**: Domain-Driven Design (DDD) with 4 layers

---

## 📋 Roadmap

### v0.2.0 - Style System (Target: 2026-05) 🎨
**Focus**: Comprehensive style management and visual customization

- [ ] **MindMapStyle Configuration System**
  - Node style configuration (fonts, colors, padding, borders)
  - Layout configuration (spacing by depth)
  - Edge styling (colors, widths, curves)
- [ ] **Priority System**
  - 3-level priority scheme (Unimportant/Normal/Important)
  - Visual feedback for different priorities
  - Priority-based style overrides
- [ ] **Template System**
  - Pre-built templates (Default, Compact, Spacious, Professional)
  - Template switching UI
  - Custom template creation and saving
- [ ] **StylePanel UI**
  - Real-time style editing
  - Depth-based style customization
  - Live preview of changes
- [ ] **Node Priority UI**
  - Context menu for priority setting
  - Batch priority operations
  - Visual indicators for priority levels
- [ ] **Enhanced UI Foundation**
  - MainWindow with menu bar and toolbar
  - Style preferences persistence
  - Auto-save functionality

### v0.3.0 - Enhanced UX (Target: 2026-06) 🔍
**Focus**: Improved user experience and navigation

- [ ] **Search and Navigation**
  - Full-text search across mind maps
  - Navigation history
  - Quick jump to nodes
- [ ] **Subtree Management**
  - Collapse/expand subtrees
  - Subtree operations (move, copy, duplicate)
  - Outline view for large mind maps
- [ ] **Advanced Editing**
  - Multi-node selection and operations
  - Node relationships (cross-links)
  - Rich text support in nodes
- [ ] **Productivity Features**
  - Keyboard shortcuts customization
  - Quick templates for common structures
  - Recent files management

### v0.4.0 - Import/Export (Target: 2026-07) 📤
**Focus**: Data portability and integration

- [ ] **Export Services**
  - PNG/SVG image export
  - PDF export with customizable layouts
  - Markdown export (preserving hierarchy)
  - OPML export for compatibility
- [ ] **Import Services**
  - Markdown import (heading-based structure)
  - OPML import from other mind mapping tools
  - Freemind (.mm) import support
- [ ] **Clipboard Integration**
  - Copy nodes as text/Markdown
  - Paste from clipboard to create nodes
  - Screenshot export

### v0.5.0+ - Advanced Features (Target: 2026-08+) 🚀
**Focus**: Power user features and extensibility

- [ ] **Icon Library**
  - Built-in icon collection
  - Custom icon support
  - Emoji integration
- [ ] **Notes and Attachments**
  - Node notes (hidden detailed content)
  - File attachments
  - Hyperlinks support
- [ ] **Plugin System**
  - Python API for plugins
  - Plugin marketplace
  - Custom export/import plugins
- [ ] **Advanced Features**
  - Python scripting API for batch processing
  - Custom layout algorithms
  - Collaboration features (future)
  - Cloud sync (future)

---

## 📚 Documentation

- [Architecture Design](ARCHITECTURE.md)
- [Technical Implementation](TECHNICAL_IMPLEMENTATION.md)
- [Feature Summary](FEATURES_SUMMARY.md)
- [CHANGELOG](../CHANGELOG.md)

---

*Last updated: 2026-04-11*  
*Maintained by: Cogist Team*
