"""
Style Panel - Configuration Panels (without Activity Bar)

Panels for style configuration:
- Simple: Quick style selection (template and color scheme)
- Advanced: Detailed layer-based template editing

Note: Activity Bar has been moved to the main window level (VSCode-style).
"""

from qtpy.QtCore import Signal
from qtpy.QtWidgets import (
    QApplication,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from .style_panel_advanced import AdvancedStyleTab
from .style_panel_color import ColorSchemeTab


class StylePanel(QWidget):
    """Style panel content (no activity bar - managed by main window)."""

    PANEL_WIDTH = 260

    def __init__(self, style_config=None, config_manager=None, command_history=None, parent=None):
        super().__init__(parent)
        self.style_config = style_config
        self.config_manager = config_manager
        self.command_history = command_history

        # Track previously selected node ID for focus restoration
        self._previous_selected_node_id = None

        # Set fixed width
        self.setMinimumWidth(self.PANEL_WIDTH)
        self.setMaximumWidth(self.PANEL_WIDTH)

        self._init_ui()

        # Connect to global focus change signal
        QApplication.instance().focusChanged.connect(self._on_focus_changed)

    def _init_ui(self):
        """Initialize the user interface with stacked panels."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create tabs
        self.color_scheme_tab = ColorSchemeTab(style_config=self.style_config)
        self.advanced_tab = AdvancedStyleTab(
            style_config=self.style_config,
            config_manager=self.config_manager,
            command_history=self.command_history,
        )

        # Initially show color scheme tab (first)
        main_layout.addWidget(self.color_scheme_tab)
        self.current_panel = "color_scheme"

    def switch_panel(self, panel_name: str):
        """Switch between color scheme and advanced panels."""
        if panel_name == self.current_panel:
            return

        layout = self.layout()
        if not layout:
            return

        # Remove current widget
        while layout.count():
            child = layout.takeAt(0)
            widget = child.widget() if child else None
            if widget:
                widget.setParent(None)

        # Add new panel
        if panel_name == "color_scheme":
            layout.addWidget(self.color_scheme_tab)
        elif panel_name == "advanced":
            layout.addWidget(self.advanced_tab)

        self.current_panel = panel_name

    def _on_focus_changed(self, old: QWidget, now: QWidget):
        """Handle global focus changes."""
        if now is None:
            return

        # Check if the new focus widget is inside this panel
        if self.isAncestorOf(now) or now == self:
            # Panel gained focus - save current node selection
            parent = self.parent()
            while parent and not hasattr(parent, 'mindmap_view'):
                parent = parent.parent()

            if parent and hasattr(parent, 'mindmap_view'):
                view = parent.mindmap_view
                # Only save if we don't already have a saved state
                if self._previous_selected_node_id is None:
                    self._previous_selected_node_id = view.selected_node_id
        else:
            # Focus moved outside panel - check if it was previously inside
            if self._previous_selected_node_id is not None and old and (self.isAncestorOf(old) or old == self):
                parent = self.parent()
                while parent and not hasattr(parent, 'mindmap_view'):
                    parent = parent.parent()

                if parent and hasattr(parent, 'mindmap_view'):
                    view = parent.mindmap_view
                    # Restore the previously selected node if it still exists
                    if self._previous_selected_node_id in view.node_items:
                        view._select_node_by_id(self._previous_selected_node_id)
                    # Clear the saved state
                    self._previous_selected_node_id = None


class SimpleStyleTab(QWidget):
    """Simple mode tab - placeholder for future template selection feature.

    Note: This tab is currently disabled. Use Advanced mode for style editing.
    Template and color scheme selection will be implemented when template files are available.
    """

    style_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize simple mode UI with placeholder message."""
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)

        # Title
        title = QLabel("Quick Style")
        title.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #333333;
                padding-bottom: 8px;
            }
        """)
        layout.addWidget(title)

        # Placeholder message
        message = QLabel(
            "Template selection will be available in a future version.\n\n"
            "Please use Advanced mode to edit styles."
        )
        message.setWordWrap(True)
        message.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #888888;
                padding: 16px;
            }
        """)
        layout.addWidget(message)

        layout.addStretch()
