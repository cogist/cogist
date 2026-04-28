"""Color scheme section widget.

Centralized color management for:
- Background color (from Node Style)
- Text/Foreground color (from Node Style)
- Border color (from Border Section)
- Connector color (from Connector Section)
- Canvas background

This section is Part of Presentation Layer (UI).
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog,
    QGridLayout,
    QLabel,
    QPushButton,
)

from .collapsible_panel import CollapsiblePanel


def position_color_dialog(dialog: QColorDialog, button: QPushButton):
    """Position color dialog next to the button with boundary checks.

    Args:
        dialog: The QColorDialog to position
        button: The button to position relative to
    """
    button_rect = button.rect()
    global_pos = button.mapToGlobal(button_rect.bottomLeft())

    dialog_width = dialog.width()
    dialog_height = dialog.height()
    screen = button.screen().availableGeometry()

    x = global_pos.x()
    y = global_pos.y()

    # Boundary checks
    if x + dialog_width > screen.right():
        x = screen.right() - dialog_width
    if y + dialog_height > screen.bottom():
        y = screen.bottom() - dialog_height
    if x < screen.left():
        x = screen.left()
    if y < screen.top():
        y = screen.top()

    dialog.move(x, y)


class ColorSchemeSection(CollapsiblePanel):
    """Color scheme settings section.

    Signals:
        color_changed(dict): Emitted when color properties change
    """

    color_changed = Signal(dict)

    # UI constants
    LABEL_WIDTH = 75
    WIDGET_HEIGHT = 32
    GROUP_MARGIN = 10

    def __init__(self, parent=None):
        super().__init__("Color Scheme", collapsed=True, parent=parent)

        self._initialized = False
        self.current_role = None

        # Default colors
        self._default_colors = {
            "bg_color": "#2196F3",
            "text_color": "#FFFFFF",
            "border_color": "#1976D2",
            "connector_color": "#1565C0",
            "canvas_bg": "#FFFFFF",
        }

        # Color button references
        self.bg_color_btn: QPushButton | None = None
        self.text_color_btn: QPushButton | None = None
        self.border_color_btn: QPushButton | None = None
        self.conn_color_btn: QPushButton | None = None
        self.canvas_picker: QPushButton | None = None

        # Label references for visibility control
        self.bg_label: QLabel | None = None
        self.text_label: QLabel | None = None
        self.border_label: QLabel | None = None
        self.conn_label: QLabel | None = None
        self.canvas_label: QLabel | None = None

        self.toggled.connect(self._on_toggled)

    def _on_toggled(self, expanded: bool):
        """Handle panel expand/collapse."""
        if expanded and not self._initialized:
            self._initialized = True  # Set before _init_content so set_role works
            self._init_content()

    def _init_content(self):
        """Initialize content on first expand."""
        layout = QGridLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(self.GROUP_MARGIN, 16, self.GROUP_MARGIN, 16)
        layout.setColumnStretch(0, 0)  # Label column - fixed width
        layout.setColumnStretch(1, 1)  # Color picker column - stretchable

        row = 0

        # Background color
        self.bg_label = QLabel("Background:")
        self.bg_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.bg_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(self.bg_label, row, 0)

        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setFixedHeight(self.WIDGET_HEIGHT)
        self.bg_color_btn.setStyleSheet(
            f"background-color: {self._default_colors['bg_color']}; "
            "border: 1px solid #ccc; border-radius: 6px;"
        )
        self.bg_color_btn.clicked.connect(lambda: self._pick_color("bg_color"))
        layout.addWidget(self.bg_color_btn, row, 1)
        row += 1

        # Text/Foreground color
        self.text_label = QLabel("Text Color:")
        self.text_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.text_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(self.text_label, row, 0)

        self.text_color_btn = QPushButton()
        self.text_color_btn.setFixedHeight(self.WIDGET_HEIGHT)
        self.text_color_btn.setStyleSheet(
            f"background-color: {self._default_colors['text_color']}; "
            "border: 1px solid #ccc; border-radius: 6px;"
        )
        self.text_color_btn.clicked.connect(lambda: self._pick_color("text_color"))
        layout.addWidget(self.text_color_btn, row, 1)
        row += 1

        # Border color
        self.border_label = QLabel("Border:")
        self.border_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.border_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(self.border_label, row, 0)

        self.border_color_btn = QPushButton()
        self.border_color_btn.setFixedHeight(self.WIDGET_HEIGHT)
        self.border_color_btn.setStyleSheet(
            f"background-color: {self._default_colors['border_color']}; "
            "border: 1px solid #ccc; border-radius: 6px;"
        )
        self.border_color_btn.clicked.connect(lambda: self._pick_color("border_color"))
        layout.addWidget(self.border_color_btn, row, 1)
        row += 1

        # Connector color
        self.conn_label = QLabel("Connector:")
        self.conn_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.conn_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(self.conn_label, row, 0)

        self.conn_color_btn = QPushButton()
        self.conn_color_btn.setFixedHeight(self.WIDGET_HEIGHT)
        self.conn_color_btn.setStyleSheet(
            f"background-color: {self._default_colors['connector_color']}; "
            "border: 1px solid #ccc; border-radius: 6px;"
        )
        self.conn_color_btn.clicked.connect(lambda: self._pick_color("connector_color"))
        layout.addWidget(self.conn_color_btn, row, 1)
        row += 1

        # Canvas background (show only when Layer is canvas)
        self.canvas_label = QLabel("Canvas:")
        self.canvas_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.canvas_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(self.canvas_label, row, 0)

        self.canvas_picker = QPushButton()
        self.canvas_picker.setFixedHeight(self.WIDGET_HEIGHT)
        self.canvas_picker.setStyleSheet(
            "background-color: #FFFFFF; "
            "border: 1px solid #ccc; border-radius: 6px;"
        )
        self.canvas_picker.clicked.connect(lambda: self._pick_color("canvas_bg"))
        layout.addWidget(self.canvas_picker, row, 1)

        self.setLayout(layout)

        # Apply current role visibility after content is created
        if self.current_role:
            self.set_role(self.current_role)

    def set_role(self, role: str):
        """Set current role and update visibility.

        Args:
            role: Layer role (root, level_1, level_2, level_3_plus, canvas)
        """
        self.current_role = role

        # If not initialized yet, just store the role - visibility will be set in _init_content
        if not self._initialized:
            return

        self._apply_role_visibility()

    def _apply_role_visibility(self):
        """Apply visibility settings based on current role."""
        if not self._initialized:
            return

        is_canvas = self.current_role == "canvas"

        # Node colors (bg, text, border) - hide for canvas
        if self.bg_label:
            self.bg_label.setVisible(not is_canvas)
        if self.bg_color_btn:
            self.bg_color_btn.setVisible(not is_canvas)
        if self.text_label:
            self.text_label.setVisible(not is_canvas)
        if self.text_color_btn:
            self.text_color_btn.setVisible(not is_canvas)
        if self.border_label:
            self.border_label.setVisible(not is_canvas)
        if self.border_color_btn:
            self.border_color_btn.setVisible(not is_canvas)

        # Connector color - hide for canvas
        if self.conn_label:
            self.conn_label.setVisible(not is_canvas)
        if self.conn_color_btn:
            self.conn_color_btn.setVisible(not is_canvas)

        # Canvas background - show only for canvas
        if self.canvas_label:
            self.canvas_label.setVisible(is_canvas)
        if self.canvas_picker:
            self.canvas_picker.setVisible(is_canvas)

    def _pick_color(self, color_key: str):
        """Open color picker dialog.

        Args:
            color_key: The key for the color being picked
        """
        button_map = {
            "bg_color": self.bg_color_btn,
            "text_color": self.text_color_btn,
            "border_color": self.border_color_btn,
            "connector_color": self.conn_color_btn,
            "canvas_bg": self.canvas_picker,
        }

        button = button_map.get(color_key)
        if not button:
            return

        current_color = QColor(button.styleSheet().split("background-color: ")[1].split(";")[0])
        color_dialog = QColorDialog(current_color, self)
        color_dialog.setWindowTitle(f"Select {color_key.replace('_', ' ').title()} Color")
        color_dialog.setOption(QColorDialog.ShowAlphaChannel)

        # Position dialog
        position_color_dialog(color_dialog, button)

        if color_dialog.exec():
            color = color_dialog.currentColor()
            if color.isValid():
                # Use HexArgb to preserve alpha channel
                new_color = color.name(QColor.HexArgb)
                button.setStyleSheet(
                    f"background-color: {new_color}; "
                    "border: 1px solid #ccc; border-radius: 6px;"
                )
                self._emit_color_changed(color_key, new_color)

    def _emit_color_changed(self, color_key: str, color_value: str):
        """Emit color change signal.

        Args:
            color_key: The color property that changed
            color_value: The new color value
        """
        # Map color keys to style keys expected by downstream components
        style_key_map = {
            "bg_color": "bg_color",
            "text_color": "text_color",
            "border_color": "border_color",
            "connector_color": "connector_color",
            "canvas_bg": "canvas_bg",
        }

        style_key = style_key_map.get(color_key, color_key)
        self.color_changed.emit({style_key: color_value})

    def get_colors(self) -> dict:
        """Get current color values.

        Returns:
            Dictionary of color values
        """
        colors = {}

        if self.bg_color_btn:
            colors["bg_color"] = self.bg_color_btn.styleSheet().split("background-color: ")[1].split(";")[0]
        if self.text_color_btn:
            colors["text_color"] = self.text_color_btn.styleSheet().split("background-color: ")[1].split(";")[0]
        if self.border_color_btn:
            colors["border_color"] = self.border_color_btn.styleSheet().split("background-color: ")[1].split(";")[0]
        if self.conn_color_btn:
            colors["connector_color"] = self.conn_color_btn.styleSheet().split("background-color: ")[1].split(";")[0]
        if self.canvas_picker:
            colors["canvas_bg"] = self.canvas_picker.styleSheet().split("background-color: ")[1].split(";")[0]

        return colors

    def set_colors(self, colors: dict):
        """Set colors programmatically.

        Args:
            colors: Dictionary of color values
        """
        if not self._initialized:
            return

        button_map = {
            "bg_color": self.bg_color_btn,
            "text_color": self.text_color_btn,
            "border_color": self.border_color_btn,
            "connector_color": self.conn_color_btn,
            "canvas_bg": self.canvas_picker,
        }

        for color_key, button in button_map.items():
            if color_key in colors and button:
                button.setStyleSheet(
                    f"background-color: {colors[color_key]}; "
                    "border: 1px solid #ccc; border-radius: 6px;"
                )
