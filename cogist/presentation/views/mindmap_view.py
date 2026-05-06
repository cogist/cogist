"""MindMap View - QGraphicsView for mind map visualization.

This module contains the MindMapView class which handles:
- UI rendering of nodes and edges
- User interaction (mouse, keyboard events)
- Layout algorithm invocation
- Node selection and focus management
"""

from qtpy.QtCore import QEvent, QPointF, Qt, QTimer, Signal
from qtpy.QtGui import QPainter, QWheelEvent
from qtpy.QtWidgets import (
    QApplication,
    QFileDialog,
    QGraphicsScene,
    QGraphicsView,
    QMessageBox,
)

from cogist.application.commands.command_history import CommandHistory
from cogist.domain.entities.node import Node
from cogist.domain.layout.registry import layout_registry
from cogist.presentation.items.edge_item import EdgeItem
from cogist.presentation.items.node_item import NodeItem


class MindMapView(QGraphicsView):
    """Mind map view with Default layout and command pattern integration."""

    # Signal emitted when style_config is updated (e.g., after loading a file)
    style_config_changed = Signal()

    # Signal emitted when zoom level changes (for UI updates)
    zoom_changed = Signal(float)

    def __init__(self, style_config=None, mindmap_service=None):
        super().__init__()

        # Store Application Layer service
        from cogist.application.services import MindMapService

        self.mindmap_service: MindMapService = mindmap_service or MindMapService()

        # Store style configuration
        if style_config is None:
            # This should never happen in normal usage (main.py always passes style_config)
            raise ValueError(
                "MindMapView must be initialized with a style_config. "
                "Production code should always load templates from JSON files."
            )
        self.style_config = style_config

        # Create scene
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(Qt.white)

        # Initialize scene rect manager for dynamic canvas sizing
        from cogist.presentation.scene_manager import SceneRectManager

        self.scene_manager = SceneRectManager(self.scene, default_margin=100.0)
        self.scene_manager.set_view(self)

        # Set initial scene rect to viewport size (will be updated after layout)
        # This ensures scrollbars always work, which is required for panel compensation
        # Defer until viewport is ready in showEvent
        self._scene_initialized = False

        self.setScene(self.scene)

        # View settings
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

        # Hide scrollbars - we handle scrolling programmatically for panel compensation
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # CRITICAL: Match original demo settings to prevent visual artifacts
        self.setOptimizationFlag(QGraphicsView.DontSavePainterState)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        # CRITICAL: Disable automatic viewport anchoring during transformations
        # This prevents unwanted scrolling when scene content changes (e.g., adding nodes)
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setResizeAnchor(QGraphicsView.NoAnchor)

        # CRITICAL: Set alignment to prevent auto-centering behavior
        # Default is AlignCenter which causes view to recenter when scene changes
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        # Enable gesture support for trackpad pinch zoom
        self.grabGesture(Qt.PinchGesture)

        # Callback for zoom operations (set by MainWindow)
        self._zoom_callback = None

        # Store UI items
        self.node_items = {}
        self.edge_items = []

        # Command pattern
        self.command_history = CommandHistory()

        # Selection
        self.selected_node_id = None

        # Drag and drop state
        self._dragged_node_id: str | None = None
        self._drag_offset: QPointF | None = None
        self._current_potential_parent: Node | None = None
        self._subtree_initial_positions: dict[str, QPointF] = {}
        self._temp_drag_edge: object | None = None
        self._is_dragging_cross_side: bool = False
        self._subtree_is_mirrored: bool = (
            False  # Track if subtree is currently mirrored
        )

        # File tracking
        self.current_file_path: str | None = None

        # Enable focus for keyboard events
        self.setFocusPolicy(Qt.StrongFocus)

        # Defer sample data creation until viewport is ready (in showEvent)
        self.root_node: Node | None = None

        # Initialize Application Layer services
        from cogist.application.services import DragHandler
        from cogist.presentation.adapters import QtNodeProvider

        self.node_provider = QtNodeProvider(self.node_items)
        self.drag_handler: DragHandler | None = None

        # Install event filter for keyboard shortcuts
        self.installEventFilter(self)

    def _initialize_new_mindmap(self):
        """Reinitialize the mind map with default sample data (same as __init__)."""
        # Reset file tracking
        self.current_file_path = None

        # Reset selection
        self.selected_node_id = None

        # Clear scene and items
        self.scene.clear()
        self.node_items.clear()
        self.edge_items.clear()

        # CRITICAL: Reset Application Layer service state
        self.mindmap_service.command_history.clear()
        self.mindmap_service._command_count_at_save = 0
        # Note: is_modified will be reset by create_new_mindmap()

        # Create sample data (this will also select the root node)
        self.root_node = self._create_sample_data()

        # Re-initialize Application Layer services with new data
        from cogist.application.services import DragHandler
        from cogist.presentation.adapters import QtNodeProvider

        self.node_provider = QtNodeProvider(self.node_items)
        self.drag_handler = DragHandler(self.root_node, self.node_provider)

        # Reset view transformation (zoom, rotation, etc.)
        self.resetTransform()

    def _create_sample_data(self):
        """Create sample mind map data with only a root node."""
        # Use MindMapService to create new mind map (Application Layer)
        root = self.mindmap_service.create_new_mindmap(root_text="Central Topic")

        # Step 1: Create temporary UI items to measure actual rendered sizes
        # (Don't add to scene yet)
        self._measure_actual_sizes(root)

        # Step 2: Apply layout with actual sizes
        from cogist.domain.layout import DefaultLayoutConfig

        # Create layout config with style_config for dynamic spacing lookup
        layout_config = DefaultLayoutConfig(
            style_config=self.style_config,  # Pass style_config for role-based spacing
        )

        # Update service layout config
        self.mindmap_service.set_layout_config(layout_config)

        # Use LayoutRegistry to create layout instance (demonstrates proper architecture)
        layout = layout_registry.get_layout("default", layout_config)

        # Get viewport size for canvas dimensions
        viewport_size = self.viewport().size()
        canvas_width = float(viewport_size.width())
        canvas_height = float(viewport_size.height())

        layout.layout(root, canvas_width=canvas_width, canvas_height=canvas_height)

        # Create final UI items with correct sizes and positions
        self._create_ui_items(root)

        # Step 4: Update scene rect based on actual content + margin
        self.scene_manager.update_from_content()

        # Step 5: Center the view by setting alignment to center
        # This ensures content is centered in the viewport
        self.setAlignment(Qt.AlignCenter)

        # Select root node by default
        self.selected_node_id = root.id
        if root.id in self.node_items:
            self.node_items[root.id].setSelected(True)

        return root

    def _measure_single_node(self, node: Node):
        """Measure a single node's size without traversing children.

        Optimized for text editing scenarios where only one node changes.
        """
        # Get color pool from style config
        color_pool = self.style_config.color_pool if hasattr(self.style_config, 'color_pool') else []

        # Determine branch color
        branch_color = None
        if node.parent and node.parent.is_root:
            idx = node.parent.children.index(node) % len(color_pool) if color_pool else 0
            branch_color = color_pool[idx] if color_pool else node.color
        elif node.parent:
            # Inherit from parent's branch
            # For simplicity, use node's own color
            branch_color = node.color
        else:
            branch_color = node.color

        # Create temporary item to measure
        temp_item = NodeItem(
            color=branch_color,
            text=node.text,
            width=node.width,
            height=node.height,
            is_root=node.is_root,
            depth=node.depth,
            style_config=self.style_config,
            domain_node=node,  # Pass domain node reference
        )

        # Update node dimensions
        node.width = temp_item.node_width
        node.height = temp_item.node_height
        # CRITICAL: Sync border_width for layout algorithm to calculate visual bounds
        if hasattr(temp_item, 'template_style') and temp_item.template_style:
            node.border_width = getattr(temp_item.template_style, 'border_width', 0)
        else:
            node.border_width = 0

    def _measure_actual_sizes(self, root: Node):
        """
        Create temporary NodeItems to measure actual rendered sizes,
        then sync back to domain nodes.
        """
        # Get color pool from style config
        color_pool = self.style_config.color_pool if hasattr(self.style_config, 'color_pool') else []

        def measure_recursive(node: Node, branch_color: str | None = None):
            current_color = branch_color if branch_color else node.color

            # Create temporary item (not added to scene)
            temp_item = NodeItem(
                color=current_color,
                text=node.text,
                width=node.width,
                height=node.height,
                is_root=node.is_root,
                depth=node.depth,
                style_config=self.style_config,  # Pass style configuration
                domain_node=node,  # Pass domain node reference
                # DO NOT use use_domain_size here - we need to measure actual size
            )

            # Sync actual measured size back to domain node
            node.width = temp_item.node_width
            node.height = temp_item.node_height
            # CRITICAL: Sync border_width for layout algorithm to calculate visual bounds
            if hasattr(temp_item, 'template_style') and temp_item.template_style:
                node.border_width = getattr(temp_item.template_style, 'border_width', 0)
            else:
                node.border_width = 0

            # Recursively measure children
            for child in node.children:
                # Determine branch color for first-level children
                child_branch_color = None
                if node.is_root:
                    idx = node.children.index(child) % len(color_pool)
                    child_branch_color = color_pool[idx]
                else:
                    child_branch_color = branch_color

                measure_recursive(child, child_branch_color)

        measure_recursive(root)

    def _update_ui_positions_incremental(self):
        """Update UI item positions without recreating them (incremental update).

        This is much faster than clearing and recreating all items.
        Only updates positions of existing items, creates new ones if needed,
        and removes deleted ones.
        """
        # Step 1: Update or create node items
        created_nodes = set()
        for node in self._traverse_tree(self.root_node):
            if node.id in self.node_items:
                # Existing node - update position AND size
                item = self.node_items[node.id]
                item.setPos(node.position[0], node.position[1])

                # CRITICAL: Check if text content has changed (e.g., after undo/redo)
                if item.text_content != node.text:
                    # Text changed - need full rebuild to update text display
                    return False

                # CRITICAL: Sync domain node size to UI item
                # Domain node width/height was updated by _measure_actual_sizes
                if (
                    abs(item.node_width - node.width) > 0.1
                    or abs(item.node_height - node.height) > 0.1
                ):
                    item.node_width = node.width
                    item.node_height = node.height
                    item.setRect(
                        -node.width / 2, -node.height / 2, node.width, node.height
                    )

                    # Recalculate text position with new dimensions
                    item._update_node_geometry(item.text_content)

                created_nodes.add(node.id)
            else:
                # New node - need to create it
                # For simplicity in this phase, fall back to full rebuild if new nodes detected
                # TODO: Implement incremental node creation
                return False

        # Step 2: Check for deleted nodes
        deleted_nodes = set(self.node_items.keys()) - created_nodes
        if deleted_nodes:
            # For simplicity, fall back to full rebuild if nodes deleted
            return False

        # Step 3: Update all edges
        self._update_all_edges()

        # Step 4: Update side flags for decorative lines
        if self.root_node:
            root_item = self.node_items.get(self.root_node.id)
            if root_item:
                root_x = root_item.scenePos().x()
                for item in self.node_items.values():
                    item.is_right_side = item.scenePos().x() >= root_x

        return True

    def _traverse_tree(self, root: Node):
        """Traverse tree in breadth-first order."""
        queue = [root]
        while queue:
            node = queue.pop(0)
            yield node
            queue.extend(node.children)

    def _update_all_edges(self):
        """Update all edge curves after position changes."""
        for edge_item in self.edge_items:
            edge_item.update_curve()

    def _update_canvas_background(self):
        """Update canvas background color from style config."""
        if hasattr(self, "style_config") and self.style_config:
            from qtpy.QtGui import QBrush, QColor

            canvas_color = self.style_config.special_colors["canvas_bg"]
            self.scene.setBackgroundBrush(QBrush(QColor(canvas_color)))

    def _create_ui_items(self, root: Node):
        """Create UI items from node tree."""

        # Apply canvas background color from style config
        if hasattr(self, "style_config") and self.style_config:
            from qtpy.QtGui import QBrush, QColor

            canvas_color = self.style_config.special_colors["canvas_bg"]
            self.scene.setBackgroundBrush(QBrush(QColor(canvas_color)))

        def create_items_recursive(
            node: Node,
            parent_item: NodeItem | None = None,
            branch_color: str | None = None,
        ):
            # Get color pool for rainbow mode
            color_pool = self.style_config.color_pool if hasattr(self.style_config, 'color_pool') else []

            # Use branch color if assigned, otherwise use root color
            current_color = branch_color if branch_color else node.color

            # Create node item
            item = NodeItem(
                color=current_color,
                text=node.text,
                width=node.width,
                height=node.height,
                is_root=node.is_root,
                depth=node.depth,
                use_domain_size=True,  # Use domain layer's pre-measured size
                style_config=self.style_config,  # Pass style configuration
                domain_node=node,  # Pass domain node reference for parent/children access
            )
            item.setPos(*node.position)

            self.scene.addItem(item)
            self.node_items[node.id] = item

            # If has parent, link to parent and create edge immediately
            if parent_item:
                parent_item.add_child_item(item)
                # Use the branch color for the edge (same as parent and child nodes)
                edge_color = current_color
                edge = EdgeItem(
                    parent_item, item, color=edge_color, style_config=self.style_config
                )

                # Apply edge style from style_config (role-based configuration)
                if hasattr(self, "style_config") and self.style_config:
                    # Get TARGET node depth to determine which connector config to use
                    # Edge belongs to the child node (target), not the parent (source)
                    target_depth = item.depth if hasattr(item, "depth") else 0

                    # Get connector config from role-based style
                    from cogist.domain.styles.extended_styles import NodeRole

                    role_map = {
                        0: NodeRole.ROOT,
                        1: NodeRole.PRIMARY,
                        2: NodeRole.SECONDARY,
                    }
                    role = role_map.get(target_depth, NodeRole.TERTIARY)

                    # NEW: Use MindMapStyle.role_styles
                    if (hasattr(self.style_config, 'role_styles') and
                        role in self.style_config.role_styles):
                        role_style = self.style_config.role_styles[role]
                        color_pool = self.style_config.color_pool

                        # Get connector color from color pool index
                        color_index = role_style.connector_color_index if hasattr(role_style, 'connector_color_index') else 0

                        if color_pool and color_index < len(color_pool):
                            connector_color = color_pool[color_index]
                        else:
                            connector_color = "#FF666666"

                        edge_style_config = {
                            "connector_color": connector_color,
                            "line_width": role_style.line_width if hasattr(role_style, 'line_width') else 2.0,
                            "connector_style": role_style.connector_style if hasattr(role_style, 'connector_style') else "solid",
                            "connector_shape": role_style.connector_shape if hasattr(role_style, 'connector_shape') else "bezier",
                        }
                    else:
                        # Fallback to default values
                        edge_style_config = {
                            "connector_color": "#FF666666",
                            "line_width": 2.0,
                            "connector_style": "solid",
                            "connector_shape": "bezier",
                        }
                    edge.update_style(edge_style_config)

                self.scene.addItem(edge)
                parent_item.add_edge(edge)  # Add edge to parent
                item.add_edge(edge)  # Add edge to child (CRITICAL!)
                self.edge_items.append(edge)

            # Recursively create children with same branch color
            for child in node.children:
                # Pass branch color to children (first level children get unique colors)
                child_branch_color = (
                    branch_color
                    if branch_color
                    else (color_pool[len(root.children) - len(node.children)] if color_pool else None)
                    if node == root
                    else None
                )
                create_items_recursive(
                    child,
                    item,
                    child_branch_color
                    if branch_color
                    else (
                        (color_pool[node.children.index(child) % len(color_pool)] if color_pool else None)
                        if node == root
                        else None
                    ),
                )

        create_items_recursive(root)

        # Mark each node's side (left/right of root) for decorative line rendering
        # This is done after all items are created and positioned in the scene
        root_item = self.node_items.get(root.id)
        if root_item:
            root_x = root_item.scenePos().x()
            for item in self.node_items.values():
                item.is_right_side = item.scenePos().x() >= root_x

    def _get_main_window(self):
        """Get the main window reference using AppContext.

        Returns:
            MainWindow instance or None
        """
        from cogist.application.services import get_app_context

        return get_app_context().get_main_window()

    def focusOutEvent(self, event):
        """Handle focus lost event.

        When the view loses keyboard focus, clear the node selection state
        to ensure visual consistency with the focus state.
        """
        # Clear node selection when view loses focus
        self._deselect_node()
        super().focusOutEvent(event)

    def keyPressEvent(self, event):
        """Handle key press events.

        Only process keyboard events when the view has focus.
        If focus is on other widgets (like dialog controls), completely ignore
        the events to prevent QGraphicsView's default scrolling behavior.
        """
        # Check if this view actually has keyboard focus
        focused = QApplication.focusWidget()

        # Focus should be on either the view itself or its viewport
        if focused != self and focused != self.viewport():
            # Focus is elsewhere - completely ignore the event
            # Do NOT call super().keyPressEvent() to prevent default scrolling
            event.accept()  # Mark as handled but do nothing
            return

        # View has focus, use eventFilter to handle shortcuts
        # IMPORTANT: Do NOT call super().keyPressEvent() because it will
        # trigger QAbstractScrollArea's default arrow key scrolling behavior
        if not self.eventFilter(self, event):
            # If eventFilter doesn't handle it, let parent handle it
            super().keyPressEvent(event)

    def eventFilter(self, obj, event):
        """Handle keyboard shortcuts for editing commands.

        Note: This filter only receives events sent to the view itself.
        When focus is on other widgets (like dialog SpinBox), their events
        are handled by those widgets directly - this filter won't see them.
        """

        if event.type() == QEvent.KeyPress:
            key_event = event

            # Tab: Add child node (only when not editing)
            if key_event.key() == Qt.Key_Tab and self.selected_node_id:
                # Check if currently editing a node
                if self.selected_node_id in self.node_items:
                    node_item = self.node_items[self.selected_node_id]
                    if node_item.edit_widget is not None:
                        # Currently editing - let EditableTextItem handle it
                        # It will emit tab_pressed signal which NodeItem handles
                        return super().eventFilter(obj, event)

                # Not editing, just add child
                self._add_selected_child()
                key_event.accept()
                return True

            # Delete: Delete selected node (disabled when editing)
            if (
                key_event.key() in (Qt.Key_Delete, Qt.Key_Backspace)
                and self.selected_node_id
            ):
                # Check if currently editing a node
                if self.selected_node_id in self.node_items:
                    node_item = self.node_items[self.selected_node_id]
                    if node_item.edit_widget is not None:
                        # Let the edit widget handle Delete/Backspace for text editing
                        # Return super() to allow normal event propagation to focused widget
                        return super().eventFilter(obj, event)
                self._delete_selected_node()
                return True

            # Enter: Edit selected node text
            if key_event.key() == Qt.Key_Return and self.selected_node_id:
                # Check if currently editing a node
                if self.selected_node_id in self.node_items:
                    node_item = self.node_items[self.selected_node_id]
                    if node_item.edit_widget is not None:
                        # Currently editing, let the edit widget handle Enter for text input
                        # Return super() to allow normal event propagation to focused widget
                        return super().eventFilter(obj, event)
                self._edit_selected_node()
                return True

            # Space: Add sibling node
            if key_event.key() == Qt.Key_Space and self.selected_node_id:
                # Check if currently editing a node
                if self.selected_node_id in self.node_items:
                    node_item = self.node_items[self.selected_node_id]
                    if node_item.edit_widget is not None:
                        # Currently editing, let the edit widget handle Space for text input
                        # Return super() to allow normal event propagation to focused widget
                        return super().eventFilter(obj, event)
                self._add_sibling_node()
                key_event.accept()
                return True

            # Escape: Cancel editing (discard changes)
            if key_event.key() == Qt.Key_Escape:
                if self.selected_node_id and self.selected_node_id in self.node_items:
                    node_item = self.node_items[self.selected_node_id]
                    if node_item.edit_widget is not None:
                        # Cancel editing - discard changes
                        node_item.cancel_editing()
                        return True
                return False

            # Arrow keys: Navigate between nodes (only when not editing)
            if self.selected_node_id and self.selected_node_id in self.node_items:
                node_item = self.node_items[self.selected_node_id]
                # If currently editing, let the edit widget handle arrow keys for cursor movement
                if node_item.edit_widget is not None:
                    return super().eventFilter(obj, event)

                # Not editing - use arrow keys for node navigation
                # Navigation direction depends on which side of root the node is on
                if key_event.key() == Qt.Key_Up:
                    self._navigate_to_previous_sibling()
                    key_event.accept()
                    return True
                elif key_event.key() == Qt.Key_Down:
                    self._navigate_to_next_sibling()
                    key_event.accept()
                    return True
                elif key_event.key() == Qt.Key_Left:
                    # Left arrow behavior depends on node position
                    if node_item.is_right_side:
                        # Right branch: left arrow goes to parent (towards center)
                        self._navigate_to_parent()
                    else:
                        # Left branch: left arrow goes to first child (away from center)
                        self._navigate_to_first_child_inward_outward(
                            direction="outward"
                        )
                    key_event.accept()
                    return True
                elif key_event.key() == Qt.Key_Right:
                    # Right arrow behavior depends on node position
                    if node_item.is_right_side:
                        # Right branch: right arrow goes to first child (away from center)
                        self._navigate_to_first_child()
                    else:
                        # Left branch: right arrow goes to parent (towards center)
                        self._navigate_to_parent()
                    key_event.accept()
                    return True

        return super().eventFilter(obj, event)

    def mousePressEvent(self, event):
        """Handle mouse press to select nodes and start drag."""

        # Get clicked item
        pos = self.mapToScene(event.position().toPoint())
        item = self.scene.itemAt(pos, self.transform())

        # Find node item
        node_item = None
        while item:
            if isinstance(item, NodeItem):
                node_item = item
                break
            item = item.parentItem()

        # Update selection
        if node_item:
            self._select_node(node_item)

            # Check if this is a draggable node (non-root)
            current_node = self._find_node_by_id(self.root_node, self.selected_node_id)
            if current_node and not current_node.is_root:
                # Start drag operation
                self._dragged_node_id = self.selected_node_id
                # Calculate offset from node center to mouse position
                node_center = node_item.scenePos() + node_item.boundingRect().center()
                self._drag_offset = pos - node_center
                self._current_potential_parent = None
                self._is_dragging_cross_side = False
                self._drag_start_pos = pos  # Save drag start position
                self._old_parent_edge_hidden = (
                    False  # Track if old parent edge is hidden
                )

                # Save initial relative positions of entire subtree
                self._save_subtree_relative_positions(current_node)
        else:
            self._deselect_node()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Handle mouse move - drag node and detect potential parent."""
        if self._dragged_node_id and self._drag_offset:
            # Get current mouse position
            current_pos = self.mapToScene(event.position().toPoint())

            # FIX: Only start drag detection after moving beyond threshold
            drag_distance = (current_pos - self._drag_start_pos).manhattanLength()
            if drag_distance < 10.0:  # Minimum drag distance in pixels
                super().mouseMoveEvent(event)
                return

            # Move the dragged node
            dragged_item = self.node_items.get(self._dragged_node_id)
            if dragged_item:
                # Position node so that the offset point is under the mouse
                new_pos = current_pos - self._drag_offset
                dragged_item.setPos(new_pos)

                # Get root position for side detection
                root_item = None
                if self.root_node:
                    root_item = self.node_items.get(self.root_node.id)
                    root_x = root_item.scenePos().x() if root_item else 0.0
                else:
                    root_x = 0.0

                # Current side based on position (needed for cross-side detection)
                is_currently_right = self._is_node_on_right_side(self._dragged_node_id)

                # Apply subtree positions based on current side
                # CRITICAL: Same logic for both sides!
                # The saved offsets are from the original position.
                # We need to mirror when the current side doesn't match the original side.
                # - Original left (negative offset) + dragged to right: mirror
                # - Original right (positive offset) + dragged to left: mirror
                dragged_node = None
                potential_parent = None

                if self.root_node:
                    dragged_node = self._find_node_by_id(
                        self.root_node, self._dragged_node_id
                    )
                    if dragged_node and root_item:
                        # Check if we need to mirror based on offset signs
                        # Get first child offset to determine original side
                        offsets = [
                            off
                            for off in self._subtree_initial_positions.values()
                            if off.x() != 0
                        ]
                        if offsets:
                            # Original side: negative = left, positive = right
                            original_is_right = offsets[0].x() > 0
                            # Mirror if current side doesn't match original side
                            should_mirror = is_currently_right != original_is_right
                        else:
                            # No children, no mirroring needed
                            should_mirror = False

                        # Apply subtree positions
                        self._apply_subtree_positions(new_pos, should_mirror)

                        # Update is_right_side for entire subtree
                        self._update_subtree_is_right_side(
                            dragged_node, is_currently_right
                        )

                    # Detect potential parent using DragHandler (Application Layer)
                    from cogist.domain.value_objects.position import Position

                    if self.drag_handler:
                        potential_parent = self.drag_handler.detect_potential_parent(
                            dragged_node_id=self._dragged_node_id,
                            mouse_pos=Position(current_pos.x(), current_pos.y()),
                        )

                # FIX: Handle parent edge visibility based on potential_parent
                if potential_parent and dragged_node:
                    # Has a valid potential parent
                    if potential_parent != dragged_node.parent:
                        # Different parent - hide old edge, show temp edge
                        if not self._old_parent_edge_hidden:
                            self._hide_parent_edge(dragged_node)
                            self._old_parent_edge_hidden = True
                    else:
                        # Same parent - show old edge
                        if self._old_parent_edge_hidden:
                            self._restore_parent_edge(dragged_node)
                            self._old_parent_edge_hidden = False
                elif dragged_node and not self._old_parent_edge_hidden:
                    # No valid potential parent - hide old edge, don't draw temp edge
                    # This creates a "floating" visual state
                    self._hide_parent_edge(dragged_node)
                    self._old_parent_edge_hidden = True

                # Update temporary edge
                self._update_temp_drag_edge(dragged_node, potential_parent)

                # Detect cross-side drag by comparing center X positions
                if potential_parent:
                    parent_item = self.node_items.get(potential_parent.id)
                    if parent_item:
                        parent_center_x = (
                            parent_item.scenePos().x()
                            + parent_item.boundingRect().width() / 2
                        )

                        # Check if dragged node and potential parent are on different sides
                        parent_is_right = parent_center_x >= root_x
                        self._is_dragging_cross_side = (
                            is_currently_right != parent_is_right
                        )

                self._current_potential_parent = potential_parent

        super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Handle double-click to enter edit mode with cursor at click position."""
        # Get clicked position
        pos = self.mapToScene(event.position().toPoint())
        item = self.scene.itemAt(pos, self.transform())

        # Find node item
        node_item = None
        while item:
            if isinstance(item, NodeItem):
                node_item = item
                break
            item = item.parentItem()

        if node_item:
            # Select the node first
            self._select_node(node_item)

            # Calculate cursor position based on click position in text
            # Convert scene position to item-local position
            local_pos = node_item.mapFromScene(pos)

            # Get text item position and width
            text_item = node_item.text_item
            text_pos = text_item.pos()  # Position relative to node_item
            text_width = text_item.boundingRect().width()

            # Calculate X position relative to text start
            text_start_x = text_pos.x()
            click_x_in_text = local_pos.x() - text_start_x

            # Estimate cursor position based on character width
            text_content = node_item.text_content
            if text_content and text_width > 0:
                char_width = text_width / len(text_content)
                cursor_pos = int(click_x_in_text / char_width)
                cursor_pos = max(0, min(cursor_pos, len(text_content)))
            else:
                cursor_pos = 0

            # Start editing with cursor at click position
            self._edit_selected_node(cursor_position=cursor_pos)
        else:
            super().mouseDoubleClickEvent(event)

    def mouseReleaseEvent(self, event):
        """Handle mouse release - reparent node and refresh layout."""
        # Clear drag state FIRST to prevent further drag events
        dragged_id = self._dragged_node_id
        potential_parent = self._current_potential_parent
        is_cross_side = self._is_dragging_cross_side

        self._dragged_node_id = None
        self._drag_offset = None
        self._current_potential_parent = None
        self._is_dragging_cross_side = False
        self._old_parent_edge_hidden = False  # Reset edge hidden state

        if dragged_id:
            dragged_node = self._find_node_by_id(self.root_node, dragged_id)

            if dragged_node and potential_parent:
                new_parent = potential_parent

                if (
                    dragged_node != new_parent
                    and new_parent not in dragged_node.get_all_descendants()
                ):
                    # Save old parent and index BEFORE modifying
                    old_parent = dragged_node.parent
                    old_index = (
                        old_parent.children.index(dragged_node) if old_parent else 0
                    )

                    # Create and execute reparent command (Application Layer)
                    from cogist.application.commands.reparent_node_command import (
                        ReparentNodeCommand,
                    )

                    command = ReparentNodeCommand(
                        dragged_node=dragged_node,
                        old_parent=old_parent,
                        new_parent=new_parent,
                        old_index=old_index,
                        is_cross_side=is_cross_side,
                    )
                    command.execute()

                    # Push to command history for undo/redo
                    self.mindmap_service.node_service.command_history.push(command)

                    # Sort children by Y position to maintain visual order
                    new_parent.children.sort(
                        key=lambda child: (
                            self.node_items[child.id].scenePos().y()
                            if child.id in self.node_items
                            else 0
                        )
                    )

                    # If crossed sides, flip entire subtree's is_right_side
                    if is_cross_side:
                        # Get the side from the new parent's NodeItem
                        new_parent_item = self.node_items.get(new_parent.id)
                        if new_parent_item:
                            self._flip_subtree_side(
                                dragged_node, new_parent_item.is_right_side
                            )

                    # CRITICAL: Update the top-level node's position[0] to the new side
                    # This ensures the layout algorithm assigns it to the correct side
                    def get_top_level_ancestor(node):
                        """Get the direct child of root for this node."""
                        current = node
                        while current.parent and not current.parent.is_root:
                            current = current.parent
                        return current

                    top_level_node = get_top_level_ancestor(dragged_node)
                    if top_level_node:
                        # Use is_currently_right to determine the target side
                        is_currently_right = self._is_node_on_right_side(dragged_id)

                        # Update position[0] to a clear side indicator
                        # This is CRITICAL for the layout algorithm to correctly assign the node
                        if is_currently_right:
                            # R node: position far to the right
                            top_level_node.position = (800.0, top_level_node.position[1])
                        else:
                            # L node: position far to the left
                            top_level_node.position = (400.0, top_level_node.position[1])

                        # Mark as locked so layout won't move it during rebalancing
                    top_level_node.is_locked_position = True

                    # CRITICAL: Node relationships have changed, must rebuild edges completely
                    # Incremental update won't work because parent-child connections changed
                    # FIX: Re-measure dragged node and all its descendants since depth may have changed
                    self._measure_actual_sizes(dragged_node)

                    # Now refresh layout with skip_measurement=True since we just measured
                    # CRITICAL: Don't clear locked positions - we need them for this layout!
                    self._refresh_layout(
                        skip_measurement=True,
                        force_rebuild_edges=True,
                        clear_locked_positions=False
                    )
                else:
                    # Parent didn't change, but still need to refresh layout to snap node back
                    self._measure_actual_sizes(dragged_node)
                    self._refresh_layout(skip_measurement=True, force_rebuild_edges=False)
            elif dragged_node:
                # No potential parent detected, refresh layout to snap node back to original position
                self._measure_actual_sizes(dragged_node)
                self._refresh_layout(skip_measurement=True, force_rebuild_edges=False)

        # Clean up temp edge
        if self._temp_drag_edge:
            import contextlib

            with contextlib.suppress(RuntimeError):
                self.scene.removeItem(self._temp_drag_edge)
            self._temp_drag_edge = None

        # Restore edge to old parent
        if dragged_id:
            dragged_node = self._find_node_by_id(self.root_node, dragged_id)
            if dragged_node:
                self._restore_parent_edge(dragged_node)

        super().mouseReleaseEvent(event)

    def _select_node(self, node_item: NodeItem):
        """Select a node."""
        # Deselect previous
        if self.selected_node_id and self.selected_node_id in self.node_items:
            old_item = self.node_items[self.selected_node_id]
            old_item.setSelected(False)

        # Select new
        self.selected_node_id = None
        for node_id, item in self.node_items.items():
            if item == node_item:
                self.selected_node_id = node_id
                item.setSelected(True)
                break

    def _select_node_by_id(self, node_id: str):
        """Select a node by ID."""
        if node_id not in self.node_items:
            return

        # Deselect previous
        if self.selected_node_id and self.selected_node_id in self.node_items:
            self.node_items[self.selected_node_id].setSelected(False)

        # Select new
        self.selected_node_id = node_id
        self.node_items[node_id].setSelected(True)

    def _deselect_node(self):
        """Deselect all nodes."""
        if self.selected_node_id and self.selected_node_id in self.node_items:
            self.node_items[self.selected_node_id].setSelected(False)
        self.selected_node_id = None

    def clear_focus_and_selection(self):
        """Clear both keyboard focus and node selection.

        Call this when another widget (like a dialog) gains focus,
        to ensure there's only one active focus in the application.
        """
        # Clear keyboard focus from the view
        self.clearFocus()
        # Clear node selection state
        self._deselect_node()

    def _navigate_to_sibling(self, direction: str):
        """Navigate to previous/next sibling node.

        Args:
            direction: 'previous' for up arrow, 'next' for down arrow

        Behavior:
        - Find the visually closest node on the same side
        - Priority: sibling > cousin on same side > cycle within same side
        """
        if not self.selected_node_id or self.selected_node_id not in self.node_items:
            return

        current_node = self._find_node_by_id(self.root_node, self.selected_node_id)
        if not current_node or not current_node.parent:
            # No parent means this is root - can't navigate to sibling
            return

        # Map direction to arrow key
        arrow_direction = "up" if direction == "previous" else "down"

        # Use visual-based navigation: find closest node on same side
        target = self._find_visually_adjacent_node(direction=arrow_direction)
        if target:
            self._select_node_by_id(target.id)
            self._ensure_node_visible(target.id)

    def _navigate_to_previous_sibling(self):
        """Navigate to the previous sibling node (Up arrow)."""
        self._navigate_to_sibling("previous")

    def _navigate_to_next_sibling(self):
        """Navigate to the next sibling node (Down arrow)."""
        self._navigate_to_sibling("next")

    def _navigate_to_parent(self):
        """Navigate to the parent node (Left arrow).

        Special case for root node:
        - If current node is root, navigate to the first left-side child
        - Otherwise, navigate to parent node
        """
        if not self.selected_node_id or self.selected_node_id not in self.node_items:
            return

        current_node = self._find_node_by_id(self.root_node, self.selected_node_id)
        if not current_node:
            return

        # Special case: if on root node, navigate to first left-side child
        if current_node.is_root:
            self._navigate_to_left_side_child()
            return

        # Normal case: navigate to parent
        if not current_node.parent:
            # No parent means this is root - should have been handled above
            return

        self._select_node_by_id(current_node.parent.id)
        self._ensure_node_visible(current_node.parent.id)

    def _navigate_to_first_child(self):
        """Navigate to the first child node (Right arrow for right branch).

        Special case for root node:
        - If current node is root, navigate to the first right-side child
        - Otherwise, navigate to first child
        """
        if not self.selected_node_id or self.selected_node_id not in self.node_items:
            return

        current_node = self._find_node_by_id(self.root_node, self.selected_node_id)
        if not current_node:
            return

        # Special case: if on root node, navigate to first right-side child
        if current_node.is_root:
            self._navigate_to_right_side_child()
            return

        # Normal case: navigate to first child
        if not current_node.children:
            # No children - can't navigate
            return

        first_child = current_node.children[0]
        self._select_node_by_id(first_child.id)
        self._ensure_node_visible(first_child.id)

    def _navigate_to_first_child_inward_outward(self, direction: str):
        """Navigate to first child based on inward/outward direction.

        For left branch nodes:
        - "outward" means navigating away from center (to the left, to children)
        - "inward" means navigating towards center (to the right, to parent)

        Args:
            direction: "inward" (towards root) or "outward" (away from root)
        """
        if not self.selected_node_id or self.selected_node_id not in self.node_items:
            return

        current_node = self._find_node_by_id(self.root_node, self.selected_node_id)
        if not current_node:
            return

        # Special case: if on root node
        if current_node.is_root:
            if direction == "outward":
                # For root, outward on left side means left-side children
                self._navigate_to_left_side_child()
            else:
                # For root, inward doesn't make sense (already at center)
                pass
            return

        # Normal case: navigate to first child (outward from parent)
        if direction == "outward" and current_node.children:
            first_child = current_node.children[0]
            self._select_node_by_id(first_child.id)
            self._ensure_node_visible(first_child.id)

    def _navigate_to_side_child(self, side: str):
        """Navigate from root to the first child on specified side.

        Args:
            side: 'left' for left-side children (x < root_x),
                  'right' for right-side children (x >= root_x)
        """
        if not self.root_node or not self.root_node.children:
            return

        root_item = self.node_items.get(self.root_node.id)
        if not root_item:
            return

        root_x = root_item.scenePos().x()

        # Find children on the specified side
        target_children = []
        for child in self.root_node.children:
            if child.id in self.node_items:
                child_item = self.node_items[child.id]
                if side == "left":
                    if child_item.scenePos().x() < root_x:
                        target_children.append(child)
                else:  # right
                    if child_item.scenePos().x() >= root_x:
                        target_children.append(child)

        if target_children:
            # Select the first child on that side (topmost one)
            self._select_node_by_id(target_children[0].id)
            self._ensure_node_visible(target_children[0].id)

    def _navigate_to_left_side_child(self):
        """Navigate from root to the first left-side child."""
        self._navigate_to_side_child("left")

    def _navigate_to_right_side_child(self):
        """Navigate from root to the first right-side child."""
        self._navigate_to_side_child("right")

    def _cycle_to_last_sibling_on_same_side(self, direction: str):
        """Cycle to the last sibling on the same side (for top-level nodes).

        Args:
            direction: "up" or "down"
        """
        if not self.selected_node_id or self.selected_node_id not in self.node_items:
            return

        current_node = self._find_node_by_id(self.root_node, self.selected_node_id)
        if (
            not current_node
            or not current_node.parent
            or not current_node.parent.is_root
            or not self.root_node
        ):
            return

        # Get all siblings on the same side
        root_item = self.node_items.get(self.root_node.id)
        if not root_item:
            return

        current_item = self.node_items[self.selected_node_id]
        is_right_side = current_item.is_right_side

        # Filter siblings on the same side
        same_side_siblings = []
        for sibling in current_node.parent.children:
            if sibling.id in self.node_items:
                sibling_item = self.node_items[sibling.id]
                if sibling_item.is_right_side == is_right_side:
                    same_side_siblings.append(sibling)

        if len(same_side_siblings) > 1:
            # Cycle to the last/first on same side
            if direction == "up":
                # Go to last sibling on same side
                target = same_side_siblings[-1]
            else:
                # Go to first sibling on same side
                target = same_side_siblings[0]
            self._select_node_by_id(target.id)
            self._ensure_node_visible(target.id)

    def _cycle_to_first_sibling_on_same_side(self, direction: str):
        """Cycle to the first sibling on the same side (for top-level nodes).

        Args:
            direction: "up" or "down"
        """
        # This is essentially the same as _cycle_to_last_sibling_on_same_side
        # but called from the opposite direction
        self._cycle_to_last_sibling_on_same_side(direction)

    def _find_visually_adjacent_node(self, direction: str):
        """Find the visually adjacent node on the same side and same depth.

        This method finds the closest node above/below the current node
        by comparing actual scene Y coordinates, ensuring visual consistency.
        Only considers nodes at the same depth level (same hierarchy level).

        Args:
            direction: "up" (find node above) or "down" (find node below)

        Returns:
            The target Node object, or None if no suitable node found
        """
        if not self.selected_node_id or self.selected_node_id not in self.node_items:
            return None

        current_node = self._find_node_by_id(self.root_node, self.selected_node_id)
        if not current_node:
            return None

        current_item = self.node_items[self.selected_node_id]
        current_y = current_item.scenePos().y()
        is_right_side = current_item.is_right_side
        current_depth = current_node.depth

        # Collect all candidate nodes on the same side AND same depth (excluding current node)
        candidates = []
        for node_id, item in self.node_items.items():
            if node_id == self.selected_node_id:
                continue
            if item.is_right_side != is_right_side:
                continue  # Skip nodes on different side

            # Find the corresponding domain node
            domain_node = self._find_node_by_id(self.root_node, node_id)
            if not domain_node:
                continue

            # CRITICAL: Only consider nodes at the same depth level
            if domain_node.depth != current_depth:
                continue

            candidates.append((domain_node, item.scenePos().y()))

        if not candidates:
            return None

        # Filter candidates based on direction
        if direction == "up":
            # Find nodes with Y < current_y (above current node)
            above_nodes = [(node, y) for node, y in candidates if y < current_y]
            if not above_nodes:
                # No nodes above, cycle to the bottom-most node on same side & depth
                below_nodes = [(node, y) for node, y in candidates if y > current_y]
                if below_nodes:
                    # Get the one with maximum Y (bottom-most)
                    return max(below_nodes, key=lambda x: x[1])[0]
                return None
            # Get the one with maximum Y (closest above)
            return max(above_nodes, key=lambda x: x[1])[0]
        else:
            # Find nodes with Y > current_y (below current node)
            below_nodes = [(node, y) for node, y in candidates if y > current_y]
            if not below_nodes:
                # No nodes below, cycle to the top-most node on same side & depth
                above_nodes = [(node, y) for node, y in candidates if y < current_y]
                if above_nodes:
                    # Get the one with minimum Y (top-most)
                    return min(above_nodes, key=lambda x: x[1])[0]
                return None
            # Get the one with minimum Y (closest below)
            return min(below_nodes, key=lambda x: x[1])[0]

    def _navigate_to_previous_group_last_node(self, direction: str):
        """Navigate to the last node in the previous group on the same side.

        When a node is the first child and has no previous sibling,
        navigate to the last child of the previous uncle/aunt on the same side.

        Args:
            direction: "up" (to previous uncle's last child) or "down" (to next uncle's first child)
        """
        if not self.selected_node_id or self.selected_node_id not in self.node_items:
            return

        current_node = self._find_node_by_id(self.root_node, self.selected_node_id)
        if not current_node or not current_node.parent or current_node.parent.is_root:
            return

        parent = current_node.parent
        grandparent = parent.parent
        if not grandparent:
            return

        # Get all siblings of parent (uncles/aunts)
        uncles = grandparent.children
        parent_index = uncles.index(parent)

        # Find the target uncle/aunt based on direction
        if direction == "up":
            # Look for previous uncle/aunt on the same side
            for i in range(parent_index - 1, -1, -1):
                uncle = uncles[i]
                if uncle.children:
                    # Check if this uncle's children are on the same side
                    first_child = uncle.children[0]
                    if first_child.id in self.node_items and self._is_on_same_side(
                        current_node, first_child
                    ):
                        # Navigate to the last child of this uncle
                        target = uncle.children[-1]
                        self._select_node_by_id(target.id)
                        self._ensure_node_visible(target.id)
                        return
        else:
            # Look for next uncle/aunt on the same side
            for i in range(parent_index + 1, len(uncles)):
                uncle = uncles[i]
                if uncle.children:
                    # Check if this uncle's children are on the same side
                    first_child = uncle.children[0]
                    if first_child.id in self.node_items and self._is_on_same_side(
                        current_node, first_child
                    ):
                        # Navigate to the first child of this uncle
                        target = uncle.children[0]
                        self._select_node_by_id(target.id)
                        self._ensure_node_visible(target.id)
                        return

        # If no cousin found on same side, cycle within current siblings
        siblings = parent.children
        if len(siblings) > 1:
            target = siblings[-1] if direction == "up" else siblings[0]
            self._select_node_by_id(target.id)
            self._ensure_node_visible(target.id)

    def _navigate_to_cousin(self, direction: str) -> bool:
        """Navigate to cousin node (parent's sibling's child).

        Args:
            direction: "up" (to previous uncle's last child) or "down" (to next uncle's first child)

        Returns:
            True if successfully navigated to a cousin, False otherwise
        """
        if not self.selected_node_id or self.selected_node_id not in self.node_items:
            return False

        current_node = self._find_node_by_id(self.root_node, self.selected_node_id)
        if not current_node or not current_node.parent or current_node.parent.is_root:
            return False

        parent = current_node.parent
        grandparents = parent.parent
        if not grandparents:
            return False

        # Get parent's siblings (uncles/aunts)
        uncles = grandparents.children
        parent_index = uncles.index(parent)

        if direction == "up":
            # Navigate to previous uncle's last child
            if parent_index > 0:
                previous_uncle = uncles[parent_index - 1]
                if previous_uncle.children and self._is_on_same_side(
                    current_node, previous_uncle.children[-1]
                ):
                    target = previous_uncle.children[-1]
                    self._select_node_by_id(target.id)
                    self._ensure_node_visible(target.id)
                    return True
        else:
            # Navigate to next uncle's first child
            if parent_index < len(uncles) - 1:
                next_uncle = uncles[parent_index + 1]
                if next_uncle.children and self._is_on_same_side(
                    current_node, next_uncle.children[0]
                ):
                    target = next_uncle.children[0]
                    self._select_node_by_id(target.id)
                    self._ensure_node_visible(target.id)
                    return True

        return False

    def _is_on_same_side(self, node1, node2) -> bool:
        """Check if two nodes are on the same side of root.

        Args:
            node1: First node
            node2: Second node

        Returns:
            True if both nodes are on the same side (both left or both right)
        """
        if node1.id not in self.node_items or node2.id not in self.node_items:
            return False

        item1 = self.node_items[node1.id]
        item2 = self.node_items[node2.id]

        return item1.is_right_side == item2.is_right_side

    def _is_node_on_right_side(self, node_id: str) -> bool:
        """Check if a node is on the right side of root.

        Args:
            node_id: The ID of the node to check

        Returns:
            True if node's x position >= root's x position, False otherwise
        """
        item = self.node_items.get(node_id)
        if not item:
            return True  # Default to right if not found

        if not self.root_node:
            return True

        root_item = self.node_items.get(self.root_node.id)
        if not root_item:
            return True

        return item.scenePos().x() >= root_item.scenePos().x()

    def _generate_node_name(self, parent_node: Node) -> str:
        """Generate unique node name based on hierarchy.

        Naming convention:
        - Root's children: a, b, c, d...
        - a's children: a1, a2, a3... (no underscore for 2nd level)
        - a1's children: a1_1, a1_2... (underscore for 3rd level+)
        """
        parent_name = parent_node.text
        child_index = len(parent_node.children)

        # If parent is root, use letter naming
        if parent_node.is_root:
            return chr(ord("a") + child_index)

        # If parent name is single letter (like 'a'), use letter + number (like 'a1')
        if len(parent_name) == 1 and parent_name.isalpha():
            return f"{parent_name}{child_index + 1}"

        # For deeper levels, use parent_name + underscore + number (like 'a1_1')
        return f"{parent_name}_{child_index + 1}"

    def _add_selected_child(self):
        """Add a child node to the selected node."""
        if not self.selected_node_id:
            return

        # Find parent node in tree
        parent_node = self._find_node_by_id(self.root_node, self.selected_node_id)
        if not parent_node:
            return

        # Generate unique name
        new_name = self._generate_node_name(parent_node)

        # Use MindMapService to add child (Application Layer)
        parent_node, new_node = self.mindmap_service.add_child_node_by_id(
            parent_id=self.selected_node_id, text=new_name
        )

        if new_node is None:
            return

        # Common post-add logic
        self._finalize_node_addition(new_node)

    def _add_sibling_node(self):
        """Add a sibling node to the selected node."""
        if not self.selected_node_id or self.selected_node_id == "root":
            return  # Can't add sibling to root

        # Find parent and current node
        parent_node, current_node = self._find_parent_and_node(
            self.root_node, self.selected_node_id
        )

        if not parent_node or not current_node:
            return

        # Generate unique name (same as child naming)
        new_name = self._generate_node_name(parent_node)

        # Use MindMapService to add sibling (Application Layer)
        parent_node, new_node = self.mindmap_service.add_sibling_node(
            node_id=self.selected_node_id, text=new_name
        )

        if new_node is None or parent_node is None:
            return

        # FIX: Insert new node right after current node in children list
        # Find the index of current node
        current_index = parent_node.children.index(current_node)

        # Remove new_node from end (it was appended by add_child)
        parent_node.children.remove(new_node)

        # Insert it right after current node
        parent_node.children.insert(current_index + 1, new_node)

        # Common post-add logic
        self._finalize_node_addition(new_node)

    def _finalize_node_addition(self, new_node):
        """Common logic after adding a node.

        Args:
            new_node: The newly added domain node
        """
        # Mark new node as locked for rebalancing
        new_node.is_locked_position = True

        # OPTIMIZATION: Only measure the new node, not the entire tree
        self._measure_single_node(new_node)

        # Refresh UI with skip_measurement=True since we just measured
        self._refresh_layout(skip_measurement=True)

        # Select the new node
        new_node_id = new_node.id
        self._select_node_by_id(new_node_id)

        # Ensure the new node is visible in the viewport (with margin)
        # Only scrolls if the node is outside the current view
        QTimer.singleShot(0, lambda: self._ensure_node_visible(new_node_id))

    def _calculate_next_focus_after_deletion(self, node_to_delete, parent_node):
        """Calculate which node should receive focus after deletion.

        Priority: previous sibling > next sibling > parent

        Args:
            node_to_delete: The node being deleted (domain object)
            parent_node: The parent of the deleted node

        Returns:
            The ID of the node that should receive focus
        """
        next_selected_id = parent_node.id  # Default to parent

        # Find the index of the node to delete in parent's children
        for i, child in enumerate(parent_node.children):
            if child.id == node_to_delete.id:
                # Priority 1: Previous sibling
                if i > 0:
                    next_selected_id = parent_node.children[i - 1].id
                # Priority 2: Next sibling
                elif i < len(parent_node.children) - 1:
                    next_selected_id = parent_node.children[i + 1].id
                # Priority 3: Parent (already set as default)
                break

        return next_selected_id

    def _focus_on_node_after_deletion(self, node_to_delete, parent_node):
        """Set focus after deleting a node.

        Focus priority: previous sibling > next sibling > parent

        Args:
            node_to_delete: The node being deleted (domain object)
            parent_node: The parent of the deleted node
        """
        if not parent_node:
            return

        # Find which sibling to focus on
        next_selected_id = self._calculate_next_focus_after_deletion(
            node_to_delete, parent_node
        )

        # Clear all selections first
        for item in self.node_items.values():
            item.setSelected(False)

        # Set new selection
        if next_selected_id in self.node_items:
            self.selected_node_id = next_selected_id
            selected_item = self.node_items[next_selected_id]
            selected_item.setSelected(True)
            # Only scroll if node is not fully visible
            margin_px = 50
            self.ensureVisible(selected_item, margin_px, margin_px)

    def _focus_on_node_after_addition(self, added_node_id):
        """Set focus after adding a node.

        Args:
            added_node_id: The ID of the newly added node
        """
        if added_node_id not in self.node_items:
            return

        # Clear all selections first
        for item in self.node_items.values():
            item.setSelected(False)

        # Set new selection
        self.selected_node_id = added_node_id
        added_item = self.node_items[added_node_id]
        added_item.setSelected(True)
        # Only scroll if node is not fully visible
        margin_px = 50
        self.ensureVisible(added_item, margin_px, margin_px)

    def _delete_selected_node(self):
        """Delete the selected node."""
        if not self.selected_node_id or self.selected_node_id == "root":
            return  # Can't delete root

        # Find parent and node
        parent_node, node_to_delete = self._find_parent_and_node(
            self.root_node, self.selected_node_id
        )

        if not parent_node or not node_to_delete:
            return

        # Determine which node to select after deletion using common logic
        next_selected_id = self._calculate_next_focus_after_deletion(
            node_to_delete, parent_node
        )

        # Use MindMapService to delete node (Application Layer)
        success = self.mindmap_service.delete_node_by_id(self.selected_node_id)
        if not success:
            return

        # Select the determined node after deletion
        self.selected_node_id = next_selected_id

        # OPTIMIZATION: Deletion doesn't change node dimensions, skip measurement
        # Refresh UI
        self._refresh_layout(skip_measurement=True)

        # Scroll to the newly selected node to ensure it's visible
        if self.selected_node_id and self.selected_node_id in self.node_items:
            # Clear all selections first to avoid multiple focus frames
            for item in self.node_items.values():
                item.setSelected(False)

            selected_item = self.node_items[self.selected_node_id]
            selected_item.setSelected(True)
            # Only scroll if node is not fully visible
            margin_px = 50
            self.ensureVisible(selected_item, margin_px, margin_px)

    def _edit_selected_node(self, cursor_position: int = -1):
        """Edit the selected node text with inline editing.

        Args:
            cursor_position: Cursor position in text (-1 for select all)
        """
        if not self.selected_node_id or self.selected_node_id not in self.node_items:
            return

        node_item = self.node_items[self.selected_node_id]
        # CRITICAL FIX: Capture the node ID at edit start time
        # This prevents issues when mouse click changes selection during editing
        editing_node_id = self.selected_node_id

        # Start inline editing
        def on_text_changed(new_text):
            # Use MindMapService to edit node text (Application Layer)
            success = self.mindmap_service.edit_node_text_by_id(
                node_id=editing_node_id, new_text=new_text
            )

            if success:
                # Find the node for measurement
                node = self._find_node_by_id(self.root_node, editing_node_id)
                if node:
                    # OPTIMIZATION: Only measure the edited node, not the entire tree
                    # This reduces layout time from O(n) to O(1) for text edits
                    self._measure_single_node(node)

                    # Re-layout with skip_measurement=True since we just measured
                    self._refresh_layout(skip_measurement=True)

                    # Check if we need to add a child node after editing (e.g., Tab was pressed)
                    if (
                        hasattr(self, "_add_child_after_edit")
                        and self._add_child_after_edit
                    ):
                        self._add_child_after_edit = False
                        self._add_selected_child()

            # CRITICAL: Re-enable Tab and Return shortcuts after editing completes
            main_window = self._get_main_window()
            if main_window:
                if hasattr(main_window, "add_child_action"):
                    main_window.add_child_action.setEnabled(True)
                if hasattr(main_window, "add_sibling_action"):
                    main_window.add_sibling_action.setEnabled(True)

        node_item.start_editing(
            on_text_changed, cursor_position=cursor_position, mindmap_view=self
        )

        # CRITICAL: Disable Tab and Return shortcuts during editing
        main_window = self._get_main_window()
        if main_window:
            if hasattr(main_window, "add_child_action"):
                main_window.add_child_action.setEnabled(False)
            if hasattr(main_window, "add_sibling_action"):
                main_window.add_sibling_action.setEnabled(False)

    def _find_node_by_id(self, root: Node, target_id: str) -> Node | None:
        """Find a node by ID in the tree."""
        if root.id == target_id:
            return root

        for child in root.children:
            found = self._find_node_by_id(child, target_id)
            if found:
                return found

        return None

    def _find_parent_and_node(self, root: Node, target_id: str) -> tuple:
        """Find parent node and target node by ID."""
        for child in root.children:
            if child.id == target_id:
                return root, child

            parent, node = self._find_parent_and_node(child, target_id)
            if node:
                return parent, node

        return None, None

    def _refresh_layout(
        self,
        skip_measurement: bool = False,
        saved_selection_id: str = None,
        parent_id: str = None,
        force_rebuild_edges: bool = False,
        clear_locked_positions: bool = True,
        update_scene_rect: bool = True,
    ):
        """Refresh the entire layout after changes.

        Args:
            skip_measurement: If True, skip _measure_actual_sizes because
                              domain sizes are already correct (e.g., after editing).
            saved_selection_id: Optional node ID to restore selection after refresh
            parent_id: Optional parent node ID for selection restoration
            force_rebuild_edges: If True, force complete edge rebuild instead of
                                incremental update (needed when parent-child relationships change)
            clear_locked_positions: If True, clear is_locked_position flags after layout.
                                   Set to False for undo/redo of text edits.
        """
        # Save selected node ID before clearing (if not provided)
        if saved_selection_id is None:
            saved_selection_id = self.selected_node_id

        # Step 1: Re-measure actual sizes (unless skipped - e.g., after editing)
        if not skip_measurement:
            self._measure_actual_sizes(self.root_node)

        # Step 2: Re-apply layout, passing selected node to preserve its side
        from cogist.domain.layout import DefaultLayoutConfig

        # Create layout config with style_config for dynamic spacing lookup
        layout_config = DefaultLayoutConfig(
            style_config=self.style_config,  # Pass style_config for role-based spacing
        )

        # Use LayoutRegistry to create layout instance (demonstrates proper architecture)
        layout = layout_registry.get_layout("default", layout_config)

        # Get viewport size for canvas dimensions
        viewport_size = self.viewport().size()
        canvas_width = float(viewport_size.width())
        canvas_height = float(viewport_size.height())

        context = (
            {"focused_node_id": saved_selection_id} if saved_selection_id else None
        )
        layout.layout(
            self.root_node,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            context=context,
        )

        # Clear locked position flags after layout (only when requested)
        # This is typically done after drag operations or node additions
        # For undo/redo of text edits, we should preserve locked states
        if clear_locked_positions and self.root_node:
            # Recursively clear all locked positions in the tree
            def clear_locks(node):
                node.is_locked_position = False
                for child in node.children:
                    clear_locks(child)

            clear_locks(self.root_node)

        # Step 3: OPTIMIZATION - Try incremental UI update first
        # This is much faster than clearing and recreating all items
        # However, if force_rebuild_edges is True, skip incremental update because
        # parent-child relationships have changed and edges need to be rebuilt
        if not force_rebuild_edges:
            success = self._update_ui_positions_incremental()
        else:
            success = False

        if not success:
            # Fallback to full rebuild if incremental update failed
            # (e.g., new nodes added, nodes deleted, or parent-child relationships changed)
            self.scene.clear()
            self.node_items.clear()
            self.edge_items.clear()
            self._create_ui_items(self.root_node)

        # Update scene rect based on new content
        self.scene_manager.update_from_content()

        # Restore selection state
        if saved_selection_id:
            if saved_selection_id in self.node_items:
                # Original node still exists, select it
                self._select_node_by_id(saved_selection_id)
            elif parent_id and parent_id in self.node_items:
                # Original node was deleted, select its parent
                self._select_node_by_id(parent_id)
            elif self.root_node:
                # Fallback to root
                self._select_node_by_id(self.root_node.id)
            # Note: Do NOT call setFocus() here - let Qt manage focus naturally.
            # If user is interacting with dialog controls, focus should stay there.

    def _restore_selection_state_after_undo(self, node_id_before_undo):
        """Restore selection state after undo operation.

        Args:
            node_id_before_undo: The selected node ID before undo was performed
        """
        if not node_id_before_undo:
            # No previous selection, select root
            if "root" in self.node_items:
                self._select_node_by_id("root")
            return

        # Check if the previously selected node still exists
        if node_id_before_undo in self.node_items:
            # Node still exists, keep it selected
            self._select_node_by_id(node_id_before_undo)
        else:
            # Node was deleted by undo
            # Try to find its parent in the current tree
            parent_node, _ = self._find_parent_and_node(
                self.root_node, node_id_before_undo
            )

            if parent_node and parent_node.id in self.node_items:
                # Select the parent (the node that contained the deleted node)
                self._select_node_by_id(parent_node.id)
            elif "root" in self.node_items:
                # Fallback to root only if we have no better option
                self._select_node_by_id("root")
            # else: keep current selection (don't force deselect)

    def _ensure_node_visible(self, node_id: str):
        """Ensure the new node is visible in the viewport with margin.

        Args:
            node_id: The ID of the node to ensure is visible
        """
        if node_id not in self.node_items:
            return

        node_item = self.node_items[node_id]

        # Use ensureVisible with margin to ensure node stays away from edges
        # This is more reliable than manually setting scroll bar values
        # because it handles all edge cases and coordinate transformations correctly
        margin_px = 50
        self.ensureVisible(node_item, margin_px, margin_px)

    def showEvent(self, event):
        """Handle show event to initialize scene, create sample data, and center on root node."""
        super().showEvent(event)

        # Initialize scene rect and create sample data on first show
        if not self._scene_initialized:
            self.scene_manager.initialize_from_viewport()

            # Create sample data now that viewport has correct dimensions
            self.root_node = self._create_sample_data()

            # Initialize drag handler with the created root node
            from cogist.application.services import DragHandler

            self.drag_handler = DragHandler(self.root_node, self.node_provider)

            # CRITICAL: Force sceneRect to be centered around content
            # This ensures symmetric scroll range for panel compensation
            self.scene_manager.ensure_minimum_size()

            self._scene_initialized = True

        # Root node is already centered by layout algorithm, no need to scroll

    def resizeEvent(self, event):
        """Handle resize events to ensure sceneRect >= viewport size."""
        super().resizeEvent(event)
        self.scene_manager.ensure_minimum_size()

    def event(self, event: QEvent) -> bool:
        """Handle gestures for trackpad pinch zoom.

        Args:
            event: The event to handle

        Returns:
            True if event was handled, False otherwise
        """
        if event.type() == QEvent.Gesture:
            return self.gestureEvent(event)
        return super().event(event)

    def gestureEvent(self, event: QEvent) -> bool:
        """Handle pinch gesture for trackpad zoom.

        CRITICAL: Only handle scale (zoom), ignore rotation to prevent unwanted view rotation.
        Qt's PinchGesture includes both scale and rotation by default.
        By only processing scaleFactor() and returning True, we prevent Qt from applying rotation.

        Args:
            event: The gesture event

        Returns:
            True if gesture was handled
        """
        gesture = event.gesture(Qt.PinchGesture)
        if gesture:
            # CRITICAL: Only handle scale factor, explicitly ignore rotation
            # Qt's default pinch gesture includes rotation, which we don't want
            # By only calling scaleFactor() and returning True, rotation is ignored
            scale_factor = gesture.scaleFactor()

            # Apply zoom with anchor point
            if self._zoom_callback:
                self._zoom_callback(scale_factor)
            else:
                # Fallback: direct scaling without anchor compensation
                self.scale(scale_factor, scale_factor)

            # Return True to indicate we handled the gesture (prevents default rotation)
            return True
        return False

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Handle mouse wheel zoom with Ctrl modifier.

        Ctrl + Wheel: Zoom in/out
        Wheel only: Default behavior (scrolling, but scrollbars are hidden)

        Args:
            event: The wheel event
        """
        # Check if Ctrl key is pressed
        if event.modifiers() & Qt.ControlModifier:
            # Get the angle delta (positive = up/zoom in, negative = down/zoom out)
            delta = event.angleDelta().y()

            # Calculate zoom factor (1.1x per 120 degrees of rotation)
            # Typical wheel delta is ±120 per notch
            factor = 1.0 + (delta / 1200.0)  # 10% per notch

            # Clamp factor to reasonable range
            factor = max(0.5, min(2.0, factor))

            # Apply zoom with anchor point
            if self._zoom_callback:
                self._zoom_callback(factor)
            else:
                # Fallback: direct scaling without anchor compensation
                self.scale(factor, factor)

            event.accept()
        else:
            # Default behavior: pass to parent for scrolling
            super().wheelEvent(event)

    def _restore_selection_state_after_redo(self, node_id_before_redo):
        """Restore selection state after redo operation.

        Args:
            node_id_before_redo: The selected node ID before redo was performed
        """
        # For redo, use the same logic as undo
        self._restore_selection_state_after_undo(node_id_before_redo)

    def _restore_selection_state(self):
        """Restore selection state after undo/redo.

        This method intelligently determines which node should be selected
        based on the current state of the mind map.
        """
        if not self.selected_node_id:
            # No selection, select root
            if "root" in self.node_items:
                self._select_node_by_id("root")
            return

        # Try to restore the exact node
        if self.selected_node_id in self.node_items:
            self._select_node_by_id(self.selected_node_id)
        else:
            # The previously selected node no longer exists in UI
            # Find its parent and select that instead
            parent_node, _ = self._find_parent_and_node(
                self.root_node, self.selected_node_id
            )

            if parent_node and parent_node.id in self.node_items:
                self._select_node_by_id(parent_node.id)
            elif "root" in self.node_items:
                # Fallback to root
                self._select_node_by_id("root")

    def _save_file(self):
        """Save current mind map to file."""
        try:
            # If we have a current file path, save directly without dialog
            if self.current_file_path:
                file_path = self.current_file_path
            else:
                # Get file path from user
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save Mind Map",
                    "",
                    "Cogist Files (*.cgs);;All Files (*)",
                )

                if not file_path:
                    return

            # Use MindMapService to save (Application Layer)
            saved_path = self.mindmap_service.save_mindmap(
                file_path, style_config=self.style_config
            )

            # Update current file path
            self.current_file_path = str(saved_path)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save:\n{e}",
            )

    def _open_file(self):
        """Load mind map from file."""
        # CRITICAL: Check for unsaved changes before opening new file
        if self.mindmap_service.is_modified():
            reply = QMessageBox.warning(
                self,
                "Unsaved Changes",
                "The current mind map has unsaved changes.\n\nDo you want to save before opening?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save,
            )

            if reply == QMessageBox.Save:
                # Save current file first
                self._save_file()
                # If user cancelled the save dialog, abort opening
                if not self.mindmap_service.is_modified():
                    pass  # Save succeeded, continue
                else:
                    return  # Save was cancelled
            elif reply == QMessageBox.Discard:
                pass  # Discard changes, continue
            else:
                return  # Cancelled, abort opening

        try:
            # Get file path from user
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Open Mind Map",
                "",
                "Cogist Files (*.cgs);;All Files (*)",
            )

            if not file_path:
                return

            # Use MindMapService to load (Application Layer)
            self.root_node, loaded_style_config = self.mindmap_service.load_mindmap(
                file_path
            )

            # CRITICAL: Update style_config if file contains style data
            if loaded_style_config is not None:
                self.style_config = loaded_style_config
                # Notify listeners that style config has changed
                self.style_config_changed.emit()

            # Update current file path
            self.current_file_path = str(self.mindmap_service.get_current_file())

            # CRITICAL: Re-initialize Application Layer services with new root node
            from cogist.application.services import DragHandler
            from cogist.presentation.adapters import QtNodeProvider

            self.node_provider = QtNodeProvider(self.node_items)
            self.drag_handler = DragHandler(self.root_node, self.node_provider)

            # Clear scene and rebuild UI
            self.scene.clear()
            self.node_items.clear()
            self.edge_items.clear()
            self._create_ui_items(self.root_node)

            # CRITICAL: Re-run layout algorithm to calculate correct positions
            # This ensures proper spacing even if saved positions are outdated
            self._refresh_layout(skip_measurement=True)

            # Update scene rect based on new content
            self.scene_manager.update_from_content()

            # Select root node
            self._select_node_by_id(self.root_node.id)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open:\n{e}",
            )

    def _hide_parent_edge(self, node: Node):
        """Hide the edge from parent to this node during drag."""
        item = self.node_items.get(node.id)
        if item:
            for edge in item.connected_edges:
                # Find the edge where this node is the target
                if hasattr(edge, "target_item") and edge.target_item == item:
                    edge.setVisible(False)
                    break

    def _restore_parent_edge(self, node: Node):
        """Restore the edge from parent to this node after drag."""
        item = self.node_items.get(node.id)
        if item:
            for edge in item.connected_edges:
                if hasattr(edge, "target_item") and edge.target_item == item:
                    edge.setVisible(True)
                    break

    def _detect_potential_parent(
        self, dragged_item: NodeItem, mouse_pos: QPointF
    ) -> Node | None:
        """
        Detect the best potential parent based on anchor point distance.

        Uses current position (not is_right_side) to determine which side the node is on.
        Distance is calculated from dragged node center to candidate's anchor point.
        """
        dragged_node = self._find_node_by_id(self.root_node, self._dragged_node_id)
        if not dragged_node or not self.root_node:
            return None

        # Determine current side based on actual position, not is_right_side property
        is_currently_right = self._is_node_on_right_side(self._dragged_node_id)

        # Calculate dragged node center for distance comparison
        root_item = self.node_items.get(self.root_node.id)
        if not root_item:
            return None

        best_candidate = None
        best_distance = float("inf")

        # Calculate dragged node center
        dragged_center = dragged_item.scenePos() + dragged_item.boundingRect().center()

        for node_id, item in self.node_items.items():
            if node_id == self._dragged_node_id:
                continue  # Skip self

            target_node = self._find_node_by_id(self.root_node, node_id)
            if not target_node:
                continue

            # Cannot be descendant (would create cycle)
            if target_node in dragged_node.get_all_descendants():
                continue

            # Get positions
            target_pos = item.scenePos()

            # Rule 6: L node looks for parent with larger anchor X; R node looks for smaller anchor X
            # Calculate anchor points based on DRAGGED node's side (not candidate's side)
            dragged_rect = dragged_item.boundingRect()
            if is_currently_right:
                # R node: its anchor is on left edge (closer to root center)
                dragged_anchor_x = dragged_item.scenePos().x()
            else:
                # L node: its anchor is on right edge (closer to root center)
                dragged_anchor_x = dragged_item.scenePos().x() + dragged_rect.width()

            candidate_rect = item.boundingRect()
            if is_currently_right:
                # For R node, parent must be on left side, parent's anchor is on right edge (away from root)
                candidate_anchor_x = target_pos.x() + candidate_rect.width()
            else:
                # For L node, parent must be on right side, parent's anchor is on left edge (away from root)
                candidate_anchor_x = target_pos.x()

            # Rule 6: Check anchor point relationship (CRITICAL FILTER)
            if is_currently_right:
                # R node: parent anchor X must be SMALLER than dragged anchor X
                if candidate_anchor_x >= dragged_anchor_x:
                    continue  # Parent is on wrong side (right of dragged node)
            else:
                # L node: parent anchor X must be LARGER than dragged anchor X
                if candidate_anchor_x <= dragged_anchor_x:
                    continue  # Parent is on wrong side (left of dragged node)

            # Calculate anchor point for candidate node
            # Right side: use right edge center; Left side: use left edge center
            rect = item.boundingRect()
            if is_currently_right:
                # Candidate is on left, use its right edge as anchor
                anchor_x = target_pos.x() + rect.width()
                anchor_y = target_pos.y() + rect.height() / 2
            else:
                # Candidate is on right, use its left edge as anchor
                anchor_x = target_pos.x()
                anchor_y = target_pos.y() + rect.height() / 2

            anchor_point = QPointF(anchor_x, anchor_y)

            # Calculate Euclidean distance from dragged center to candidate anchor
            dx = dragged_center.x() - anchor_point.x()
            dy = dragged_center.y() - anchor_point.y()
            distance = (dx * dx + dy * dy) ** 0.5

            if distance < best_distance:
                best_distance = distance
                best_candidate = target_node

        return best_candidate

    def _update_temp_drag_edge(
        self, dragged_node: Node | None, potential_parent: Node | None
    ):
        """Create or update temporary edge to show connection during drag."""

        # Remove old temp edge
        if self._temp_drag_edge:
            self.scene.removeItem(self._temp_drag_edge)
            self._temp_drag_edge = None

        # Create new temp edge if we have a potential parent
        if potential_parent and dragged_node:
            parent_item = self.node_items.get(potential_parent.id)
            dragged_item = self.node_items.get(dragged_node.id)

            if parent_item and dragged_item:
                # Get connector config from role-based style
                from cogist.domain.styles.extended_styles import NodeRole

                parent_depth = potential_parent.depth
                role_map = {
                    0: NodeRole.ROOT,
                    1: NodeRole.PRIMARY,
                    2: NodeRole.SECONDARY,
                }
                role = role_map.get(parent_depth, NodeRole.TERTIARY)

                # Default values
                color = "#999999"
                connector_shape = "bezier"

                if role in self.style_config.role_styles:
                    role_style = self.style_config.role_styles[role]

                    # Get connector color from color pool
                    if role_style.connector_color_index < len(self.style_config.color_pool):
                        color = self.style_config.color_pool[role_style.connector_color_index]
                    else:
                        color = "#999999"

                    connector_shape = role_style.connector_shape

                # Create a temporary EdgeItem with proper styling
                from cogist.presentation.items.edge_item import EdgeItem

                temp_edge = EdgeItem(
                    parent_item,
                    dragged_item,
                    color=color,
                    style_config=self.style_config,
                )

                # Set the connector strategy based on config (already set above)
                from cogist.presentation.connectors import (
                    BezierConnector,
                    OrthogonalConnector,
                    RoundedOrthogonalConnector,
                    SharpFirstRoundedConnector,
                    StraightConnector,
                )

                shape_map = {
                    "bezier": BezierConnector(),
                    "bezier_uniform": BezierConnector(),
                    "orthogonal": OrthogonalConnector(),
                    "straight": StraightConnector(),
                    "rounded_orthogonal": RoundedOrthogonalConnector(),
                    "sharp_first_rounded": SharpFirstRoundedConnector(),
                }

                temp_edge.connector_strategy = shape_map.get(
                    connector_shape, BezierConnector()
                )
                temp_edge.setZValue(0)  # Behind nodes

                # Force update to calculate path
                temp_edge.update_curve()

                self.scene.addItem(temp_edge)
                self._temp_drag_edge = temp_edge

    def _update_subtree_is_right_side(self, node: Node, is_right: bool):
        """Recursively update is_right_side for entire subtree."""
        item = self.node_items.get(node.id)
        if item:
            item.is_right_side = is_right

        for child in node.children:
            self._update_subtree_is_right_side(child, is_right)

    def _save_subtree_relative_positions(self, node: Node):
        """Save relative positions of all nodes in subtree relative to dragged node."""
        dragged_item = self.node_items.get(node.id)
        if not dragged_item:
            return

        dragged_scene_pos = dragged_item.scenePos()

        # Clear previous data
        self._subtree_initial_positions.clear()

        # Save for root of subtree (offset should be 0,0)
        self._subtree_initial_positions[node.id] = QPointF(0.0, 0.0)

        # Recursively save children
        self._save_children_relative_positions(node, dragged_scene_pos)

    def _save_children_relative_positions(self, node: Node, root_scene_pos: QPointF):
        """Recursively save children's positions relative to subtree root."""
        for child in node.children:
            child_item = self.node_items.get(child.id)
            if child_item:
                # Calculate offset from root
                child_scene_pos = child_item.scenePos()
                offset = QPointF(
                    child_scene_pos.x() - root_scene_pos.x(),
                    child_scene_pos.y() - root_scene_pos.y(),
                )
                self._subtree_initial_positions[child.id] = offset

                # Recursively save grandchildren
                self._save_children_relative_positions(child, root_scene_pos)

    def _apply_subtree_positions(self, new_root_pos: QPointF, mirror_x: bool):
        """Apply saved relative positions to entire subtree."""
        for node_id, offset in self._subtree_initial_positions.items():
            item = self.node_items.get(node_id)
            if item:
                if mirror_x:
                    # Mirror the X offset
                    mirrored_offset_x = -offset.x()
                    new_x = new_root_pos.x() + mirrored_offset_x
                else:
                    new_x = new_root_pos.x() + offset.x()

                new_y = new_root_pos.y() + offset.y()

                # Set position considering parent-child relationship
                parent_item = item.parentItem()
                if parent_item:
                    local_pos = parent_item.mapFromScene(QPointF(new_x, new_y))
                    item.setPos(local_pos)
                else:
                    item.setPos(new_x, new_y)

    def _flip_subtree_visual(self, node: Node, root_x: float, new_is_right: bool):
        """Visually flip subtree X positions during drag (without modifying Node entity)."""
        item = self.node_items.get(node.id)
        if item:
            # Get current scene position
            current_scene_pos = item.scenePos()

            # Mirror X coordinate across root
            distance_from_root = current_scene_pos.x() - root_x
            mirrored_x = root_x - distance_from_root

            # Set scene position directly (bypasses parent-child relative positioning)
            # We need to convert scene pos to local pos for setPos
            parent_item = item.parentItem()
            if parent_item:
                # Convert mirrored scene position to local position relative to parent
                local_pos = parent_item.mapFromScene(
                    QPointF(mirrored_x, current_scene_pos.y())
                )
                item.setPos(local_pos)
            else:
                # No parent, set scene position directly
                item.setPos(mirrored_x, current_scene_pos.y())

        # Recursively flip children
        for child in node.children:
            self._flip_subtree_visual(child, root_x, new_is_right)

    def _flip_subtree_side(self, node: Node, new_is_right: bool):
        """Recursively flip is_right_side and mirror X positions for entire subtree."""
        if not self.root_node:
            return

        root_item = self.node_items.get(self.root_node.id)
        if not root_item:
            return

        root_x = root_item.scenePos().x()

        # Recursively flip
        self._flip_subtree_recursive(node, root_x, new_is_right)

    def _flip_subtree_recursive(self, node: Node, root_x: float, new_is_right: bool):
        """Update is_right_side flag for entire subtree (position already updated during drag)."""
        item = self.node_items.get(node.id)
        if item:
            # CRITICAL FIX: Only update the is_right_side flag
            # Position was already updated during drag by _apply_subtree_positions
            # and mouseReleaseEvent position update
            # DO NOT mirror position again to avoid double-flipping
            item.is_right_side = new_is_right

        # Recursively update children
        for child in node.children:
            self._flip_subtree_recursive(child, root_x, new_is_right)

    def _update_node_depths_recursive(self, node: Node):
        """Recursively update depth values after parent change."""
        if node.parent:
            node.depth = node.parent.depth + 1
        else:
            node.depth = 0

        # Recursively update children
        for child in node.children:
            self._update_node_depths_recursive(child)
