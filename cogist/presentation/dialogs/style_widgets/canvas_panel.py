"""Canvas panel widget.

Provides controls for customizing canvas background appearance.
Implements lazy initialization for better performance.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton

from .collapsible_panel import CollapsiblePanel
from .color_picker import create_color_picker
from .dialog_utils import position_color_dialog


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
        super().__init__("Background", collapsed=True, parent=parent)

        # Get LABEL_WIDTH from parent (AdvancedStyleTab) if available, otherwise use class default
        self._label_width = getattr(parent, 'LABEL_WIDTH', self.LABEL_WIDTH) if parent else self.LABEL_WIDTH

        # Store reference to AdvancedStyleTab for accessing style_config
        # Note: parent() returns _content_widget, so we need to store the actual parent
        self._advanced_tab = parent

        # State
        self._initialized = False
        self.current_style: dict = {}  # Will be populated by set_style() from global config

        # Color picker (lazy creation)
        self._color_picker = None

        # Connect toggle signal for lazy initialization
        self.toggled.connect(self._on_toggled)

    def _on_toggled(self, checked: bool):
        """Handle expand/collapse events."""
        if checked and not self._initialized:
            self._init_content()
            self._initialized = True
            # Apply saved style to newly created button
            if self.current_style:
                self.set_style(self.current_style)

    def _init_content(self):
        """Initialize content on first expand (lazy initialization)."""
        layout = QGridLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(self.GROUP_MARGIN, 6, self.GROUP_MARGIN, 16)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)

        row = 0

        # Background color
        bg_color_label = QLabel("Color:")
        bg_color_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        bg_color_label.setFixedWidth(self._label_width)
        layout.addWidget(bg_color_label, row, 0)

        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setFixedHeight(self.WIDGET_HEIGHT)
        self.bg_color_btn.clicked.connect(self._on_bg_color_clicked)
        layout.addWidget(self.bg_color_btn, row, 1)
        # Note: Button stylesheet is set by set_style() - no hardcoded colors here
        row += 1

        # Placeholder for future features
        # - Background image
        # - Background texture
        # - Gradient background

        self.setLayout(layout)

    def _emit_style_changed(self):
        """Emit style changed signal."""
        self.style_changed.emit(dict(self.current_style))

    def get_style(self) -> dict:
        """Get current canvas style."""
        return self.current_style.copy()

    def set_style(self, style: dict):
        """Set canvas style programmatically."""
        self.current_style.update(style)

        # Update button background color if button exists
        if hasattr(self, 'bg_color_btn') and "bg_color" in style:
            # Set button background color from style data object
            bg_color = style["bg_color"]
            # Convert #AARRGGBB to rgba() format for Qt (9 chars: # + 8 hex)
            if len(bg_color) == 9 and bg_color.startswith("#"):
                # #AARRGGBB format
                alpha = int(bg_color[1:3], 16)
                red = int(bg_color[3:5], 16)
                green = int(bg_color[5:7], 16)
                blue = int(bg_color[7:9], 16)
                self.bg_color_btn.setStyleSheet(
                    f"background-color: rgba({red}, {green}, {blue}, {alpha});"
                    " border: 1px solid #C8C8C8;"
                    " border-radius: 6px;"
                    " padding: 4px 24px 4px 12px;"
                    " font-size: 13px;"
                    " text-align: left;"
                )

    def _on_bg_color_clicked(self):
        """Handle background color button click."""
        if self._color_picker is None:
            # Get the top-level window to ensure proper dialog lifecycle
            from PySide6.QtCore import Qt
            top_level = self.window() if self.window() else self._advanced_tab
            self._color_picker = create_color_picker(top_level)
            self._color_picker.color_selected.connect(self._on_bg_color_selected)
            # Ensure dialog closes when parent window closes
            self._color_picker.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

            # Reset reference when dialog closes (WA_DeleteOnClose destroys the object)
            self._color_picker.finished.connect(lambda: setattr(self, '_color_picker', None))

        # Get current color from style data object (no fallback)
        # Use stored reference to AdvancedStyleTab instead of parent()
        parent = self._advanced_tab

        if parent and hasattr(parent, 'style_config') and parent.style_config:
            current_color = parent.style_config.special_colors["canvas_bg"]
        else:
            # Should not happen - style_config is required
            return

        # Set current color (MUST call before show!)
        self._color_picker.set_current_color(current_color)

        # Show color picker
        self._color_picker.show()
        self._color_picker.raise_()
        self._color_picker.activateWindow()

        # Position dialog
        position_color_dialog(self._color_picker, self.bg_color_btn)

    def _on_bg_color_selected(self, hex_color: str):
        """Handle color selection from picker."""
        self.current_style["bg_color"] = hex_color

        # Update button color directly (like color pool)
        if hasattr(self, 'bg_color_btn'):
            self.bg_color_btn.setStyleSheet(
                f"background-color: {hex_color}; "
                "border: 1px solid #C8C8C8; "
                "border-radius: 6px; "
                "padding: 4px 24px 4px 12px; "
                "font-size: 13px; "
                "text-align: left;"
            )

        self._emit_style_changed()
