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
    QColorDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from cogist.presentation.widgets import ToggleSwitch

from .collapsible_panel import CollapsiblePanel

# Removed RainbowColorPool QWidget wrapper - using 8 individual buttons instead


class ColorSchemeSection(CollapsiblePanel):
    """Color scheme settings section.

    Signals:
        color_changed(dict): Emitted when color properties change
    """

    color_changed = Signal(dict)

    # UI constants (fallback value, will use parent's LABEL_WIDTH if available)
    LABEL_WIDTH = 90
    WIDGET_HEIGHT = 32
    GROUP_MARGIN = 10

    def __init__(self, parent=None):
        super().__init__("Color Scheme", collapsed=True, parent=parent)

        # Get LABEL_WIDTH from parent (AdvancedStyleTab) if available, otherwise use class default
        self._label_width = getattr(parent, 'LABEL_WIDTH', self.LABEL_WIDTH) if parent else self.LABEL_WIDTH

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

        # Rainbow branch references
        self.rainbow_pool_widget: QWidget | None = None
        self.rainbow_label: QLabel | None = None
        self.rainbow_check: ToggleSwitch | None = None
        self.rainbow_label_pool: QLabel | None = None
        self.rainbow_buttons: list[QPushButton] = []
        self.rainbow_colors: list[str] = []

        # Rainbow mode controls (per-role)
        self.rainbow_bg_check: ToggleSwitch | None = None
        self.rainbow_border_check: ToggleSwitch | None = None
        self.brightness_check: ToggleSwitch | None = None
        self.brightness_slider: QSlider | None = None

        # Labels for rainbow mode controls
        self.rainbow_bg_label: QLabel | None = None
        self.rainbow_border_label: QLabel | None = None
        self.brightness_label: QLabel | None = None
        self.brightness_slider_label: QLabel | None = None

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
        layout.setContentsMargins(self.GROUP_MARGIN, 6, self.GROUP_MARGIN, 16)
        layout.setColumnStretch(0, 0)  # Label column - fixed width
        layout.setColumnStretch(1, 1)  # Widget column - stretchable

        row = 0

        # === Global Rainbow Branch Switch ===
        switch_row = QHBoxLayout()
        switch_row.setContentsMargins(0, 0, 0, 0)
        switch_row.setSpacing(0)

        self.rainbow_label = QLabel("Branch-based:")
        self.rainbow_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.rainbow_label.setFixedWidth(self._label_width)
        switch_row.addWidget(self.rainbow_label)

        switch_row.addStretch()

        self.rainbow_check = ToggleSwitch()
        self.rainbow_check.toggled.connect(self._on_rainbow_changed)
        switch_row.addWidget(self.rainbow_check)

        layout.addLayout(switch_row, row, 0, 1, 2)
        row += 1

        # === Rainbow Branch Color Pool (shown when rainbow enabled) ===
        self.rainbow_label_pool = QLabel("Color Pool:")
        self.rainbow_label_pool.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.rainbow_label_pool.setFixedWidth(self._label_width)
        layout.addWidget(self.rainbow_label_pool, row, 0)

        # Rainbow color buttons container - 2 rows with flexible spacing
        buttons_container = QWidget()
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(4)
        buttons_layout.setContentsMargins(0, 0, 0, 0)

        self.rainbow_buttons = []
        self.rainbow_colors = self._default_rainbow.copy()

        for row_idx in range(2):
            btn_row_layout = QHBoxLayout()
            btn_row_layout.setSpacing(0)  # No fixed spacing, use stretch instead
            btn_row_layout.setContentsMargins(0, 0, 0, 0)

            for col_idx in range(4):
                i = row_idx * 4 + col_idx
                btn = QPushButton()
                btn.setFixedSize(32, 32)
                btn.setToolTip(f"Branch {i + 1} color")
                color = self.rainbow_colors[i] if i < len(self.rainbow_colors) else "#FFCCCCCC"
                btn.setStyleSheet(
                    f"background-color: {color}; "
                    "border: none; border-radius: 4px;"
                )
                btn.clicked.connect(lambda _, idx=i: self._edit_rainbow_color(idx))
                self.rainbow_buttons.append(btn)
                btn_row_layout.addWidget(btn)

                # Add stretch after each button except the last one in each row
                if col_idx < 3:
                    btn_row_layout.addStretch()

            buttons_layout.addLayout(btn_row_layout)

        buttons_container.setLayout(buttons_layout)

        # Wrap pool buttons in a widget for visibility control
        self.rainbow_pool_widget = QWidget()
        pool_layout = QVBoxLayout()
        pool_layout.setContentsMargins(0, 0, 0, 0)
        pool_layout.setSpacing(0)
        pool_layout.addWidget(buttons_container)
        self.rainbow_pool_widget.setLayout(pool_layout)

        layout.addWidget(self.rainbow_pool_widget, row, 1)
        self.rainbow_buttons_row = row
        row += 1

        # Initially hide rainbow pool
        if self.rainbow_pool_widget:
            self.rainbow_pool_widget.setVisible(False)

        # Background color
        self.bg_label = QLabel("Background:")
        self.bg_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.bg_label.setFixedWidth(self._label_width)
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
        self.text_label.setFixedWidth(self._label_width)
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
        self.border_label.setFixedWidth(self._label_width)
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
        self.conn_label.setFixedWidth(self._label_width)
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
        self.canvas_label.setFixedWidth(self._label_width)
        layout.addWidget(self.canvas_label, row, 0)

        self.canvas_picker = QPushButton()
        self.canvas_picker.setFixedHeight(self.WIDGET_HEIGHT)
        self.canvas_picker.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid #ccc; border-radius: 6px;"
        )
        self.canvas_picker.clicked.connect(lambda: self._pick_color("canvas_bg"))
        layout.addWidget(self.canvas_picker, row, 1)
        row += 1

        # === Per-Role Rainbow Mode Controls (dynamic visibility) ===

        # Level 1: Rainbow Background toggle
        bg_row = QHBoxLayout()
        bg_row.setContentsMargins(0, 0, 0, 0)
        bg_row.setSpacing(0)

        self.rainbow_bg_label = QLabel("Background:")
        self.rainbow_bg_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.rainbow_bg_label.setFixedWidth(self._label_width)
        bg_row.addWidget(self.rainbow_bg_label)

        bg_row.addStretch()

        self.rainbow_bg_check = ToggleSwitch()
        self.rainbow_bg_check.toggled.connect(lambda checked: self._emit_change("rainbow_bg_enabled", checked))
        bg_row.addWidget(self.rainbow_bg_check)

        layout.addLayout(bg_row, row, 0, 1, 2)
        row += 1

        # Level 1: Rainbow Border toggle
        border_row = QHBoxLayout()
        border_row.setContentsMargins(0, 0, 0, 0)
        border_row.setSpacing(0)

        self.rainbow_border_label = QLabel("Border:")
        self.rainbow_border_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.rainbow_border_label.setFixedWidth(self._label_width)
        border_row.addWidget(self.rainbow_border_label)

        border_row.addStretch()

        self.rainbow_border_check = ToggleSwitch()
        self.rainbow_border_check.toggled.connect(lambda checked: self._emit_change("rainbow_border_enabled", checked))
        border_row.addWidget(self.rainbow_border_check)

        layout.addLayout(border_row, row, 0, 1, 2)
        row += 1

        # Level 2/3+: Brightness adjustment toggle
        brightness_toggle_row = QHBoxLayout()
        brightness_toggle_row.setContentsMargins(0, 0, 0, 0)
        brightness_toggle_row.setSpacing(0)

        self.brightness_label = QLabel("Brightness:")
        self.brightness_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.brightness_label.setFixedWidth(self._label_width)
        brightness_toggle_row.addWidget(self.brightness_label)

        brightness_toggle_row.addStretch()

        # Use ToggleSwitch instead of QCheckBox
        self.brightness_check = ToggleSwitch()
        self.brightness_check.toggled.connect(lambda checked: self._on_brightness_toggled(checked))
        brightness_toggle_row.addWidget(self.brightness_check)

        layout.addLayout(brightness_toggle_row, row, 0, 1, 2)
        row += 1

        # Brightness slider with label (only visible when switch is ON)
        brightness_slider_row = QHBoxLayout()
        brightness_slider_row.setContentsMargins(0, 0, 0, 0)
        brightness_slider_row.setSpacing(0)

        self.brightness_slider_label = QLabel("Adjust:")
        self.brightness_slider_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.brightness_slider_label.setFixedWidth(self._label_width)
        self.brightness_slider_label.setVisible(False)  # Initially hidden
        brightness_slider_row.addWidget(self.brightness_slider_label)

        brightness_slider_row.addStretch()

        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(0, 100)
        self.brightness_slider.setValue(50)
        self.brightness_slider.setEnabled(False)
        self.brightness_slider.setVisible(False)  # Initially hidden
        self.brightness_slider.valueChanged.connect(lambda value: self._emit_change("brightness_amount", value))
        brightness_slider_row.addWidget(self.brightness_slider)

        layout.addLayout(brightness_slider_row, row, 0, 1, 2)
        row += 1

        # Initially hide all rainbow mode controls
        self._hide_rainbow_mode_controls()

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
        is_level_2 = self.current_role == "level_2"
        is_level_3_plus = self.current_role == "level_3_plus"

        rainbow_enabled = self._rainbow_visible

        # Node colors (bg, text, border, connector) - hide for canvas
        # Background
        if self.bg_label and self.bg_color_btn:
            # Hide in rainbow mode for level_1/2/3+
            should_show_bg = not is_canvas and not (rainbow_enabled and (is_level_1 or is_level_2 or is_level_3_plus))
            self.bg_label.setVisible(should_show_bg)
            self.bg_color_btn.setVisible(should_show_bg)

        # Text Color
        if self.text_label and self.text_color_btn:
            # Hide in rainbow mode (use auto contrast)
            should_show_text = not is_canvas and not rainbow_enabled
            self.text_label.setVisible(should_show_text)
            self.text_color_btn.setVisible(should_show_text)

        # Border Color
        if self.border_label and self.border_color_btn:
            # Hide in rainbow mode for level_1/2/3+
            should_show_border = not is_canvas and not (rainbow_enabled and (is_level_1 or is_level_2 or is_level_3_plus))
            self.border_label.setVisible(should_show_border)
            self.border_color_btn.setVisible(should_show_border)

        # Connector Color
        if self.conn_label and self.conn_color_btn:
            # Hide in rainbow mode (follow node color)
            should_show_conn = not is_canvas and not rainbow_enabled
            self.conn_label.setVisible(should_show_conn)
            self.conn_color_btn.setVisible(should_show_conn)

        # Rainbow mode controls - show based on role and rainbow state
        if rainbow_enabled:
            # Always show rainbow color pool when rainbow is enabled (regardless of role)
            if self.rainbow_label_pool:
                self.rainbow_label_pool.setVisible(True)
            for btn in self.rainbow_buttons:
                btn.setVisible(True)

            if is_level_2 or is_level_3_plus:
                # Level 2/3+: Show rainbow bg/border toggles AND brightness controls
                if self.rainbow_bg_label:
                    self.rainbow_bg_label.setVisible(True)
                if self.rainbow_bg_check:
                    self.rainbow_bg_check.setVisible(True)
                if self.rainbow_border_label:
                    self.rainbow_border_label.setVisible(True)
                if self.rainbow_border_check:
                    self.rainbow_border_check.setVisible(True)

                # Show brightness adjustment for level 2/3+
                if self.brightness_label:
                    self.brightness_label.setVisible(True)
                if self.brightness_check:
                    self.brightness_check.setVisible(True)
                if self.brightness_slider and self.brightness_slider_label and self.brightness_check:
                    # Slider and label visibility is controlled by the toggle switch state
                    is_checked = self.brightness_check.isChecked()
                    self.brightness_slider.setVisible(is_checked)
                    self.brightness_slider_label.setVisible(is_checked)

            elif is_level_1:
                # Level 1 only: Show rainbow bg/border toggles, hide brightness controls
                if self.rainbow_bg_label:
                    self.rainbow_bg_label.setVisible(True)
                if self.rainbow_bg_check:
                    self.rainbow_bg_check.setVisible(True)
                if self.rainbow_border_label:
                    self.rainbow_border_label.setVisible(True)
                if self.rainbow_border_check:
                    self.rainbow_border_check.setVisible(True)

                # Hide brightness controls for level 1
                if self.brightness_label:
                    self.brightness_label.setVisible(False)
                if self.brightness_check:
                    self.brightness_check.setVisible(False)
                if self.brightness_slider_label:
                    self.brightness_slider_label.setVisible(False)
                if self.brightness_slider:
                    self.brightness_slider.setVisible(False)
            else:
                # Other roles (root, canvas): hide level-specific rainbow controls but keep color pool visible
                if self.rainbow_bg_label:
                    self.rainbow_bg_label.setVisible(False)
                if self.rainbow_bg_check:
                    self.rainbow_bg_check.setVisible(False)
                if self.rainbow_border_label:
                    self.rainbow_border_label.setVisible(False)
                if self.rainbow_border_check:
                    self.rainbow_border_check.setVisible(False)
                if self.brightness_label:
                    self.brightness_label.setVisible(False)
                if self.brightness_check:
                    self.brightness_check.setVisible(False)
                if self.brightness_slider_label:
                    self.brightness_slider_label.setVisible(False)
                if self.brightness_slider:
                    self.brightness_slider.setVisible(False)
        else:
            # Rainbow disabled: hide all rainbow mode controls
            self._hide_rainbow_mode_controls()

        # Canvas background - show only for canvas
        if self.canvas_label:
            self.canvas_label.setVisible(is_canvas)
        if self.canvas_picker:
            self.canvas_picker.setVisible(is_canvas)

    def _on_rainbow_changed(self, checked: bool):
        """Handle rainbow checkbox state change."""
        enabled = checked
        self._rainbow_visible = enabled

        # Show/hide entire rainbow pool widget
        if self.rainbow_pool_widget:
            self.rainbow_pool_widget.setVisible(enabled)

        # Update role-specific controls visibility
        self._apply_role_visibility()

        # Force layout update
        if self.rainbow_buttons:
            self.updateGeometry()
            if self.layout():
                self.layout().update()

        self._emit_change("use_rainbow", enabled)

    def _hide_rainbow_mode_controls(self):
        """Hide all rainbow mode specific controls."""
        # Rainbow pool
        if self.rainbow_label_pool:
            self.rainbow_label_pool.setVisible(False)
        for btn in self.rainbow_buttons:
            btn.setVisible(False)

        # Level 1 controls
        if self.rainbow_bg_label:
            self.rainbow_bg_label.setVisible(False)
        if self.rainbow_bg_check:
            self.rainbow_bg_check.setVisible(False)
        if self.rainbow_border_label:
            self.rainbow_border_label.setVisible(False)
        if self.rainbow_border_check:
            self.rainbow_border_check.setVisible(False)

        # Level 2/3+ controls
        if self.brightness_label:
            self.brightness_label.setVisible(False)
        if self.brightness_check:
            self.brightness_check.setVisible(False)
        if self.brightness_slider_label:
            self.brightness_slider_label.setVisible(False)
        if self.brightness_slider:
            self.brightness_slider.setVisible(False)

    def _on_brightness_toggled(self, checked: bool):
        """Handle brightness toggle switch state change."""
        if self.brightness_slider:
            self.brightness_slider.setEnabled(checked)
            self.brightness_slider.setVisible(checked)  # Show/hide slider
        if self.brightness_slider_label:
            self.brightness_slider_label.setVisible(checked)  # Show/hide label
        self._emit_change("brightness_enabled", checked)

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
                "border: none; border-radius: 4px;"
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

        # Rainbow
        # Only update internal state and button visibility, don't reset checkbox state
        if "use_rainbow" in colors:
            rainbow_enabled = colors["use_rainbow"]
            self._rainbow_visible = rainbow_enabled

            # Update rainbow checkbox state (block signals to avoid recursion)
            if self.rainbow_check:
                self.rainbow_check.blockSignals(True)
                self.rainbow_check.setChecked(rainbow_enabled)
                self.rainbow_check.blockSignals(False)

            # Update button and label visibility based on loaded state
            if self.rainbow_label_pool:
                self.rainbow_label_pool.setVisible(rainbow_enabled)
            for btn in self.rainbow_buttons:
                btn.setVisible(rainbow_enabled)

            # Update role-specific controls
            self._apply_role_visibility()

        # Set rainbow mode control values
        if "rainbow_bg_enabled" in colors and self.rainbow_bg_check:
            self.rainbow_bg_check.blockSignals(True)
            self.rainbow_bg_check.setChecked(colors["rainbow_bg_enabled"])
            self.rainbow_bg_check.blockSignals(False)

        if "rainbow_border_enabled" in colors and self.rainbow_border_check:
            self.rainbow_border_check.blockSignals(True)
            self.rainbow_border_check.setChecked(colors["rainbow_border_enabled"])
            self.rainbow_border_check.blockSignals(False)

        if "brightness_enabled" in colors and self.brightness_check:
            self.brightness_check.blockSignals(True)
            self.brightness_check.setChecked(colors["brightness_enabled"])
            self.brightness_check.blockSignals(False)

            # Only update slider visibility if current role allows brightness controls (level_2 or level_3_plus)
            is_level_2 = self.current_role == "level_2"
            is_level_3_plus = self.current_role == "level_3_plus"
            should_show_brightness = is_level_2 or is_level_3_plus

            if self.brightness_slider:
                self.brightness_slider.setEnabled(colors["brightness_enabled"])
                # Update slider visibility based on checked state AND role
                self.brightness_slider.setVisible(colors["brightness_enabled"] and should_show_brightness)
            if self.brightness_slider_label:
                # Update label visibility based on checked state AND role
                self.brightness_slider_label.setVisible(colors["brightness_enabled"] and should_show_brightness)

        if "brightness_amount" in colors and self.brightness_slider:
            self.brightness_slider.blockSignals(True)
            self.brightness_slider.setValue(int(colors["brightness_amount"]))
            self.brightness_slider.blockSignals(False)

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
                        "border: none; border-radius: 4px;"
                    )
