# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-04-25

### Added
- **Built-in default template system**: Implemented complete template loading with fallback strategy
  - Created `assets/templates/default.json` for built-in default template
  - Added `cogist/infrastructure/utils/resources/template_loader.py` for resource loading
  - Added `cogist/infrastructure/utils/resources/template_deserializer.py` for template deserialization
  - Three-level fallback: user directory → built-in assets → hardcoded default
- **Template save feature**: Save current style as reusable template
  - Added "Save as Template" menu item in File menu
  - Saves complete style data (node styles, colors, spacing, connectors) as single JSON file
  - Templates stored in platform-specific directory (`~/Library/Application Support/cogist/templates/` on macOS)
- **Configuration management**: Cross-platform config manager
  - Added `cogist/infrastructure/utils/config_manager.py` for unified config handling
  - Platform-aware paths: macOS (Application Support), Windows (AppData), Linux (XDG)
  - Automatic directory creation on first use

### Changed
- **Architecture compliance**: Moved resources to Infrastructure Layer
  - Resource loading code in `cogist/infrastructure/utils/resources/`
  - Data files separated to project-level `assets/` directory
  - Follows four-layer architecture design principles
- **Serialization improvements**: Enhanced template serialization
  - Unified serialize/deserialize functions for complete template data
  - Reuses CGS serializer logic for consistency
  - Supports per-depth configuration (spacing, connectors, text width)

### Technical Details
- All tests passing (96 unit tests)
- Code quality checks passed (ruff + pyright)
- No breaking changes, backward compatible

## [0.3.9] - 2026-04-25

### Refactored
- **Code simplification**: Reduced duplicate code in MindMapView through parameterization
  - Merged `_navigate_to_left_side_child` and `_navigate_to_right_side_child` into parameterized `_navigate_to_side_child(side: str)`
  - Simplified `_navigate_to_previous_sibling` and `_navigate_to_next_sibling` by extracting common logic to `_navigate_to_sibling(direction: str)`
  - Extracted `_is_node_on_right_side(node_id: str)` helper method to eliminate 4 repeated position comparisons
- **Improved maintainability**: Better adherence to DRY principle while maintaining backward compatibility
  - Wrapper methods preserved for API stability
  - No functional changes, pure refactoring
  - Code reduced by ~70 lines of duplication

## [0.3.8] - 2026-04-25

### Refactored
- **Architecture refactoring**: Major architectural improvements for better maintainability
  - Moved Connectors from `cogist/domain/connectors/` to `cogist/presentation/connectors/`
  - Moved Borders from `cogist/domain/borders/` to `cogist/presentation/borders/`
  - Extracted MindMapView from main.py to `cogist/presentation/views/mindmap_view.py`
  - Domain Layer is now completely pure (no Qt dependencies)
- **Code organization**: Improved code structure and separation of concerns
  - main.py reduced from 2712 lines to 597 lines (78% reduction)
  - MindMapView can now be reused in future MDI architecture
  - Better alignment with Qt official Diagram Scene example patterns

### Added
- **Architecture compliance checking**: Automated script for architecture validation
  - `scripts/check_architecture.sh` validates layer boundaries
  - Checks Domain Layer purity (no Qt dependencies)
  - Verifies correct file locations (connectors, borders, views)
  - Validates import statements across layers
- **AI assistant rules**: Enhanced architecture guidelines
  - Updated `.lingma/rules/architecture.md` with latest constraints
  - Added connectors/borders location requirements
  - Added MindMapView extraction requirement
  - Added layout algorithm interface specifications

### Technical Details
- All connector implementations (Bezier, Orthogonal, Straight, etc.) moved to Presentation Layer
- All border strategies (Container, Decorative Lines) moved to Presentation Layer
- MindMapView class (2105 lines) extracted to independent module
- Updated all import statements in edge_item.py, node_item.py, and main.py
- Architecture compliance: ✅ 100% PASS

## [0.3.7] - 2026-04-25

### Fixed
- **View focus management**: Fixed focus behavior after node deletion and undo/redo operations
  - Delete key now properly moves focus to sibling nodes (previous > next > parent)
  - Undo delete operation correctly restores focus to appropriate sibling node
  - Undo add operation properly focuses on deleted node's sibling
  - Redo add operation focuses on the restored node
- **Dynamic sceneRect management**: Implemented intelligent canvas sizing
  - Scene rect now dynamically adjusts based on content bounds + margin
  - Root node properly centered in viewport using `setAlignment(Qt.AlignCenter)`
  - Removed hardcoded canvas dimensions (1200x800), now uses viewport size
  - Scrollbars no longer appear in initial empty state

### Refactored
- **Extracted common focus methods**: Created reusable methods for focus management
  - `_calculate_next_focus_after_deletion()` - calculates focus priority
  - `_focus_on_node_after_deletion()` - handles post-deletion focus
  - `_focus_on_node_after_addition()` - handles post-addition focus
  - `_finalize_node_addition()` - common post-add logic
- **Moved focus methods to MindMapView**: Corrected class归属 for focus management methods
- **Added SceneRectManager**: Dedicated class for dynamic scene rectangle management

### Technical Details
- Focus calculation now happens before undo execution to avoid accessing deleted nodes
- All selection changes now clear previous selections to prevent multiple focus frames
- SceneRectManager ensures scene rect is always at least viewport size for proper centering

## [0.3.6] - 2026-04-24

### Fixed
- **Sibling node alignment after drag**: Fixed misalignment issue where sibling nodes' edges were not properly aligned after drag operations. Root cause was skipping size measurement when node depth changed, causing layout algorithm to use outdated width values.
- **Canvas background color update**: Fixed canvas background color not updating immediately when changed in style panel. Issue occurred because incremental UI updates skipped `_create_ui_items()` which was the only place setting scene background.

### Technical Details
- Added `_measure_actual_sizes(dragged_node)` call before layout refresh in drag operations to ensure correct dimensions after depth changes
- Added immediate `scene.setBackgroundBrush()` update in style panel's `_apply_node_styles_to_mindmap()` method
- Both fixes maintain compatibility with incremental update optimization while ensuring visual consistency

## [0.3.5] - 2026-04-24

### Fixed
- **Drag locking mechanism regression**: Restored position locking for dragged nodes that was accidentally removed during performance optimization
- **Double-flip bug**: Fixed `_flip_subtree_recursive` to only update `is_right_side` flag without mirroring position (prevents double-flipping)

### Performance
- **Incremental UI update**: Implemented position-only updates using `setPos()`, reducing UI refresh time by 90% (from 150-250ms to 10-20ms)
- **Single-node measurement**: Added `_measure_single_node()` for text editing scenarios, reducing measurement from O(n) to O(1)
- **Smart measurement skipping**: Skip unnecessary measurements for undo/redo/delete/drag operations where dimensions don't change
- **Overall layout refresh**: Total refresh time reduced by 40% (from 350-600ms to 220-440ms)

### Technical Details
- Restored `is_locked_position` flag management in drag operations and node creation
- Added incremental update fallback to full rebuild when new/deleted nodes detected
- Preserved all performance optimizations while fixing the regression
- Applied incremental modification principle to avoid future regressions

## [0.3.4] - 2026-04-24

### Fixed
- **Text editing dimension restore**: Node dimensions now correctly restore to original size when canceling edit with Esc key
- **Linter configuration**: Centralized Ruff ignore rules in pyproject.toml, removed 27 inline noqa comments for cleaner code

### Technical Details
- Added dimension caching mechanism in NodeItem.start_editing() for cancel support
- Restored node rect, triggered repaint, and updated edges in cancel_editing()
- Configured N802 and ARG002 rules globally to support Qt event methods and interface consistency

## [0.3.3] - 2026-04-24

### Fixed
- **Left-side subtree flip direction**: Fixed incorrect flip direction when dragging left-side node trees across the root
- **Dragged node position preservation**: Added `is_locked_position` flag to prevent layout rebalancing from moving dragged nodes back to the original side
- **Root node position detection bug**: Fixed drag-to-left-side failure caused by root node's `is_right_side` defaulting to `True`
- **Double-flip issue**: Disabled position mirroring in `_flip_subtree_recursive` to prevent duplicate position flips after drag release

### Technical Details
- Added `is_locked_position` property to Node entity for layout rebalancing control
- New top-level nodes are locked during creation to maintain right-side default behavior
- Dragged node's top-level ancestor is locked on mouse release with position update based on actual drag coordinates
- Locked nodes are excluded from `_rebalance_branches` candidate list
- Position lock flags are automatically cleared after each layout pass

## [0.3.2] - 2026-04-23

### Changed
- **Keyboard Navigation**: Implemented visual coordinate-based navigation for Up/Down arrow keys
- **Same-Side Constraint**: Navigation now strictly stays within the same side (left or right branch)
- **Same-Depth Constraint**: Navigation only moves between nodes at the same hierarchy level
- **Visual Adjacency**: Uses actual rendered Y coordinates to determine node ordering
- **Smart Cycling**: Automatically cycles to opposite end when reaching boundary

### Technical Details
- Added `_find_visually_adjacent_node()` method with strict filtering (same side + same depth)
- Simplified navigation logic from 30+ lines to 5 lines per direction
- Removed complex tree-structure based cousin detection algorithms
- Improved user experience with intuitive visual navigation

## [0.3.1] - 2026-04-23

### Fixed
- **Node Editing Size Inflation**: Fixed document margin issue in EditableTextItem causing size increase when entering edit mode
- **Style Data Access**: Replaced all `.get()` calls with direct dictionary access to ensure style data integrity
- **Edit Widget Separation**: Fixed edit widget positioning to align with node expansion direction during typing
- **Line Wrapping Consistency**: Unified wrapping strategy between display and edit modes (WrapAnywhere)

### Technical Details
- Added `setDocumentMargin(0)` to EditableTextItem initialization
- Updated style panel to use direct dictionary access for required fields
- Fixed coordinate calculation in on_width_changed callback

## [0.3.0] - 2026-04-23

### Added
- **Style System Data Structures**: Template, ColorScheme, SpacingConfig, RoleBasedStyle
- **Style Serialization**: JSON serialization/deserialization for all style components
- **Real-time Preview**: Live preview of style changes in Settings Panel
- **Advanced Settings Panel**: Dual-mode panel (Simple/Advanced) with layer-based editing
- **Node Shape System**: Support for basic shapes, SVG shapes, and custom shapes
- **Border System**: Container borders and decorative line borders
- **Connector System**: Multiple connector types (Bezier, Orthogonal, Rounded, Sharp-First Rounded)
- **Visual Previews**: Shape previews, connector previews, visual selectors
- **Activity Bar**: Modern activity bar for tool access
- **Shadow Effects**: Node shadow configuration
- **Spacing System**: Abstract spacing levels (Compact/Normal/Relaxed/Spacious)
- **Font Decorations**: Italic, Underline, Strikethrough support
- **Template System**: Role-based style templates with recommended layouts
- **Color Scheme System**: Node colors, border colors, text colors, branch color pools

### Changed
- **Architecture**: Complete DDD four-layer architecture implementation
- **File Format**: Updated to `.cgs` format (ZIP-compressed JSON container)
- **Style Panel**: Refactored from depth-based to role-based editing
- **Node Rendering**: Improved node size measurement and caching
- **Edge Rendering**: Enhanced gradient curve rendering with varying line widths
- **Layout System**: Decoupled layout algorithms from rendering
- **Documentation**: Reorganized documentation structure with Chinese localization

### Technical Details
- New modules: `extended_styles.py`, `style_resolver.py`, `cgs_serializer.py`
- New UI components: `style_panel_advanced.py`, `menu_button.py`, `collapsible_panel.py`
- New domain modules: `borders/`, `connectors/`, `templates/`
- Comprehensive unit tests for style serialization and extended styles

### Files Added
- `cogist/domain/styles/extended_styles.py` - Core style data structures
- `cogist/domain/styles/style_resolver.py` - Style resolution and serialization
- `cogist/domain/borders/` - Border system implementation
- `cogist/domain/connectors/` - Connector algorithms
- `cogist/presentation/dialogs/style_panel_advanced.py` - Advanced settings panel
- `cogist/presentation/dialogs/style_widgets/` - Reusable style widgets
- `cogist/infrastructure/io/cgs_serializer.py` - CGS file format support
- `tests/unit/test_extended_styles.py` - Style system tests
- `tests/unit/test_style_serialization.py` - Serialization tests

### Fixed
- Various UI styling issues
- Connector rendering improvements
- Panel spacing adjustments

## [0.2.0] - 2026-04-18

### Added
- **Layout System Refactoring**: Decoupled layout from rendering
- **Multiple Layout Support**: Infrastructure for multiple layout algorithms
- **Center-Radial Layout**: Balanced node distribution algorithm
- **Gradient Curves**: Professional curve rendering with varying line widths (10→2px)
- **Smart Edge Anchors**: Automatic edge anchor point selection
- **Performance Optimization**: Path caching for high-performance rendering
- **Branch Colors**: Auto-matching curve colors to branches
- **View Controls**: Zoom (+/-/0), pan (arrow keys)
- **Node Operations**: Add child (Tab), add sibling (Enter), delete (Delete)

### Technical Stack
- Python 3.13+
- PySide6 6.8+ (Qt for Python)
- QGraphicsView Framework
- uv package manager

## [0.1.0] - 2026-04-11

### Added
- **Initial Release**: Cogist - A Beautiful Mind Mapping Tool
- **Domain Layer**: Node entity with UUID, parent-child relationships, tree traversal
- **Architecture**: Four-layer DDD architecture (Domain/Application/Infrastructure/Presentation)
- **Layout Algorithm**: Intelligent auto-layout with depth-based spacing and styling
- **Node Editing**: Inline text editing with Space key
- **File Operations**: Save/Load mind maps in `.mwd` format (JSON-based)
- **Keyboard Shortcuts**: Full keyboard navigation (Cmd/Ctrl key mappings for macOS)
- **Undo/Redo**: Command pattern implementation for all operations
- **Documentation**: Complete documentation system

### Technical Stack
- Python 3.13+
- PySide6 6.8+ (Qt for Python)
- Built with uv package manager

### Project Information
- **Name**: Cogist (formerly MindWeave, renamed 2026-04-11)
- **License**: MIT License for project code + LGPL-3.0 compliance for PySide6 dependency

---

*Last updated: 2026-04-24 (v0.3.3)*
