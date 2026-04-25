#!/usr/bin/env python3
"""
Cogist - Main Application Entry Point

This is the main demo application showing the four-layer architecture:
- Domain Layer: Node entity + DefaultLayout algorithm
- Presentation Layer: NodeItem, EdgeItem, MindMapView
- Infrastructure Layer: (to be added)
- Application Layer: Command pattern integration
"""

import os
import sys

# Suppress Qt/macOS warnings at the environment level
os.environ["QT_LOGGING_RULES"] = (
    "*.debug=false;qt.scenegraph=false;qt.qpa.keymapper=false;qt.qpa.input=false"
)

from PySide6.QtCore import Qt, qInstallMessageHandler
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QWidget,
)

from cogist.presentation.views.mindmap_view import MindMapView


# Install custom message handler to suppress remaining warnings
def qt_message_handler(_msg_type, _context, message):
    """Suppress Qt/macOS warning messages."""
    msg_str = str(message)
    # Suppress keyboard mapping warnings
    if (
        "qt.qpa.keymapper" in msg_str.lower()
        or "Cocoa" in msg_str
        or "Carbon" in msg_str
    ):
        return
    # Suppress macOS IMKC warnings
    if "IMKC" in msg_str or "mach port" in msg_str.lower():
        return
    # Print other messages to stderr
    sys.stderr.write(f"{msg_str}\n")


# Install the message handler
qInstallMessageHandler(qt_message_handler)


class MainWindow(QMainWindow):
    """Main application window with menu bar."""

    def __init__(self):
        super().__init__()

        # Register this window in the global application context
        from cogist.application.services import get_app_context

        app_context = get_app_context()
        app_context.set_main_window(self)

        # Initialize Application Layer service
        from cogist.application.services import MindMapService

        self.mindmap_service = MindMapService()

        # Initialize style system
        from cogist.domain.styles import templates

        self.current_style = templates.create_default_template()

        # Apply global styles
        self._apply_global_styles()

        # Create mind map view with style configuration and service
        self.mindmap_view = MindMapView(
            style_config=self.current_style, mindmap_service=self.mindmap_service
        )

        # Create Activity Bar (left sidebar)

        from cogist.infrastructure.utils import config_manager
        from cogist.presentation.dialogs.activity_bar import ActivityBar
        from cogist.presentation.dialogs.style_panel import StylePanel

        self.activity_bar = ActivityBar()
        self.activity_bar.setVisible(False)  # Hidden by default
        self.style_panel = StylePanel(
            style_config=self.current_style,
            config_manager=config_manager
        )
        self.style_panel.setVisible(False)  # Hidden by default

        # Create horizontal layout: ActivityBar | StylePanel | MindMapView
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Add activity bar to the left
        main_layout.addWidget(self.activity_bar)

        # Create splitter for style panel and mindmap
        self.content_splitter = QSplitter(Qt.Horizontal)
        self.content_splitter.addWidget(self.style_panel)
        self.content_splitter.addWidget(self.mindmap_view)
        self.content_splitter.setStretchFactor(0, 0)  # Panel has fixed width
        self.content_splitter.setStretchFactor(1, 1)  # Mindmap takes most space
        self.content_splitter.setCollapsible(0, False)  # Panel cannot be collapsed

        # CRITICAL: Set initial splitter handle position to match panel width
        # Without this, QSplitter defaults to evenly splitting, causing a gap
        self.content_splitter.setSizes([StylePanel.PANEL_WIDTH, 1000])

        main_layout.addWidget(self.content_splitter)

        # Set as central widget
        self.setCentralWidget(main_widget)

        # Connect activity bar signals
        self.activity_bar.panel_activated.connect(self._on_panel_activated)

        # Create menu bar and shortcuts on initialization
        self._create_menu_bar()
        self._setup_shortcuts()

    def _on_panel_activated(self, panel_name: str):
        """Handle panel switch from activity bar."""
        if panel_name in ["simple", "advanced"]:
            # Show style panel
            self.style_panel.setVisible(True)
            # Switch to the selected mode
            self.style_panel.switch_panel(panel_name)
        else:
            # Hide style panel
            self.style_panel.setVisible(False)

        # Enable document mode to reduce decorations
        self.setDocumentMode(True)

        # Disable dock nesting and animated docks
        self.setDockNestingEnabled(False)

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
                padding: 18px 0 0 0;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                left: 10px;
                top: 0px;
                padding: 0 8px;
                background-color: transparent;
            }

            /* Separator between dock widget and main area */
            QSplitter::handle {
                background-color: transparent;
                width: 0;
            }
            QSplitter::handle:horizontal {
                width: 0;
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

        # Clear existing menus to prevent duplicates
        menubar.clear()

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

        # Save as Template
        save_template_action = QAction("Save as &Template...", self)
        save_template_action.triggered.connect(self._save_as_template)
        file_menu.addAction(save_template_action)

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
        self.add_sibling_action.setShortcut("Space")
        self.add_sibling_action.triggered.connect(self._add_sibling)
        edit_menu.addAction(self.add_sibling_action)

        # Edit Node
        edit_action = QAction("&Edit Node", self)
        edit_action.setShortcut("Return")
        edit_action.triggered.connect(self._edit_selected_node)
        edit_menu.addAction(edit_action)

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

        # Toggle Style Panel
        toggle_style_panel_action = QAction("Toggle Style &Panel", self)
        toggle_style_panel_action.setShortcut("Ctrl+Shift+S")
        toggle_style_panel_action.setCheckable(True)
        toggle_style_panel_action.triggered.connect(self._toggle_style_panel)
        view_menu.addAction(toggle_style_panel_action)

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

    def _save_as_template(self):
        """Save current style as a template."""
        from cogist.infrastructure.utils import config_manager

        if not config_manager:
            print("Warning: config_manager not available, cannot save template")
            return

        # Show dialog to get template name
        from PySide6.QtWidgets import QInputDialog

        template_name, ok = QInputDialog.getText(
            self,
            "Save as Template",
            "Enter template name:",
            text="My Custom Template"
        )

        if not ok or not template_name.strip():
            return

        template_name = template_name.strip()

        try:
            # Get template directory
            template_dir = config_manager.get_template_directory()

            # Serialize all style data into a single file
            import json

            from cogist.domain.styles import (
                serialize_color_scheme,
                serialize_style,
                serialize_template,
            )

            # Build complete template data structure (same as CGS format)
            template_data = {
                "name": template_name,
                "description": f"Custom template: {template_name}",
            }

            # Add MindMapStyle config (spacing, connectors, etc.)
            if self.current_style:
                style_config_data = serialize_style(self.current_style)
                template_data["style_config"] = style_config_data

            # Add Template (node styles)
            if self.current_style.resolved_template:
                template_obj_data = serialize_template(self.current_style.resolved_template)
                template_data["template"] = template_obj_data

            # Add ColorScheme (colors)
            if self.current_style.resolved_color_scheme:
                color_scheme_data = serialize_color_scheme(self.current_style.resolved_color_scheme)
                template_data["color_scheme"] = color_scheme_data

            # Save as single JSON file
            template_file = template_dir / f"{template_name}.json"
            template_file.write_text(json.dumps(template_data, indent=2, ensure_ascii=False))
            print(f"Template saved to: {template_file}")

            # Show success message
            QMessageBox.information(
                self,
                "Success",
                f"Template '{template_name}' saved successfully!\n\nLocation: {template_dir}\nFile: {template_name}.json"
            )

        except Exception as e:
            print(f"Error saving template: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save template:\n{str(e)}"
            )

    def _new_file(self):
        """Create a new mind map."""
        # CRITICAL: Check for unsaved changes
        if self.mindmap_service.is_modified():
            # Check if current mind map has any content (not just root node)
            has_content = (
                self.mindmap_view.root_node and
                len(self.mindmap_view.root_node.children) > 0
            )

            if has_content:
                reply = QMessageBox.warning(
                    self,
                    "Unsaved Changes",
                    "The current mind map has unsaved changes.\n\nDo you want to save before creating a new mind map?",
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                    QMessageBox.Save,
                )

                if reply == QMessageBox.Save:
                    # Save current file first
                    self.mindmap_view._save_file()
                    # If save was cancelled, abort
                    if self.mindmap_service.is_modified():
                        return
                elif reply == QMessageBox.Discard:
                    pass  # Discard changes, continue
                else:
                    return  # Cancelled, abort

        # Reinitialize the mind map view (same as __init__)
        self.mindmap_view._initialize_new_mindmap()

    def _undo(self):
        """Undo the last operation."""
        # Check what type of command we're undoing
        last_command = (
            self.mindmap_service.node_service.command_history.peek_last_undo_command()
        )
        is_add_node_command = (
            last_command and type(last_command).__name__ == "AddNodeCommand"
        )

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

        # If undoing an add command, save focus info BEFORE undo
        undo_delete_focus_id = None
        if (
            is_add_node_command
            and last_command is not None
            and hasattr(last_command, "new_node")
            and last_command.new_node
        ):
            node_to_delete = last_command.new_node
            parent_node = node_to_delete.parent

            if parent_node:
                # Calculate which sibling to focus on after deletion (before undo removes the node)
                undo_delete_focus_id = (
                    self.mindmap_view._calculate_next_focus_after_deletion(
                        node_to_delete, parent_node
                    )
                )

        # Use MindMapService to undo (Application Layer)
        if self.mindmap_service.undo():
            # OPTIMIZATION: Undo restores old dimensions, no need to re-measure
            self.mindmap_view._refresh_layout(
                skip_measurement=True,
                saved_selection_id=node_id_before_undo,
                parent_id=parent_id_before_undo,
            )

            # Scroll to appropriate node based on command type
            if is_add_node_command and undo_delete_focus_id:
                # Undoing an add = deleting the added node
                # Focus follows normal deletion logic: previous sibling > next sibling > parent
                if undo_delete_focus_id in self.mindmap_view.node_items:
                    # Clear all selections first
                    for item in self.mindmap_view.node_items.values():
                        item.setSelected(False)

                    self.mindmap_view.selected_node_id = undo_delete_focus_id
                    selected_item = self.mindmap_view.node_items[undo_delete_focus_id]
                    selected_item.setSelected(True)
                    self.mindmap_view.centerOn(selected_item)
            elif (
                self.mindmap_view.selected_node_id
                and self.mindmap_view.selected_node_id in self.mindmap_view.node_items
            ):
                # Normal undo (e.g., undoing a delete), focus stays on current selection
                selected_item = self.mindmap_view.node_items[
                    self.mindmap_view.selected_node_id
                ]
                self.mindmap_view.centerOn(selected_item)

    def _redo(self):
        """Redo the last undone operation."""
        # Check what type of command we're redoing
        last_command = (
            self.mindmap_service.node_service.command_history.peek_last_redo_command()
        )
        is_add_node_command = (
            last_command and type(last_command).__name__ == "AddNodeCommand"
        )

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

        # Use MindMapService to redo (Application Layer)
        if self.mindmap_service.redo():
            # OPTIMIZATION: Redo may need measurement for text changes
            # For now, use skip_measurement=True (commands should restore dimensions)
            self.mindmap_view._refresh_layout(
                skip_measurement=True,
                saved_selection_id=node_id_before_redo,
                parent_id=parent_id_before_redo,
            )

            # Scroll to appropriate node based on command type
            if (
                is_add_node_command
                and last_command is not None
                and hasattr(last_command, "new_node")
                and last_command.new_node
            ):
                # Redoing an add = adding a new node again, focus on the added node
                self.mindmap_view._focus_on_node_after_addition(
                    last_command.new_node.id
                )
            elif (
                self.mindmap_view.selected_node_id
                and self.mindmap_view.selected_node_id in self.mindmap_view.node_items
            ):
                # Normal redo (e.g., redoing a delete), focus stays on current selection
                selected_item = self.mindmap_view.node_items[
                    self.mindmap_view.selected_node_id
                ]
                self.mindmap_view.centerOn(selected_item)

    def _add_child(self):
        """Add a child node."""
        if self.mindmap_view.selected_node_id:
            self.mindmap_view._add_selected_child()

    def _add_sibling(self):
        """Add a sibling node."""
        if self.mindmap_view.selected_node_id:
            self.mindmap_view._add_sibling_node()

    def _edit_selected_node(self):
        """Edit the selected node text."""
        if self.mindmap_view.selected_node_id:
            self.mindmap_view._edit_selected_node()

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

    def _setup_shortcuts(self):
        """Setup global keyboard shortcuts."""
        self.toggle_style_shortcut = QShortcut(QKeySequence("Ctrl+Shift+S"), self)
        self.toggle_style_shortcut.activated.connect(self._toggle_style_panel)

    def _toggle_style_panel(self):
        """Toggle style panel visibility."""
        is_visible = self.style_panel.isVisible()
        self.style_panel.setVisible(not is_visible)
        self.activity_bar.setVisible(not is_visible)

        # Update activity bar button state
        if not is_visible:
            # If showing, activate advanced mode by default
            self.activity_bar.activate_panel("advanced")
        else:
            # If hiding, uncheck all buttons
            for btn in self.activity_bar.buttons.values():
                btn.setChecked(False)

    def _open_style_panel(self):
        """Open the style panel via activity bar."""
        # Activate the advanced mode button by default
        self.activity_bar.activate_panel("advanced")


def main():
    """Main entry point for the application."""
    from PySide6.QtWidgets import QApplication

    # Set application name for macOS menu bar
    app = QApplication(sys.argv)
    app.setApplicationName("Cogist")
    app.setApplicationDisplayName("Cogist")

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
