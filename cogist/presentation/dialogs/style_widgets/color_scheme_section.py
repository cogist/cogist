"""Color scheme section widget.

Provides controls for customizing color scheme including:
- Per-role colors (background, text, border, connector)
- Auto-calculation for derived levels (level_2, level_3_plus)
- Rainbow branch colors (only for level_1)
- Canvas background

This section is Part of Presentation Layer (UI).
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
)

from .collapsible_panel import CollapsiblePanel

# Removed RainbowColorPool QWidget wrapper - using 8 individual buttons instead


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
        self._rainbow_visible = False  # Track rainbow check state

        # Default colors
        self._default_colors = {
            "bg_color": "#2196F3",
            "text_color": "#FFFFFF",
            "border_color": "#1976D2",
            "connector_color": "#1565C0",
            "canvas_bg": "#FFFFFF",
        }

        # Default rainbow colors
        self._default_rainbow = [
            "#FFFF6B6B",
            "#FF4ECDC4",
            "#FF45B7D1",
            "#FFFFA07A",
            "#FF98D8C8",
            "#FFF7DC6F",
            "#FFBB8FCE",
            "#FF85C1E2",
        ]

        # Color picker references
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

        # Auto checkbox (single switch for all colors)
        self.auto_check: QCheckBox | None = None

        # Rainbow branch references
        self.rainbow_label: QLabel | None = None
        self.rainbow_check: QCheckBox | None = None
        self.rainbow_buttons: list[QPushButton] = []
        self.rainbow_colors: list[str] = []

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
        layout.setColumnStretch(1, 1)  # Widget column - stretchable

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

        # Auto checkbox (show only for level_2 and level_3_plus)
        self.auto_label = QLabel("Auto:")
        self.auto_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.auto_label.setMinimumWidth(self.LABEL_WIDTH)
        self.auto_check = QCheckBox("Inherit from parent")
        self.auto_check.stateChanged.connect(self._on_auto_changed)
        layout.addWidget(self.auto_label, row, 0)
        layout.addWidget(self.auto_check, row, 1)
        row += 1

        # Rainbow branch (show only for level_1)
        self.rainbow_label = QLabel("Rainbow:")
        self.rainbow_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.rainbow_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(self.rainbow_label, row, 0)

        self.rainbow_check = QCheckBox("Use Rainbow")
        self.rainbow_check.toggled.connect(self._on_rainbow_changed)
        layout.addWidget(self.rainbow_check, row, 1)
        row += 1

        # Rainbow color buttons (8 individual buttons, not wrapped in QWidget)
        self.rainbow_buttons = []
        self.rainbow_colors = self._default_rainbow.copy()
        rainbow_layout = QHBoxLayout()
        rainbow_layout.setSpacing(4)
        rainbow_layout.setContentsMargins(0, 0, 0, 0)

        for i, color in enumerate(self.rainbow_colors):
            btn = QPushButton()
            btn.setFixedSize(32, 32)  # Larger size for better visibility
            btn.setToolTip(f"Branch {i + 1} color")
            btn.setStyleSheet(
                f"background-color: {color}; "
                "border: 2px solid #999999; border-radius: 4px;"
            )
            btn.clicked.connect(lambda _, idx=i: self._edit_rainbow_color(idx))
            self.rainbow_buttons.append(btn)
            rainbow_layout.addWidget(btn)

        rainbow_layout.addStretch()
        layout.addLayout(rainbow_layout, row, 0, 1, 2)
        row += 1

        # Canvas background (show only when Layer is canvas)
        self.canvas_label = QLabel("Canvas:")
        self.canvas_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.canvas_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(self.canvas_label, row, 0)

        self.canvas_picker = QPushButton()
        self.canvas_picker.setFixedHeight(self.WIDGET_HEIGHT)
        self.canvas_picker.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid #ccc; border-radius: 6px;"
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
        is_level_1 = self.current_role == "level_1"
        needs_auto = self.current_role in ("level_2", "level_3_plus")

        # Node colors (bg, text, border, connector) - hide for canvas
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

        if self.conn_label:
            self.conn_label.setVisible(not is_canvas)
        if self.conn_color_btn:
            self.conn_color_btn.setVisible(not is_canvas)

        # Auto checkbox - show only for level_2 and level_3_plus
        if self.auto_label:
            self.auto_label.setVisible(needs_auto)
        if self.auto_check:
            self.auto_check.setVisible(needs_auto)

        # Rainbow branch - show only for level_1
        if self.rainbow_label:
            self.rainbow_label.setVisible(is_level_1)
        if self.rainbow_check:
            self.rainbow_check.setVisible(is_level_1)
        # Show/hide rainbow buttons based on role and checkbox state
        rainbow_visible = is_level_1 and self._rainbow_visible
        for btn in self.rainbow_buttons:
            btn.setVisible(rainbow_visible)

        # Canvas background - show only for canvas
        if self.canvas_label:
            self.canvas_label.setVisible(is_canvas)
        if self.canvas_picker:
            self.canvas_picker.setVisible(is_canvas)

    def _on_auto_changed(self, state: int):
        """Handle Auto checkbox state change."""
        enabled = state == Qt.Checked

        # Disable all color pickers when Auto is enabled
        if self.bg_color_btn:
            self.bg_color_btn.setEnabled(not enabled)
        if self.text_color_btn:
            self.text_color_btn.setEnabled(not enabled)
        if self.border_color_btn:
            self.border_color_btn.setEnabled(not enabled)
        if self.conn_color_btn:
            self.conn_color_btn.setEnabled(not enabled)

        # Emit change for all color types
        self._emit_change("auto_enabled", enabled)

    def _on_rainbow_changed(self, checked: bool):
        """Handle rainbow checkbox state change."""
        enabled = checked
        self._rainbow_visible = enabled

        # Directly set rainbow buttons visibility
        # Only show if current role is level_1 AND checkbox is checked
        is_level_1 = self.current_role == "level_1"
        visible = is_level_1 and enabled

        for btn in self.rainbow_buttons:
            btn.setVisible(visible)

        # Force layout update
        if self.rainbow_buttons:
            self.updateGeometry()
            self.layout().update()

        # Disable background color picker when rainbow is enabled
        if self.bg_color_btn:
            self.bg_color_btn.setEnabled(not enabled)

        self._emit_change("use_rainbow", enabled)

    def _edit_rainbow_color(self, index: int):
        """Edit a rainbow branch color."""
        from PySide6.QtGui import QColor
        from PySide6.QtWidgets import QColorDialog

        current = QColor(self.rainbow_colors[index])
        color = QColorDialog.getColor(
            current, self, "Select Branch Color", QColorDialog.ShowAlphaChannel
        )
        if color.isValid():
            self.rainbow_colors[index] = color.name(QColor.HexArgb)
            self.rainbow_buttons[index].setStyleSheet(
                f"background-color: {self.rainbow_colors[index]}; "
                "border: 1px solid #CCCCCC; border-radius: 3px;"
            )
            self._emit_change("rainbow_pool", self.rainbow_colors)

    def _pick_color(self, color_key: str):
        """Open color picker dialog."""
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

        current_color = QColor(
            button.styleSheet().split("background-color: ")[1].split(";")[0]
        )
        color_dialog = QColorDialog(current_color, self)
        color_dialog.setWindowTitle(
            f"Select {color_key.replace('_', ' ').title()} Color"
        )
        color_dialog.setOption(QColorDialog.ShowAlphaChannel)

        # Position dialog
        from .dialog_utils import position_color_dialog

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
        """Emit color change signal."""
        style_key_map = {
            "bg_color": "bg_color",
            "text_color": "text_color",
            "border_color": "border_color",
            "connector_color": "connector_color",
            "canvas_bg": "canvas_bg",
        }

        style_key = style_key_map.get(color_key, color_key)
        self.color_changed.emit({style_key: color_value})

    def _emit_change(self, key: str, value):
        """Emit a change signal with key-value pair."""
        self.color_changed.emit({key: value})

    def get_colors(self) -> dict:
        """Get current color values."""
        colors = {}

        if self.bg_color_btn:
            colors["bg_color"] = (
                self.bg_color_btn.styleSheet()
                .split("background-color: ")[1]
                .split(";")[0]
            )
        if self.text_color_btn:
            colors["text_color"] = (
                self.text_color_btn.styleSheet()
                .split("background-color: ")[1]
                .split(";")[0]
            )
        if self.border_color_btn:
            colors["border_color"] = (
                self.border_color_btn.styleSheet()
                .split("background-color: ")[1]
                .split(";")[0]
            )
        if self.conn_color_btn:
            colors["connector_color"] = (
                self.conn_color_btn.styleSheet()
                .split("background-color: ")[1]
                .split(";")[0]
            )
        if self.canvas_picker:
            colors["canvas_bg"] = (
                self.canvas_picker.styleSheet()
                .split("background-color: ")[1]
                .split(";")[0]
            )

        # Auto state
        if self.auto_check:
            colors["auto_enabled"] = self.auto_check.isChecked()

        # Rainbow
        if self.rainbow_check:
            colors["use_rainbow"] = self.rainbow_check.isChecked()
        if self.rainbow_buttons:
            colors["rainbow_pool"] = self.rainbow_colors

        return colors

    def set_colors(self, colors: dict):
        """Set colors programmatically."""
        # Always update state, even if not initialized (for lazy loading)
        if "use_rainbow" in colors:
            self._rainbow_visible = colors["use_rainbow"]

        # Update UI only if initialized
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

        # Auto state
        if "auto_enabled" in colors and self.auto_check:
            self.auto_check.setChecked(colors["auto_enabled"])

        # Rainbow
        # Only update internal state and button visibility, don't reset checkbox state
        if "use_rainbow" in colors:
            rainbow_enabled = colors["use_rainbow"]
            self._rainbow_visible = rainbow_enabled

            # Update button visibility based on loaded state
            is_level_1 = self.current_role == "level_1"
            visible = is_level_1 and rainbow_enabled
            for btn in self.rainbow_buttons:
                btn.setVisible(visible)

            # Update background color picker enabled state
            if self.bg_color_btn:
                self.bg_color_btn.setEnabled(not rainbow_enabled)

        # Set rainbow colors
        if "rainbow_pool" in colors and self.rainbow_buttons:
            self.rainbow_colors = colors["rainbow_pool"][:8]
            # Pad with default colors if needed
            while len(self.rainbow_colors) < 8:
                self.rainbow_colors.append(
                    self._default_rainbow[len(self.rainbow_colors)]
                )

            for i, btn in enumerate(self.rainbow_buttons):
                if i < len(self.rainbow_colors):
                    btn.setStyleSheet(
                        f"background-color: {self.rainbow_colors[i]}; "
                        "border: 1px solid #CCCCCC; border-radius: 3px;"
                    )
