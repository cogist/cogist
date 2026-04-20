"""
Style Panel - Configuration Panels (without Activity Bar)

Panels for style configuration:
- Simple: Quick style selection (TODO)
- Advanced: Detailed layer-based template editing

Note: Activity Bar has been moved to the main window level (VSCode-style).
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QVBoxLayout,
    QWidget,
)

from .style_panel_advanced import AdvancedStyleTab


class StylePanel(QWidget):
    """Style panel content (no activity bar - managed by main window)."""

    PANEL_WIDTH = 260

    def __init__(self, parent=None):
        super().__init__(parent)

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
        self.advanced_tab = AdvancedStyleTab()

        # Initially show advanced tab
        main_layout.addWidget(self.advanced_tab)
        self.current_panel = "advanced"

    def switch_panel(self, panel_name: str):
        """Switch between simple and advanced panels."""
        if panel_name == self.current_panel:
            return

        layout = self.layout()
        # Remove current widget
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)

        # Add new panel
        if panel_name == "simple":
            layout.addWidget(self.simple_tab)
        elif panel_name == "advanced":
            layout.addWidget(self.advanced_tab)

        self.current_panel = panel_name


class SimpleStyleTab(QWidget):
    """Simple mode tab for quick style selection (TODO - requires Template/ColorScheme Registry)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize simple mode UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        # Placeholder message
        placeholder = QLabel("简单模式正在开发中...\n\n需要完成：\n• 模板注册表 (Template Registry)\n• 配色方案注册表 (ColorScheme Registry)\n• 布局算法注册表 (Layout Registry)")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 13px;
                padding: 40px 20px;
            }
        """)
        layout.addWidget(placeholder)

        layout.addStretch()
