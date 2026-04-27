"""
Style Panel - Configuration Panels (without Activity Bar)

Panels for style configuration:
- Simple: Quick style selection (template and color scheme)
- Advanced: Detailed layer-based template editing

Note: Activity Bar has been moved to the main window level (VSCode-style).
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)

from .style_panel_advanced import AdvancedStyleTab


class StylePanel(QWidget):
    """Style panel content (no activity bar - managed by main window)."""

    PANEL_WIDTH = 260

    def __init__(self, style_config=None, config_manager=None, command_history=None, parent=None):
        super().__init__(parent)
        self.style_config = style_config
        self.config_manager = config_manager
        self.command_history = command_history

        # Set fixed width
        self.setMinimumWidth(self.PANEL_WIDTH)
        self.setMaximumWidth(self.PANEL_WIDTH)

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface with stacked panels."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create simple tab (default)
        self.simple_tab = SimpleStyleTab()
        self.advanced_tab = AdvancedStyleTab(
            style_config=self.style_config,
            config_manager=self.config_manager,
            command_history=self.command_history,
        )

        # Initially show advanced tab
        main_layout.addWidget(self.simple_tab)
        self.current_panel = "simple"

    def switch_panel(self, panel_name: str):
        """Switch between simple and advanced panels."""
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
        if panel_name == "simple":
            layout.addWidget(self.simple_tab)
        elif panel_name == "advanced":
            layout.addWidget(self.advanced_tab)

        self.current_panel = panel_name


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
