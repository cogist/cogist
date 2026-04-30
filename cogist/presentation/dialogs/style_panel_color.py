"""Color Scheme Panel - Global color pool and rainbow mode configuration."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QVBoxLayout,
    QWidget,
)

from .style_widgets.color_scheme_section import ColorSchemeSection


class ColorSchemeTab(QWidget):
    """Tab for managing global color scheme (color pool and rainbow mode)."""

    style_changed = Signal(dict)

    def __init__(self, style_config=None, parent=None):
        super().__init__(parent)
        self.style_config = style_config
        self._init_ui()

    def _init_ui(self):
        """Initialize the color scheme panel UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create scroll area
        from PySide6.QtWidgets import QScrollArea

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #F0F0F0;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #C0C0C0;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #A0A0A0;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)  # No spacing between collapsible panels

        # Color Scheme Section (global color pool and rainbow mode)
        self.color_scheme_section = ColorSchemeSection()
        content_layout.addWidget(self.color_scheme_section)

        content_layout.addStretch()

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

        # Connect signals
        self.color_scheme_section.color_changed.connect(self._on_style_changed)

        # Apply custom styles
        self._apply_styles()

        # Initialize color scheme section with current config (if available)
        # This will be saved as pending if panel not yet expanded
        if self.style_config:
            self.set_style_config(self.style_config)

    def _apply_styles(self):
        """Apply custom QSS styles to the panel."""
        self.setStyleSheet("""
            ColorSchemeTab {
                background-color: #F5F5F5;
            }
        """)

    def _on_style_changed(self, style: dict):
        """Handle style changes from color scheme section."""
        self.style_changed.emit(style)

    def set_style_config(self, style_config):
        """Set the style configuration."""
        self.style_config = style_config
        # Initialize color scheme section with current config
        if style_config:
            color_style = {
                "use_rainbow_branches": getattr(style_config, 'use_rainbow_branches', False),
                "branch_colors": getattr(style_config, 'branch_colors', []),
            }
            print(f"[ColorSchemeTab] Setting style: {len(color_style['branch_colors'])} colors")
            if color_style['branch_colors']:
                print(f"  First 3 colors: {color_style['branch_colors'][:3]}")
            self.color_scheme_section.set_style(color_style)
