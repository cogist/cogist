"""Canvas panel widget.

Provides controls for customizing canvas background appearance.
Implements lazy initialization for better performance.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QGridLayout, QLabel

from .collapsible_panel import CollapsiblePanel
from .menu_button import MenuButton


class CanvasPanel(CollapsiblePanel):
    """Canvas background settings with lazy initialization.

    Signals:
        style_changed(dict): Emitted when canvas style changes
    """

    style_changed = Signal(dict)

    # UI constants (fallback value, will use parent's LABEL_WIDTH if available)
    LABEL_WIDTH = 90
    WIDGET_HEIGHT = 32
    GROUP_MARGIN = 10

    def __init__(self, parent=None):
        super().__init__("Canvas", collapsed=True, parent=parent)

        # Get LABEL_WIDTH from parent (AdvancedStyleTab) if available, otherwise use class default
        self._label_width = getattr(parent, 'LABEL_WIDTH', self.LABEL_WIDTH) if parent else self.LABEL_WIDTH

        # State
        self._initialized = False
        self.current_style = {
            "bg_color": "#FFFFFFFF",  # Default canvas background color
        }

        # Connect toggle signal for lazy initialization
        self.toggled.connect(self._on_toggled)

    def _on_toggled(self, checked: bool):
        """Handle expand/collapse events."""
        if checked and not self._initialized:
            self._init_content()
            self._initialized = True

    def _init_content(self):
        """Initialize content on first expand (lazy initialization)."""
        layout = QGridLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(self.GROUP_MARGIN, 6, self.GROUP_MARGIN, 16)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)

        row = 0

        # Background color
        bg_color_label = QLabel("Background:")
        bg_color_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        bg_color_label.setFixedWidth(self._label_width)
        layout.addWidget(bg_color_label, row, 0)

        # Placeholder button - will be implemented later
        self.bg_color_btn = MenuButton("White", self.WIDGET_HEIGHT)
        self.bg_color_btn.setStyleSheet(self._button_style())
        # TODO: Connect to color picker dialog
        layout.addWidget(self.bg_color_btn, row, 1)
        row += 1

        # Placeholder for future features
        # - Background image
        # - Background texture
        # - Gradient background

        self.setLayout(layout)

    def _button_style(self) -> str:
        """Get standard button stylesheet."""
        return """
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #C8C8C8;
                border-radius: 6px;
                padding: 4px 24px 4px 12px;
                font-size: 13px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
                border-color: #A0A0A0;
            }
            QPushButton::menu-indicator {
                image: none;
                width: 0;
                height: 0;
            }
        """

    def _emit_style_changed(self):
        """Emit style changed signal."""
        self.style_changed.emit(dict(self.current_style))

    def get_style(self) -> dict:
        """Get current canvas style."""
        return self.current_style.copy()

    def set_style(self, style: dict):
        """Set canvas style programmatically."""
        self.current_style.update(style)

        # Update UI if initialized
        if self._initialized and "bg_color" in style:
            # TODO: Update button text based on color
            pass
