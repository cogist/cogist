"""
Style Panel - Dual Mode (Simple & Advanced)

A dockable panel with tabbed interface for style configuration:
- Simple Mode: Quick selection of layout, template, color scheme, and priority (TODO)
- Advanced Mode: Detailed layer-based template editing
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .style_panel_advanced import AdvancedStyleTab


class StylePanel(QWidget):
    """Main style panel with tabbed interface for simple and advanced modes."""

    PANEL_WIDTH = 260  # Match AdvancedStyleTab width

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set fixed width
        self.setMinimumWidth(self.PANEL_WIDTH)
        self.setMaximumWidth(self.PANEL_WIDTH)

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface with tabs."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)  # Cleaner appearance
        self.tab_widget.setTabPosition(QTabWidget.North)

        # Create tabs
        self.simple_tab = SimpleStyleTab()
        self.advanced_tab = AdvancedStyleTab()

        self.tab_widget.addTab(self.simple_tab, "简单")
        self.tab_widget.addTab(self.advanced_tab, "高级")

        main_layout.addWidget(self.tab_widget)


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
