"""
Style Panel - Dual Mode (Simple & Advanced)

A dockable panel with tabbed interface for style configuration:
- Simple Mode: Quick selection of layout, template, color scheme, and priority
- Advanced Mode: Detailed layer-based template editing
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)


class StylePanel(QWidget):
    """Main style panel with tabbed interface for simple and advanced modes."""

    PANEL_WIDTH = 280

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
    """Simple mode tab for quick style selection."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize simple mode UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        # === Layout Algorithm Selection ===
        layout_group = QGroupBox("📐 布局算法")
        layout_grid = QVBoxLayout()
        layout_grid.setSpacing(6)

        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["Default", "Tree", "Radial"])
        self.layout_combo.currentTextChanged.connect(self._on_layout_changed)
        layout_grid.addWidget(self.layout_combo)

        layout_group.setLayout(layout_grid)
        layout.addWidget(layout_group)

        # === Node Template Selection ===
        template_group = QGroupBox("🎨 节点模板")
        template_grid = QVBoxLayout()
        template_grid.setSpacing(6)

        self.template_combo = QComboBox()
        self.template_combo.addItems(["Modern", "Minimal", "Colorful", "Professional"])
        self.template_combo.currentTextChanged.connect(self._on_template_changed)
        template_grid.addWidget(self.template_combo)

        template_group.setLayout(template_grid)
        layout.addWidget(template_group)

        # === Color Scheme Selection ===
        color_group = QGroupBox("🎨 配色方案")
        color_grid = QVBoxLayout()
        color_grid.setSpacing(6)

        self.color_combo = QComboBox()
        self.color_combo.addItems(["Blue", "Dark", "Warm", "Cool"])
        self.color_combo.currentTextChanged.connect(self._on_color_changed)
        color_grid.addWidget(self.color_combo)

        color_group.setLayout(color_grid)
        layout.addWidget(color_group)

        # === Priority Selection ===
        priority_group = QGroupBox("⚡ 选中节点优先级")
        priority_layout = QVBoxLayout()
        priority_layout.setSpacing(8)

        # Radio buttons for priority
        self.priority_group_btn = QButtonGroup(self)
        priority_radio_layout = QHBoxLayout()
        priority_radio_layout.setSpacing(12)

        self.critical_radio = QRadioButton("关键")
        self.normal_radio = QRadioButton("普通")
        self.minor_radio = QRadioButton("次要")

        self.normal_radio.setChecked(True)  # Default to normal

        self.priority_group_btn.addButton(self.critical_radio, 0)
        self.priority_group_btn.addButton(self.normal_radio, 1)
        self.priority_group_btn.addButton(self.minor_radio, 2)

        priority_radio_layout.addWidget(self.critical_radio)
        priority_radio_layout.addWidget(self.normal_radio)
        priority_radio_layout.addWidget(self.minor_radio)
        priority_radio_layout.addStretch()

        priority_layout.addLayout(priority_radio_layout)

        # Apply button
        apply_btn = QPushButton("应用到选中节点")
        apply_btn.clicked.connect(self._apply_priority)
        priority_layout.addWidget(apply_btn)

        priority_group.setLayout(priority_layout)
        layout.addWidget(priority_group)

        layout.addStretch()

    def _on_layout_changed(self, layout_name: str):
        """Handle layout algorithm change."""
        print(f"Layout changed to: {layout_name}")
        # TODO: Implement layout switching logic

    def _on_template_changed(self, template_name: str):
        """Handle template change."""
        print(f"Template changed to: {template_name}")
        # TODO: Implement template switching logic

    def _on_color_changed(self, color_name: str):
        """Handle color scheme change."""
        print(f"Color scheme changed to: {color_name}")
        # TODO: Implement color scheme switching logic

    def _apply_priority(self):
        """Apply priority to selected node."""
        if self.critical_radio.isChecked():
            priority = "critical"
        elif self.minor_radio.isChecked():
            priority = "minor"
        else:
            priority = "normal"

        print(f"Applying priority: {priority}")
        # TODO: Implement priority application logic


class AdvancedStyleTab(QWidget):
    """Advanced mode tab for detailed template editing."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize advanced mode UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(12, 12, 12, 12)

        # Placeholder message
        placeholder = QLabel("高级模式正在开发中...\n\n将支持：\n• 基于层级编辑模板\n• 基于分支定制样式\n• 保存为自定义模板")
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
