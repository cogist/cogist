#!/usr/bin/env python3
"""
Cogist - Main Application Entry Point

This is the main demo application showing the four-layer architecture:
- Domain Layer: Node entity + DefaultLayout algorithm
- Presentation Layer: NodeItem, EdgeItem, MindMapView
- Infrastructure Layer: (to be added)
- Application Layer: Command pattern integration
"""

import sys

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QPainter
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGraphicsScene,
    QGraphicsView,
    QMainWindow,
    QMessageBox,
)

from cogist.application.commands import (
    AddNodeCommand,
    DeleteNodeCommand,
    EditTextCommand,
)
from cogist.domain.entities.node import Node
from cogist.domain.layout.default_layout import DefaultLayout
from cogist.presentation.items.edge_item import EdgeItem
from cogist.presentation.items.node_item import NodeItem


class CommandHistory:
    """Simple command history manager for undo/redo."""

    def __init__(self):
        self._history = []
        self._current_index = -1

    def execute(self, command):
        """Execute a command and add it to history."""
        # Remove any redo commands if we're not at the end
        if self._current_index < len(self._history) - 1:
            self._history = self._history[: self._current_index + 1]

        # Execute and store
        command.execute()
        self._history.append(command)
        self._current_index += 1

    def undo(self):
        """Undo the last command."""
        if self._current_index >= 0:
            command = self._history[self._current_index]
            command.undo()
            self._current_index -= 1
            return True
        return False

    def redo(self):
        """Redo the next command."""
        if self._current_index < len(self._history) - 1:
            self._current_index += 1
            command = self._history[self._current_index]
            command.execute()
            return True
        return False


class MainWindow(QMainWindow):
    """Main application window with menu bar."""

    def __init__(self):
        super().__init__()

        # Initialize style system
        from cogist.domain.styles import templates

        self.current_style = templates.create_default_template()

        # Apply global styles
        self._apply_global_styles()

        # Create mind map view with style configuration
        self.mindmap_view = MindMapView(style_config=self.current_style)
        self.setCentralWidget(self.mindmap_view)

        # Enable document mode to reduce decorations
        self.setDocumentMode(True)

        # Disable dock nesting and animated docks
        self.setDockNestingEnabled(False)

        # Create menu bar
        self._create_menu_bar()

    def _apply_global_styles(self):
        """Apply global QSS styles to the application."""
        self.setStyleSheet("""
            /* Main window background */
            QMainWindow {
                background-color: #F5F5F5;
            }

            /* Hide dock widget separator */
            QMainWindow::separator {
                width: 0;
                height: 0;
                background: #F5F5F5;
            }
            QDockWidget::separator {
                background: #F5F5F5;
            }

            /* Menu bar style */
            QMenuBar {
                background-color: #FFFFFF;
                border-bottom: 1px solid #E0E0E0;
                padding: 2px;
            }
            QMenuBar::item {
                padding: 5px 10px;
                background-color: transparent;
            }
            QMenuBar::item:selected {
                background-color: #E3F2FD;
                border-radius: 3px;
            }
            QMenuBar::item:pressed {
                background-color: #BBDEFB;
            }

            /* Menu style */
            QMenu {
                background-color: #FFFFFF;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #E3F2FD;
                border-radius: 3px;
            }
            QMenu::separator {
                height: 1px;
                background-color: #E0E0E0;
                margin: 5px 0;
            }

            /* Dock widget style - removes the black separator line */
            QDockWidget {
                background-color: #F5F5F5;
                border: none;
            }
            QDockWidget::title {
                background-color: #E8E8E8;
                padding-left: 10px;
                padding-top: 6px;
                padding-bottom: 6px;
                font-weight: bold;
                font-size: 12px;
                color: #424242;
            }
            QDockWidget::close-button,
            QDockWidget::float-button {
                background-color: transparent;
                border: none;
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 16px;
                height: 16px;
            }
            QDockWidget::close-button:hover,
            QDockWidget::float-button:hover {
                background-color: #E0E0E0;
                border-radius: 3px;
            }

            /* GroupBox styling to prevent title overlap */
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                margin-top: 15px;
                padding-top: 18px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                left: 10px;
                top: 0px;
                padding: 0 8px;
                background-color: white;
            }

            /* Separator between dock widget and main area */
            QSplitter::handle {
                background-color: #E0E0E0;
                width: 2px;
            }
            QSplitter::handle:horizontal {
                width: 2px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 transparent, stop:0.5 #D0D0D0, stop:1 transparent);
            }

            /* Unified widget styles for the debugger panel */
            QPushButton {
                border: 1px solid #CCCCCC;
                border-radius: 6px;
                padding: 4px 8px;
                background-color: #F5F5F5;
            }
            QPushButton:hover {
                background-color: #E8E8E8;
            }
            QPushButton:pressed {
                background-color: #D0D0D0;
            }
            QSpinBox {
                border: 1px solid #CCCCCC;
                border-radius: 6px;
                padding: 4px 8px;
                background-color: white;
            }
            QSpinBox:focus {
                border: 1px solid #2196F3;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                border: none;
                width: 16px;
            }
            QSpinBox::up-arrow {
                image: none;
                border: none;
            }
            QSpinBox::down-arrow {
                image: none;
                border: none;
            }
        """)

    def _create_menu_bar(self):
        """Create the menu bar with File and Edit menus."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        # New
        new_action = QAction("&New", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._new_file)
        file_menu.addAction(new_action)

        file_menu.addSeparator()

        # Open
        open_action = QAction("&Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.mindmap_view._open_file)
        file_menu.addAction(open_action)

        # Save
        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.mindmap_view._save_file)
        file_menu.addAction(save_action)

        # Close
        close_action = QAction("&Close", self)
        close_action.setShortcut("Ctrl+W")
        close_action.triggered.connect(self._close_file)
        file_menu.addAction(close_action)

        file_menu.addSeparator()

        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        # Undo
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        undo_action.triggered.connect(self._undo)
        edit_menu.addAction(undo_action)

        # Redo
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        redo_action.triggered.connect(self._redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        # Add Child
        self.add_child_action = QAction("Add &Child", self)
        self.add_child_action.setShortcut("Tab")
        self.add_child_action.triggered.connect(self._add_child)
        edit_menu.addAction(self.add_child_action)

        # Add Sibling
        self.add_sibling_action = QAction("Add Sibling", self)
        self.add_sibling_action.setShortcut("Return")
        self.add_sibling_action.triggered.connect(self._add_sibling)
        edit_menu.addAction(self.add_sibling_action)

        # Delete
        delete_action = QAction("&Delete", self)
        delete_action.setShortcut("Delete")
        delete_action.triggered.connect(self._delete)
        edit_menu.addAction(delete_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        # Zoom In
        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut("Ctrl++")
        zoom_in_action.triggered.connect(self._zoom_in)
        view_menu.addAction(zoom_in_action)

        # Zoom Out
        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut("Ctrl+-")
        zoom_out_action.triggered.connect(self._zoom_out)
        view_menu.addAction(zoom_out_action)

        view_menu.addSeparator()

        # Style Panel (Development Tool)
        style_panel_action = QAction("&Style Panel", self)
        style_panel_action.setShortcut("Ctrl+Shift+S")
        style_panel_action.triggered.connect(self._open_style_panel)
        view_menu.addAction(style_panel_action)

        view_menu.addSeparator()

        # Fit View
        fit_view_action = QAction("&Fit View", self)
        fit_view_action.setShortcut("Ctrl+0")
        fit_view_action.triggered.connect(self._fit_view)
        view_menu.addAction(fit_view_action)

        # Actual Size
        actual_size_action = QAction("&Actual Size", self)
        actual_size_action.setShortcut("Ctrl+1")
        actual_size_action.triggered.connect(self._actual_size)
        view_menu.addAction(actual_size_action)

    def _close_file(self):
        """Close the current file and create a new one (same as New)."""
        # For SDI, Close = New (keep at least one blank document)
        # This will also handle the confirmation dialog
        self._new_file()

    def _new_file(self):
        """Create a new mind map."""
        # Ask user to confirm (in a full implementation, check for unsaved changes)
        reply = QMessageBox.question(
            self,
            "New Mind Map",
            "Create a new mind map? Any unsaved changes will be lost.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # Reinitialize the mind map view (same as __init__)
            self.mindmap_view._initialize_new_mindmap()

    def _undo(self):
        """Undo the last operation."""
        # Save selection state BEFORE undo
        node_id_before_undo = self.mindmap_view.selected_node_id
        parent_id_before_undo = None

        # Also save the parent ID in case the selected node gets deleted
        if node_id_before_undo:
            # Find the node in the domain tree and get its parent
            _, node_before = self.mindmap_view._find_parent_and_node(
                self.mindmap_view.root_node, node_id_before_undo
            )
            if node_before and node_before.parent:
                parent_id_before_undo = node_before.parent.id

        if self.mindmap_view.command_history.undo():
            print("Undo successful")
            # Pass saved selection IDs to _refresh_layout()
            self.mindmap_view._refresh_layout(
                saved_selection_id=node_id_before_undo, parent_id=parent_id_before_undo
            )

    def _redo(self):
        """Redo the last undone operation."""
        # Save selection state BEFORE redo
        node_id_before_redo = self.mindmap_view.selected_node_id
        parent_id_before_redo = None

        # Also save the parent ID in case the selected node gets deleted
        if node_id_before_redo:
            _, node_before = self.mindmap_view._find_parent_and_node(
                self.mindmap_view.root_node, node_id_before_redo
            )
            if node_before and node_before.parent:
                parent_id_before_redo = node_before.parent.id

        if self.mindmap_view.command_history.redo():
            print("Redo successful")
            # Pass saved selection IDs to _refresh_layout()
            self.mindmap_view._refresh_layout(
                saved_selection_id=node_id_before_redo, parent_id=parent_id_before_redo
            )

    def _add_child(self):
        """Add a child node."""
        if self.mindmap_view.selected_node_id:
            self.mindmap_view._add_selected_child()

    def _add_sibling(self):
        """Add a sibling node."""
        if self.mindmap_view.selected_node_id:
            self.mindmap_view._add_sibling_node()

    def _delete(self):
        """Delete the selected node."""
        if self.mindmap_view.selected_node_id:
            self.mindmap_view._delete_selected_node()

    def _zoom_in(self):
        """Zoom in the view."""
        self.mindmap_view.scale(1.2, 1.2)

    def _zoom_out(self):
        """Zoom out the view."""
        self.mindmap_view.scale(1 / 1.2, 1 / 1.2)

    def _fit_view(self):
        """Fit the view to show all content with margins."""
        # Get bounding rect of all items
        items_rect = self.mindmap_view.scene.itemsBoundingRect()

        # Add margins (20% on each side)
        margin_x = items_rect.width() * 0.2
        margin_y = items_rect.height() * 0.2
        expanded_rect = items_rect.adjusted(-margin_x, -margin_y, margin_x, margin_y)

        # Fit view to expanded rect
        self.mindmap_view.fitInView(expanded_rect, Qt.KeepAspectRatio)

    def _actual_size(self):
        """Reset zoom to actual size (100%)."""
        self.mindmap_view.resetTransform()

    def _open_style_panel(self):
        """Open the style panel for development."""
        from PySide6.QtWidgets import QSplitter

        from cogist.presentation.dialogs.style_panel import StylePanel

        # Check if panel already exists and is still valid
        if hasattr(self, "style_panel") and self.style_panel:
            try:
                # Toggle visibility
                is_visible = self.style_panel.isVisible()
                self.style_panel.setVisible(not is_visible)
                if is_visible:
                    # When hiding, restore single widget
                    self.setCentralWidget(self.mindmap_view)
                    # CRITICAL: Clear the reference to avoid dangling pointer
                    # The panel will be recreated when needed
                    del self.style_panel
                else:
                    # When showing, restore splitter
                    splitter = QSplitter(Qt.Horizontal)
                    splitter.addWidget(self.mindmap_view)
                    splitter.addWidget(self.style_panel)
                    splitter.setStretchFactor(0, 1)  # Mind map takes most space
                    splitter.setStretchFactor(1, 0)  # Panel has fixed width
                    splitter.setCollapsible(1, False)  # Panel cannot be collapsed
                    self.setCentralWidget(splitter)
            except RuntimeError:
                # Panel was deleted, recreate it
                del self.style_panel
                self._open_style_panel()  # Recursively call to create new panel
                return
        else:
            # Create new panel
            self.style_panel = StylePanel(self)

            # Create a horizontal splitter with mind map view and style panel
            splitter = QSplitter(Qt.Horizontal)
            splitter.addWidget(self.mindmap_view)
            splitter.addWidget(self.style_panel)
            splitter.setStretchFactor(0, 1)  # Mind map takes most space
            splitter.setStretchFactor(1, 0)  # Panel has fixed width
            splitter.setCollapsible(1, False)  # Panel cannot be collapsed

            # Set initial widths (mind map: 1100px, panel: 300px)
            splitter.setSizes([1100, 300])

            # Set as central widget
            self.setCentralWidget(splitter)


class MindMapView(QGraphicsView):
    """Mind map view with Default layout and command pattern integration."""

    def __init__(self, style_config=None):
        super().__init__()

        # Store style configuration
        from cogist.domain.styles import templates

        self.style_config = style_config or templates.create_default_template()

        # Create scene
        self.scene = QGraphicsScene()
        self.scene.setBackgroundBrush(Qt.white)

        # CRITICAL: Set a large scene rect to ensure centerOn() works properly
        # Without this, when scene is smaller than viewport, centerOn() has no effect
        # and alignment controls positioning instead
        import sys

        self.scene.setSceneRect(
            -sys.maxsize, -sys.maxsize, sys.maxsize * 2, sys.maxsize * 2
        )

        self.setScene(self.scene)

        # View settings
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

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

        # Store UI items
        self.node_items = {}
        self.edge_items = []

        # Command pattern
        self.command_history = CommandHistory()

        # Selection
        self.selected_node_id = None

        # File tracking
        self.current_file_path: str | None = None

        # Enable focus for keyboard events
        self.setFocusPolicy(Qt.StrongFocus)

        # Create sample data
        self.root_node = self._create_sample_data()

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

        # Reset command history
        self.command_history = CommandHistory()

        # Create sample data (this will also select the root node)
        self.root_node = self._create_sample_data()

        # Reset view transformation (zoom, rotation, etc.)
        self.resetTransform()

    def _create_sample_data(self):
        """Create sample mind map data with only a root node."""
        # Root node only - user will add children via Tab key
        root = Node(id="root", text="Central Topic", is_root=True, color="#2196F3")

        # Step 1: Create temporary UI items to measure actual rendered sizes
        # (Don't add to scene yet)
        self._measure_actual_sizes(root)

        # Step 2: Apply layout with actual sizes
        layout = DefaultLayout(style=self.style_config)
        layout.layout(root, canvas_width=1200, canvas_height=800)

        # Step 3: Create final UI items with correct sizes and positions
        self._create_ui_items(root)

        # Select root node by default
        self.selected_node_id = root.id
        if root.id in self.node_items:
            self.node_items[root.id].setSelected(True)

        return root

    def _measure_actual_sizes(self, root: Node):
        """
        Create temporary NodeItems to measure actual rendered sizes,
        then sync back to domain nodes.
        """
        branch_colors = [
            "#FF6B6B",
            "#4ECDC4",
            "#45B7D1",
            "#FFA07A",
            "#98D8C8",
            "#F7DC6F",
            "#BB8FCE",
            "#85C1E9",
        ]

        def measure_recursive(node: Node, branch_color: str | None = None):
            current_color = branch_color if branch_color else node.color

            # Create temporary item (not added to scene)
            temp_item = NodeItem(
                text=node.text,
                width=node.width,
                height=node.height,
                color=current_color,
                is_root=node.is_root,
                depth=node.depth,
                style_config=self.style_config,  # Pass style configuration
                # DO NOT use use_domain_size here - we need to measure actual size
            )

            # Sync actual measured size back to domain node
            node.width = temp_item.node_width
            node.height = temp_item.node_height

            # Recursively measure children
            for child in node.children:
                # Determine branch color for first-level children
                child_branch_color = None
                if node.is_root:
                    idx = node.children.index(child) % len(branch_colors)
                    child_branch_color = branch_colors[idx]
                else:
                    child_branch_color = branch_color

                measure_recursive(child, child_branch_color)

        measure_recursive(root)

    def _create_ui_items(self, root: Node):
        """Create UI items from node tree."""

        # Define branch colors (light colors for background, black text)
        branch_colors = [
            "#FF6B6B",  # Red
            "#4ECDC4",  # Teal
            "#45B7D1",  # Blue
            "#FFA07A",  # Salmon
            "#98D8C8",  # Mint
            "#F7DC6F",  # Yellow
            "#BB8FCE",  # Purple
            "#85C1E9",  # Light Blue
        ]

        def create_items_recursive(
            node: Node,
            parent_item: NodeItem | None = None,
            branch_color: str | None = None,
        ):
            # Use branch color if assigned, otherwise use root color
            current_color = branch_color if branch_color else node.color

            # Create node item
            item = NodeItem(
                text=node.text,
                width=node.width,
                height=node.height,
                color=current_color,
                is_root=node.is_root,
                depth=node.depth,
                use_domain_size=True,  # Use domain layer's pre-measured size
                style_config=self.style_config,  # Pass style configuration
            )
            item.setPos(*node.position)

            self.scene.addItem(item)
            self.node_items[node.id] = item

            # If has parent, link to parent and create edge immediately
            if parent_item:
                parent_item.add_child_item(item)
                # Use the branch color for the edge (same as parent and child nodes)
                edge_color = current_color
                edge = EdgeItem(parent_item, item, color=edge_color)
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
                    else branch_colors[len(root.children) - len(node.children)]
                    if node == root
                    else None
                )
                create_items_recursive(
                    child,
                    item,
                    child_branch_color
                    if branch_color
                    else (
                        branch_colors[node.children.index(child) % len(branch_colors)]
                        if node == root
                        else None
                    ),
                )

        create_items_recursive(root)

    def _get_main_window(self):
        """Get the main window reference, handling QSplitter nesting.

        Returns:
            MainWindow instance or None
        """
        parent = self.parent()
        while parent:
            if isinstance(parent, MainWindow):
                return parent
            parent = parent.parent()
        return None

    def eventFilter(self, obj, event):  # noqa: N802
        """Handle keyboard shortcuts for editing commands."""
        from PySide6.QtCore import QEvent

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

            # Space: Edit selected node text
            if key_event.key() == Qt.Key_Space and self.selected_node_id:
                # Check if currently editing a node
                if self.selected_node_id in self.node_items:
                    node_item = self.node_items[self.selected_node_id]
                    if node_item.edit_widget is not None:
                        # Currently editing, let the edit widget handle Space for text input
                        # Return super() to allow normal event propagation to focused widget
                        return super().eventFilter(obj, event)
                self._edit_selected_node()
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

        return super().eventFilter(obj, event)

    def mousePressEvent(self, event):  # noqa: N802
        """Handle mouse press to select nodes."""

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
        else:
            self._deselect_node()

        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):  # noqa: N802
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
                print(f"Selected: {node_id}")
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
        print(f"Selected: {node_id}")

    def _deselect_node(self):
        """Deselect all nodes."""
        if self.selected_node_id and self.selected_node_id in self.node_items:
            self.node_items[self.selected_node_id].setSelected(False)
        self.selected_node_id = None

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

        parent_node = self.root_node if self.selected_node_id == "root" else None

        # Find parent node in tree
        if not parent_node:
            parent_node = self._find_node_by_id(self.root_node, self.selected_node_id)

        if not parent_node:
            return

        # Generate unique name
        new_name = self._generate_node_name(parent_node)

        # Execute add command
        cmd = AddNodeCommand(parent_node, new_name)
        self.command_history.execute(cmd)

        # Get the new node ID (it's the last child)
        new_node_id = parent_node.children[-1].id

        # Refresh UI
        self._refresh_layout()

        # Select the new node
        self._select_node_by_id(new_node_id)

        # Ensure the new node is visible in the viewport (with margin)
        # Only scrolls if the node is outside the current view
        QTimer.singleShot(0, lambda: self._ensure_node_visible(new_node_id))

        print(f"Added child '{new_name}' to '{parent_node.text}'")

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

        # Determine which node to select after deletion
        # Priority: previous sibling > parent
        next_selected_id = parent_node.id  # Default to parent

        # Find the index of the node to delete
        for i, child in enumerate(parent_node.children):
            if child.id == node_to_delete.id:
                # If there's a previous sibling, select it
                if i > 0:
                    next_selected_id = parent_node.children[i - 1].id
                break

        # Execute delete command
        cmd = DeleteNodeCommand(parent_node, node_to_delete)
        self.command_history.execute(cmd)

        # Select the determined node after deletion
        self.selected_node_id = next_selected_id

        # Refresh UI
        self._refresh_layout()
        print(f"Deleted {node_to_delete.id}")

    def _edit_selected_node(self, cursor_position: int = -1):
        """Edit the selected node text with inline editing.

        Args:
            cursor_position: Cursor position in text (-1 for select all)
        """
        if not self.selected_node_id or self.selected_node_id not in self.node_items:
            print("No node selected")
            return

        node_item = self.node_items[self.selected_node_id]
        # CRITICAL FIX: Capture the node ID at edit start time
        # This prevents issues when mouse click changes selection during editing
        editing_node_id = self.selected_node_id

        # Start inline editing
        def on_text_changed(new_text):
            # Update domain node using EditTextCommand
            node = self._find_node_by_id(self.root_node, editing_node_id)
            if node:
                # Update text
                cmd = EditTextCommand(node, new_text)
                self.command_history.execute(cmd)
                # Sync UI dimensions back to domain entity (width/height changed due to word wrap)
                node.width = node_item.node_width
                node.height = node_item.node_height
                # Re-layout: DO NOT skip measurement - re-measure to ensure sizes are accurate
                # This prevents issues where domain sizes don't match actual UI rendering
                self._refresh_layout(skip_measurement=False)

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

    def _add_sibling_node(self):
        """Add a sibling node to the selected node."""
        if not self.selected_node_id or self.selected_node_id == "root":
            print("Cannot add sibling to root or no selection")
            return  # Can't add sibling to root

        # Find parent and current node
        parent_node, current_node = self._find_parent_and_node(
            self.root_node, self.selected_node_id
        )

        if not parent_node or not current_node:
            print("Parent or current node not found")
            return

        # Generate unique name (same as child naming)
        new_name = self._generate_node_name(parent_node)

        # Execute add command
        cmd = AddNodeCommand(parent_node, new_name)
        self.command_history.execute(cmd)

        # Get the new node ID (it's the last child)
        new_node_id = parent_node.children[-1].id

        # Refresh UI
        self._refresh_layout()

        # Select the new node
        self._select_node_by_id(new_node_id)

        # Ensure the new node is visible in the viewport (with margin)
        # Only scrolls if the node is outside the current view
        QTimer.singleShot(0, lambda: self._ensure_node_visible(new_node_id))

        print(f"Added sibling '{new_name}' as child of '{parent_node.text}'")

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
    ):
        """Refresh the entire layout after changes.

        Args:
            skip_measurement: If True, skip _measure_actual_sizes because
                              domain sizes are already correct (e.g., after editing).
            saved_selection_id: Optional node ID to restore selection after refresh
        """
        # Save selected node ID before clearing (if not provided)
        if saved_selection_id is None:
            saved_selection_id = self.selected_node_id

        # Clear scene
        self.scene.clear()
        self.node_items.clear()
        self.edge_items.clear()

        # Step 1: Re-measure actual sizes (unless skipped - e.g., after editing)
        if not skip_measurement:
            self._measure_actual_sizes(self.root_node)

        # Step 2: Re-apply layout, passing selected node to preserve its side
        layout = DefaultLayout(style=self.style_config)
        layout.layout(
            self.root_node,
            canvas_width=1200,
            canvas_height=800,
            focused_node_id=saved_selection_id,
        )

        # Step 3: Recreate UI items
        self._create_ui_items(self.root_node)

        # Restore selection state and focus
        if saved_selection_id:
            if saved_selection_id in self.node_items:
                # Original node still exists, select it
                self._select_node_by_id(saved_selection_id)
                print(f"Restored selection: {saved_selection_id}")
            elif parent_id and parent_id in self.node_items:
                # Original node was deleted, select its parent
                self._select_node_by_id(parent_id)
                print(f"Restored selection to parent: {parent_id}")
            else:
                # Fallback to root
                self._select_node_by_id(self.root_node.id)
                print("Restored selection to root")
            # Ensure view has keyboard focus for keyboard shortcuts
            self.setFocus(Qt.OtherFocusReason)

        print("Layout refreshed")

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

    def showEvent(self, event):  # noqa: N802
        """Handle show event to center on root node initially."""
        super().showEvent(event)

        # Center on root node when first shown
        if hasattr(self, "root_node") and self.root_node.id in self.node_items:
            # Temporarily use center alignment for initial positioning
            original_alignment = self.alignment()
            self.setAlignment(Qt.AlignCenter)
            self.centerOn(self.node_items[self.root_node.id])
            self.setAlignment(original_alignment)

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
                    "Cogist Files (*.mwe);;All Files (*)",
                )

                if not file_path:
                    return

            # Use repository to save
            from cogist.infrastructure.repositories.mindmap_repository import (
                MindMapRepository,
            )

            repository = MindMapRepository()
            repository.save(self.root_node, file_path)

            # Update current file path
            self.current_file_path = file_path

            print(f"✓ Saved to: {file_path}")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save:\n{e}",
            )
            print(f"✗ Save failed: {e}")

    def _open_file(self):
        """Load mind map from file."""
        try:
            # Get file path from user
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Open Mind Map",
                "",
                "Cogist Files (*.mwe);;All Files (*)",
            )

            if not file_path:
                return

            # Use repository to load
            from cogist.infrastructure.repositories.mindmap_repository import (
                MindMapRepository,
            )

            repository = MindMapRepository()
            self.root_node = repository.load(file_path)

            # Update current file path
            self.current_file_path = file_path

            # Refresh UI
            self._refresh_layout()

            # Select root node
            self._select_node_by_id(self.root_node.id)

            print(f"✓ Loaded from: {file_path}")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open:\n{e}",
            )
            print(f"✗ Open failed: {e}")


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)

    # Use macOS native style for proper scrollbar appearance
    app.setStyle("macos")

    # Create and show main window
    window = MainWindow()
    window.setWindowTitle("Cogist")
    window.setGeometry(100, 100, 1400, 900)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
