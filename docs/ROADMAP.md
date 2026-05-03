# Cogist Project Roadmap

📋 **This document is an index of project development, listing core goals and main tasks for each version**

**Last Updated**: 2026-05-03  
**Current Version**: v0.5.1 (Stable)

---

## 🎯 Version Overview

| Version | Theme | Time | Status | Detailed Document |
|---------|-------|------|--------|-------------------|
| v0.1.0 | Basic Features | Completed | ✅ | [FEATURES.md](FEATURES.md) |
| v0.2.0 | Basic Architecture Implementation | 2026-05 | ✅ Completed | [VERSION_v0.2.0.md](VERSION_v0.2.0.md) |
| v0.3.0 | Style System Data Structure & Serialization | 2026-06 | ✅ Completed | [VERSION_v0.3.0.md](VERSION_v0.3.0.md) |
| v0.4.0 | Rainbow Branch Feature | 2026-07 | ✅ Completed | [VERSION_v0.4.0.md](VERSION_v0.4.0.md) |
| v0.5.0 | Complete Serialization & Template Management | 2026-08 | ✅ Completed | [VERSION_v0.5.0.md](VERSION_v0.5.0.md) |
| v0.5.1 | UI Improvements with SVG Icons | 2026-05 | ✅ Completed | - |
| v0.6.0 | Node Priority System | 2026-09 | ⏳ Planned | [VERSION_v0.6.0.md](VERSION_v0.6.0.md) |
| v0.7.0 | Multiple Layout Algorithms | 2026-10 | ⏳ Planned | [VERSION_v0.7.0.md](VERSION_v0.7.0.md) |
| v0.8.0 | Internationalization Support | 2026-11 | ⏳ Planned | [VERSION_v0.8.0.md](VERSION_v0.8.0.md) |
| v0.9.0 | Advanced Style Customization | 2026-12 | ⏳ Planned | - |
| v1.0.0 | Official Release | 2027-01 | ⏳ Planned | - |

---

## 📚 Related Documents

### Design Documents
- [LAYOUT_STYLE_ARCHITECTURE.md](LAYOUT_STYLE_ARCHITECTURE.md) - Mind map template architecture
- [COLOR_SCHEME_DATA_STRUCTURE.md](COLOR_SCHEME_DATA_STRUCTURE.md) - Color scheme data structure
- [TEMPLATE_DATA_STRUCTURE.md](TEMPLATE_DATA_STRUCTURE.md) - Template data structure
- [MINDMAP_STYLE_DATA_STRUCTURE.md](MINDMAP_STYLE_DATA_STRUCTURE.md) - Mind map style data structure

### Version Documents
- [VERSION_v0.2.0.md](VERSION_v0.2.0.md) - v0.2.0 detailed description
- [VERSION_v0.3.0.md](VERSION_v0.3.0.md) - v0.3.0 detailed description
- [VERSION_v0.3.1.md](VERSION_v0.3.1.md) - v0.3.1 detailed description
- [VERSION_v0.3.2.md](VERSION_v0.3.2.md) - v0.3.2 detailed description
- [VERSION_v0.4.0.md](VERSION_v0.4.0.md) - v0.4.0 detailed description
- [VERSION_v0.5.0.md](VERSION_v0.5.0.md) - v0.5.0 detailed description
- [VERSION_v0.6.0.md](VERSION_v0.6.0.md) - v0.6.0 detailed description
- [VERSION_v0.7.0.md](VERSION_v0.7.0.md) - v0.7.0 detailed description
- [VERSION_v0.8.0.md](VERSION_v0.8.0.md) - v0.8.0 detailed description

### Architecture Documents
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture overview
- [TECHNICAL_IMPLEMENTATION.md](TECHNICAL_IMPLEMENTATION.md) - Technical implementation details
- [NODE_DRAG_ALGORITHM_DESIGN.md](NODE_DRAG_ALGORITHM_DESIGN.md) - Node drag algorithm design
- [CGS_FILE_FORMAT.md](CGS_FILE_FORMAT.md) - CGS file format specification

### Product Documents
- [PRODUCT_STRATEGY.md](PRODUCT_STRATEGY.md) - Product strategy
- [DESIGN_PHILOSOPHY.md](DESIGN_PHILOSOPHY.md) - Design philosophy
- [FEATURES.md](FEATURES.md) - Feature list

### Other
- [todo(不要删掉！).md](todo\(不要删掉！\).md) - To-do list (development notes)
- [DOCUMENT_STRUCTURE.md](DOCUMENT_STRUCTURE.md) - Document structure explanation

---

**Maintainer**: Cogist Team  
**License**: MIT License

---

## 📝 Complete Work Checklist (Grouped by Topic)

### 🎨 Style & Theme System

#### v0.3.0 - Style System Data Structure & Serialization
- [x] **Style Serialization**
  - [x] Implement Template JSON serialization/deserialization
  - [x] Implement ColorScheme JSON serialization/deserialization
  - [x] Implement SpacingConfig serialization
  - [x] Save to `style` field in .cgs file
  - [x] Restore style configuration when loading from file
  - [x] Implement resolve_style() function call
  
- [x] **Real-time Preview Mechanism**
  - [x] Real-time node style updates (re-measure + apply to NodeItem)
  - [x] Real-time edge style updates
  - [x] Real-time canvas background color updates
  - [x] Apply new data structures (Template + ColorScheme)
  
- [x] **Bug Fixes**
  - [x] Hide main window scrollbars
  - [x] Auto-scroll to view center after deleting nodes
  - [x] Optimize node size measurement performance (add cache/dirty flag)
  - [x] Clean up main.py technical debt (duplicate CommandHistory, unused MindMapService)
  - [x] Check and fix undo/redo stack structure issues

#### v0.4.0 - Rainbow Branch Feature
- [x] **Rainbow Branch Data Structure**
  - [x] Complete branch_colors color pool in ColorScheme
  - [x] Implement use_rainbow_branches toggle
  - [x] Branch color allocation algorithm (assign colors by first-level branches)
  
- [x] **Rainbow Branch Rendering**
  - [x] Edge colors use branch color pool
  - [x] Only enable in tree layouts
  - [x] Consistent colors for all nodes in the same branch
  
- [x] **UI Controls**
  - [x] Add rainbow branch toggle in style panel
  - [x] Branch color pool editing UI
  - [x] Real-time preview effect
  
- [x] **Color Scheme Management**
  - [x] Preset color scheme library (including rainbow branch schemes)
  - [x] Color scheme save/load
  - [x] Color scheme import/export

#### v0.5.0 - Complete Serialization & Template Management
- [x] **Template Serialization Completion**
  - [x] Implement complete Template serialization
  - [x] Implement complete ColorScheme serialization
  - [x] Save to `style` field in .cgs file
  
- [x] **Template Management Features**
  - [x] Template save/load functionality
  - [x] Template preview
  - [x] Recommended layout selection
  - [x] Preset template library (3-5 sets)
  
- [x] **Style Panel UI Optimization**
  - [x] Template Selection control optimization
  - [x] Color Scheme Selection control optimization
  - [x] Add template preview functionality

#### v0.6.0 - Node Priority System
- [ ] **Priority Marking**
  - [ ] Node priority property (High, Medium, Low)
  - [ ] Priority style override
  - [ ] Visual markers (icons, borders)
  
- [ ] **Priority Filtering**
  - [ ] Show/hide nodes by priority
  - [ ] Priority statistics
  
- [ ] **Priority Layout Optimization**
  - [ ] Highlight high-priority nodes
  - [ ] Priority affects node ordering

#### v0.7.0 - Multiple Layout Algorithms
- [ ] **Layout Architecture Refactoring**
  - [ ] Create LayoutAlgorithm enum
  - [ ] Create LayoutConfig data structure
  - [ ] Layout algorithm registry
  - [ ] Decouple layout from styles
  
- [ ] **Tree Layout Family**
  - [ ] Radial layout
  - [ ] Top-Down layout
  - [ ] Left-Right layout
  - [ ] Seamless switching between these layouts
  
- [ ] **Layout Selector**
  - [ ] Add layout selection dropdown in main window
  - [ ] Recalculate positions when switching layouts
  - [ ] Keep styles unchanged
  
- [ ] **Layout Compatibility Check**
  - [ ] Implement can_switch_layout() function
  - [ ] Prompt user when incompatible
  - [ ] Record current layout to file
  
- [ ] **Semi-Structured Layouts**
  - [ ] Fishbone diagram layout (FishboneLayout)
  - [ ] Timeline layout (TimelineLayout)
  - [ ] Organizational chart (OrgChartLayout)

#### v0.9.0 - Advanced Style Customization
- [ ] **Role-Based Style System**
  - [ ] Introduce NodeRole enum
  - [ ] Modify MindMapStyle to support role_styles
  - [ ] Layout algorithms implement assign_node_roles()
  - [ ] Rendering engine uses roles to get styles
  
- [ ] **Level Style Override**
  - [ ] Add "Advanced" collapsible area in style panel
  - [ ] Support adding style overrides for specific levels
  - [ ] Override priority: override > theme > default
  
- [ ] **Complex Background Support**
  - [ ] Gradient backgrounds (linear/radial gradient)
  - [ ] Texture backgrounds (paper/canvas/wood, etc.)
  - [ ] Image backgrounds (support scaling, transparency)
  
- [ ] **Custom Shapes**
  - [ ] SVG shape support (fan shapes, scrolls, and other special shapes)
  - [ ] Custom shape parameter editor
  
- [ ] **Complex Border Effects**
  - [ ] SVG borders (decorative borders)
  - [ ] Image borders
  - [ ] Gradient borders
  
- [ ] **Advanced Edge Effects**
  - [ ] Gradient edges
  - [ ] Brush stroke effects (pressure sensitivity, texture)
  - [ ] Arrow decorations (start/end points, support SVG custom arrows)
  - [ ] Dashed line mode customization
  
- [ ] **Non-Tree Layouts (Optional)**
  - [ ] Network graph layout (Force-directed)
  - [ ] Free layout (manual dragging)

---

### 🔧 Other Features

#### v0.8.0 - Internationalization Support
- [ ] **Multi-language Framework**
  - [ ] i18n infrastructure
  - [ ] Translation file management
  - [ ] Language switching
  
- [ ] **UI Translation**
  - [ ] English interface
  - [ ] Chinese interface
  - [ ] Other languages (optional)

---

### 🚀 Release Preparation

#### v1.0.0 - Official Release
- [ ] **Stability**
  - [ ] Comprehensive testing
  - [ ] Bug fixes
  - [ ] Performance optimization
  
- [ ] **Documentation**
  - [ ] User manual
  - [ ] API documentation
  - [ ] Tutorial videos
  
- [ ] **Packaging & Distribution**
  - [ ] Windows installer
  - [ ] macOS DMG
  - [ ] Linux AppImage
  - [ ] PyPI package
