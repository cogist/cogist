"""
Style Panel - Configuration Panels (without Activity Bar)

Panels for style configuration:
- Simple: Quick style selection (template and color scheme)
- Advanced: Detailed layer-based template editing

Note: Activity Bar has been moved to the main window level (VSCode-style).
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from cogist.domain.styles import COLOR_SCHEMES, NODE_TEMPLATES

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
    """Simple mode tab for quick style selection.

    Provides template and color scheme selection for quick styling.
    """

    style_changed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        """Initialize simple mode UI."""
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

        # Template selector
        template_label = QLabel("Template:")
        template_label.setStyleSheet("QLabel { font-size: 12px; color: #666666; }")
        layout.addWidget(template_label)

        self.template_combo = QComboBox()
        self.template_combo.setFixedHeight(32)
        for key, template in NODE_TEMPLATES.items():
            self.template_combo.addItem(template.name, key)
        self.template_combo.currentIndexChanged.connect(self._on_template_changed)
        layout.addWidget(self.template_combo)

        # Template description
        self.template_desc_label = QLabel()
        self.template_desc_label.setWordWrap(True)
        self.template_desc_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #888888;
                padding-bottom: 12px;
            }
        """)
        layout.addWidget(self.template_desc_label)

        layout.addSpacing(8)

        # Color scheme selector
        colorscheme_label = QLabel("Color Scheme:")
        colorscheme_label.setStyleSheet("QLabel { font-size: 12px; color: #666666; }")
        layout.addWidget(colorscheme_label)

        self.colorscheme_combo = QComboBox()
        self.colorscheme_combo.setFixedHeight(32)
        for key, scheme in COLOR_SCHEMES.items():
            self.colorscheme_combo.addItem(scheme.name, key)
        self.colorscheme_combo.currentIndexChanged.connect(self._on_colorscheme_changed)
        layout.addWidget(self.colorscheme_combo)

        # Color scheme description
        self.colorscheme_desc_label = QLabel()
        self.colorscheme_desc_label.setWordWrap(True)
        self.colorscheme_desc_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #888888;
                padding-bottom: 12px;
            }
        """)
        layout.addWidget(self.colorscheme_desc_label)

        layout.addSpacing(8)

        # Rainbow branches toggle
        self.rainbow_checkbox = QCheckBox("Rainbow Branches")
        self.rainbow_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 12px;
                color: #333333;
                padding: 8px 0;
            }
        """)
        self.rainbow_checkbox.stateChanged.connect(self._on_rainbow_changed)
        layout.addWidget(self.rainbow_checkbox)

        # Color scheme preview
        preview_label = QLabel("Preview:")
        preview_label.setStyleSheet("QLabel { font-size: 12px; color: #666666; padding-top: 8px; }")
        layout.addWidget(preview_label)

        self.preview_widget = QWidget()
        self.preview_widget.setFixedHeight(80)
        self.preview_widget.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border: 1px solid #DDDDDD;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.preview_widget)

        layout.addStretch()

        # Initialize with first template and color scheme
        self._update_template_description()
        self._update_colorscheme_description()
        self._update_preview()

    def _on_template_changed(self, _index):
        """Handle template selection change."""
        self._update_template_description()
        self._update_preview()
        self._emit_style_changed()

    def _on_colorscheme_changed(self, _index):
        """Handle color scheme selection change."""
        self._update_colorscheme_description()
        self._update_preview()
        self._emit_style_changed()

    def _on_rainbow_changed(self, _state):
        """Handle rainbow branches toggle."""
        self._update_preview()
        self._emit_style_changed()

    def _update_template_description(self):
        """Update template description label."""
        key = self.template_combo.currentData()
        if key and key in NODE_TEMPLATES:
            template = NODE_TEMPLATES[key]
            self.template_desc_label.setText(template.description)

    def _update_colorscheme_description(self):
        """Update color scheme description label."""
        key = self.colorscheme_combo.currentData()
        if key and key in COLOR_SCHEMES:
            scheme = COLOR_SCHEMES[key]
            self.colorscheme_desc_label.setText(scheme.description)

    def _update_preview(self):
        """Update color scheme preview."""
        scheme_key = self.colorscheme_combo.currentData()
        if scheme_key and scheme_key in COLOR_SCHEMES:
            scheme = COLOR_SCHEMES[scheme_key]
            bg_color = scheme.canvas_bg_color
            edge_color = scheme.edge_color
            self.preview_widget.setStyleSheet(f"""
                QWidget {{
                    background-color: {bg_color};
                    border: 2px solid {edge_color};
                    border-radius: 8px;
                }}
            """)

    def _emit_style_changed(self):
        """Emit style changed signal with current settings."""
        template_key = self.template_combo.currentData()
        scheme_key = self.colorscheme_combo.currentData()
        use_rainbow = self.rainbow_checkbox.isChecked()

        self.style_changed.emit({
            "template_name": template_key,
            "color_scheme_name": scheme_key,
            "use_rainbow_branches": use_rainbow,
        })
