"""Node style section widget.

Provides controls for customizing node appearance including shape, colors,
padding, and font properties. Implements lazy initialization for better performance.
"""

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QWidget,
)

from cogist.presentation.widgets import ToggleSwitch, VisualPreviewButton
from cogist.presentation.widgets.node_shape_previews import (
    generate_bottom_line_preview,
    generate_circle_preview,
    generate_left_line_preview,
    generate_rounded_rect_preview,
)

from .collapsible_panel import CollapsiblePanel
from .color_picker import create_color_picker
from .dialog_utils import position_color_dialog


class NodeStyleSection(CollapsiblePanel):
    """Node style settings with lazy initialization.

    Signals:
        style_changed(dict): Emitted when any node style property changes
        shadow_enabled_changed(bool): Emitted when shadow enabled state changes
    """

    style_changed = Signal(dict)
    shadow_enabled_changed = Signal(bool)

    # UI constants (fallback value, will use parent's LABEL_WIDTH if available)
    LABEL_WIDTH = 90
    WIDGET_HEIGHT = 32
    GROUP_MARGIN = 10

    def __init__(self, parent=None):
        super().__init__("Node Style", collapsed=True, parent=parent)

        # Get LABEL_WIDTH from parent (AdvancedStyleTab) if available, otherwise use class default
        self._label_width = getattr(parent, 'LABEL_WIDTH', self.LABEL_WIDTH) if parent else self.LABEL_WIDTH

        # Store reference to AdvancedStyleTab for accessing style_config
        # Note: parent() returns _content_widget, so we need to store the actual parent
        self._advanced_tab = parent

        # State
        self._initialized = False
        self.current_style = self._get_default_style()
        self.last_emitted_style = None  # Track last emitted style to detect changes
        self.is_root_mode = False  # True for root layer, False for level1/2/3+

        # Color picker (lazy creation)
        self._color_picker = None

        # Connect toggle signal for lazy initialization
        self.toggled.connect(self._on_toggled)

    def _get_default_style(self) -> dict:
        """Get default node style - used only during initialization before real data is loaded."""
        # This should be overwritten by set_style() before any UI interaction
        return {
            "bg_enabled": True,
            "shape": "rounded_rect",
            "radius": 10,
            "padding_w": 20,
            "padding_h": 16,
            "max_text_width": 250,  # Default max text width
            "bg_color_index": 0,
            "brightness": 1.0,
            "opacity": 255,
        }

    def _on_toggled(self, checked: bool):
        """Handle expand/collapse events."""
        if checked and not self._initialized:
            self._init_content()
            self._initialized = True
            # Apply saved style to newly created button (same as CanvasPanel)
            if self.current_style:
                self.set_style(self.current_style)

    def set_root_mode(self, is_root: bool):
        """Set whether this section is in root mode.

        In root mode, background color uses branch_colors[9] directly.
        In normal mode, background color uses bg_color_index to reference the pool.
        """
        self.is_root_mode = is_root
        # No need to update button - it only shows color, no text

    def _init_content(self):
        """Initialize content on first expand (lazy initialization)."""
        layout = QGridLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(self.GROUP_MARGIN, 6, self.GROUP_MARGIN, 6)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)

        row = 0

        # Style selector - using reusable VisualPreviewButton
        style_label = QLabel("Style:")
        style_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        style_label.setFixedWidth(self._label_width)
        layout.addWidget(style_label, row, 0)

        # Create visual options for popup
        style_options = [
            ("rounded_rect", generate_rounded_rect_preview, QSize(100, 24)),
            ("circle", generate_circle_preview, QSize(100, 24)),
            ("bottom_line", generate_bottom_line_preview, QSize(100, 24)),
            ("left_line", generate_left_line_preview, QSize(100, 24)),
        ]

        # Create reusable visual preview button
        self.style_btn = VisualPreviewButton(
            options=style_options,
            initial_value=self.current_style.get("shape", "rounded_rect"),
            preview_size=QSize(100, 24),
            button_height=self.WIDGET_HEIGHT,
        )
        self.style_btn.value_changed.connect(self._on_shape_changed)
        layout.addWidget(self.style_btn, row, 1)
        row += 1

        # Corner radius
        radius_label = QLabel("Radius:")
        radius_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        radius_label.setFixedWidth(self._label_width)
        layout.addWidget(radius_label, row, 0)

        self.radius_spin = QSpinBox()
        self.radius_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.radius_spin.setRange(0, 30)
        self.radius_spin.setValue(self.current_style["radius"])
        self.radius_spin.setAlignment(Qt.AlignLeft)
        self.radius_spin.valueChanged.connect(self._on_radius_changed)

        # Set initial visibility based on current shape
        # Only show radius for rounded_rect and rect (shapes that support border radius)
        container_shapes = ["rounded_rect", "rect"]
        current_shape = self.current_style.get("shape", "rounded_rect")
        show_radius = current_shape in container_shapes
        self.radius_spin.setVisible(show_radius)

        # Also set initial label visibility
        radius_label.setVisible(show_radius)

        layout.addWidget(self.radius_spin, row, 1)
        row += 1

        # Padding W
        padding_w_label = QLabel("Padding W:")
        padding_w_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        padding_w_label.setFixedWidth(self._label_width)
        layout.addWidget(padding_w_label, row, 0)

        self.padding_w_spin = QSpinBox()
        self.padding_w_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.padding_w_spin.setRange(0, 50)
        self.padding_w_spin.setValue(self.current_style["padding_w"])
        self.padding_w_spin.setAlignment(Qt.AlignLeft)
        self.padding_w_spin.valueChanged.connect(self._on_padding_changed)
        layout.addWidget(self.padding_w_spin, row, 1)
        row += 1

        # Padding H
        padding_h_label = QLabel("Padding H:")
        padding_h_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        padding_h_label.setFixedWidth(self._label_width)
        layout.addWidget(padding_h_label, row, 0)

        self.padding_h_spin = QSpinBox()
        self.padding_h_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.padding_h_spin.setRange(0, 50)
        self.padding_h_spin.setValue(self.current_style["padding_h"])
        self.padding_h_spin.setAlignment(Qt.AlignLeft)
        self.padding_h_spin.valueChanged.connect(self._on_padding_changed)
        layout.addWidget(self.padding_h_spin, row, 1)
        row += 1

        # Max text width
        max_text_width_label = QLabel("Max Width:")
        max_text_width_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        max_text_width_label.setFixedWidth(self._label_width)
        layout.addWidget(max_text_width_label, row, 0)

        self.max_text_width_spin = QSpinBox()
        self.max_text_width_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.max_text_width_spin.setRange(0, 1000)  # 0 means unlimited (no wrapping)
        self.max_text_width_spin.setValue(self.current_style.get("max_text_width", 250))
        self.max_text_width_spin.setAlignment(Qt.AlignLeft)
        self.max_text_width_spin.setSpecialValueText("Unlimited")  # Show "Unlimited" when value is 0
        self.max_text_width_spin.valueChanged.connect(self._on_max_text_width_changed)
        layout.addWidget(self.max_text_width_spin, row, 1)
        row += 1

        # Background enabled - Toggle Switch with label on same row (right-aligned like rainbow switch)
        from PySide6.QtWidgets import QHBoxLayout
        bg_switch_row = QHBoxLayout()
        bg_switch_row.setContentsMargins(0, 0, 0, 0)
        bg_switch_row.setSpacing(0)

        bg_header_label = QLabel("Background:")
        bg_header_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        bg_header_label.setFixedWidth(self._label_width)
        # Removed bold style - use normal font weight
        bg_switch_row.addWidget(bg_header_label)

        bg_switch_row.addStretch()

        self.bg_enabled_toggle = ToggleSwitch()
        self.bg_enabled_toggle.set_checked(self.current_style.get("bg_enabled", True))
        self.bg_enabled_toggle.toggled.connect(self._on_bg_enabled_changed)
        bg_switch_row.addWidget(self.bg_enabled_toggle)

        # Create a container widget to ensure proper height in grid layout
        bg_switch_container = QWidget()
        bg_switch_container.setLayout(bg_switch_row)
        bg_switch_container.setFixedHeight(self.WIDGET_HEIGHT)  # Match other widgets height

        layout.addWidget(bg_switch_container, row, 0, 1, 2)
        row += 1

        # Background color - same as CanvasPanel
        self.bg_color_label = QLabel("Color:")
        self.bg_color_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.bg_color_label.setFixedWidth(self._label_width)
        layout.addWidget(self.bg_color_label, row, 0)

        # Use QPushButton without text (like CanvasPanel) - shows only color
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setFixedHeight(self.WIDGET_HEIGHT)
        self.bg_color_btn.clicked.connect(self._on_bg_color_clicked)
        layout.addWidget(self.bg_color_btn, row, 1)
        # Note: Button stylesheet is set by set_style() - no text, no hardcoded colors
        row += 1

        # Brightness slider
        self.brightness_label = QLabel("Brightness:")
        self.brightness_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.brightness_label.setFixedWidth(self._label_width)
        layout.addWidget(self.brightness_label, row, 0)

        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(50, 150)  # 0.5-1.5
        self.brightness_slider.setValue(int(self.current_style.get("brightness", 1.0) * 100))
        self.brightness_slider.setFixedHeight(self.WIDGET_HEIGHT)
        self.brightness_slider.valueChanged.connect(self._on_brightness_changed)
        layout.addWidget(self.brightness_slider, row, 1, alignment=Qt.AlignVCenter)
        row += 1

        # Opacity slider
        self.opacity_label = QLabel("Opacity:")
        self.opacity_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.opacity_label.setFixedWidth(self._label_width)
        layout.addWidget(self.opacity_label, row, 0)

        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 255)
        self.opacity_slider.setValue(self.current_style.get("opacity", 255))
        self.opacity_slider.setFixedHeight(self.WIDGET_HEIGHT)
        self.opacity_slider.valueChanged.connect(self._on_opacity_changed)
        layout.addWidget(self.opacity_slider, row, 1, alignment=Qt.AlignVCenter)

        # Initialize visibility based on enabled state
        self._update_background_controls_visibility()

        self.setLayout(layout)

    def _on_shape_changed(self, shape_name: str):
        """Handle shape selection change."""
        self.current_style["shape"] = shape_name

        # Show/hide radius control based on shape type
        # Only show radius for rounded_rect and rect (shapes that support border radius)
        container_shapes = ["rounded_rect", "rect"]
        show_radius = shape_name in container_shapes

        if hasattr(self, 'radius_spin'):
            self.radius_spin.setVisible(show_radius)

            # Also hide/show the label
            layout = self._content_widget.layout()
            if layout:
                for i in range(layout.count()):
                    item = layout.itemAt(i)
                    widget = item.widget() if item else None
                    if widget and isinstance(widget, QLabel) and widget.text() == "Radius:":
                        widget.setVisible(show_radius)
                        break

        self._emit_style_changed()

    def _on_radius_changed(self, value: int):
        """Handle radius change."""
        self.current_style["radius"] = value
        self._emit_style_changed()

    def _on_padding_changed(self):
        """Handle padding changes."""
        self.current_style["padding_w"] = self.padding_w_spin.value()
        self.current_style["padding_h"] = self.padding_h_spin.value()
        self._emit_style_changed()

    def _on_max_text_width_changed(self, value: int):
        """Handle max text width change."""
        self.current_style["max_text_width"] = value
        self._emit_style_changed()

    def _update_background_controls_visibility(self):
        """Show/hide background controls based on enabled state."""
        enabled = self.current_style.get("bg_enabled", True)

        # Show/hide color button and label
        if hasattr(self, 'bg_color_label'):
            self.bg_color_label.setVisible(enabled)
        if hasattr(self, 'bg_color_btn'):
            self.bg_color_btn.setVisible(enabled)

        # Show/hide brightness slider and label
        if hasattr(self, 'brightness_label'):
            self.brightness_label.setVisible(enabled)
        if hasattr(self, 'brightness_slider'):
            self.brightness_slider.setVisible(enabled)

        # Show/hide opacity slider and label
        if hasattr(self, 'opacity_label'):
            self.opacity_label.setVisible(enabled)
        if hasattr(self, 'opacity_slider'):
            self.opacity_slider.setVisible(enabled)

    def _on_bg_enabled_changed(self, checked: bool):
        """Handle background enabled toggle change."""
        self.current_style["bg_enabled"] = checked

        # Update visibility of background controls
        self._update_background_controls_visibility()

        # Emit style changed event
        self._emit_style_changed()

    def _on_bg_color_clicked(self):
        """Handle background color button click."""
        # Use stored reference to AdvancedStyleTab instead of parent()
        parent = self._advanced_tab

        if not (parent and hasattr(parent, 'style_config') and parent.style_config):
            return

        if self.is_root_mode:
            # Root mode: show color picker for branch_colors[9] (same as CanvasPanel)
            if self._color_picker is None:
                self._color_picker = create_color_picker(self)
                self._color_picker.color_selected.connect(self._on_bg_color_selected)

            # Get current color from branch_colors[9]
            if (hasattr(parent.style_config, 'branch_colors') and
                parent.style_config.branch_colors and
                len(parent.style_config.branch_colors) > 9):
                current_color = parent.style_config.branch_colors[9]
            else:
                print("Warning: branch_colors not properly initialized or index 9 out of range")
                return

            # Set current color (MUST call before show!)
            self._color_picker.set_current_color(current_color)

            # Show color picker
            self._color_picker.show()
            self._color_picker.raise_()
            self._color_picker.activateWindow()

            # Position dialog
            position_color_dialog(self._color_picker, self.bg_color_btn)
        else:
            # Normal mode (level 1/2/3+): show color pool selector dialog
            self._show_color_pool_selector()

    def _show_color_pool_selector(self):
        """Show color pool selector dialog for level 1/2/3+ layers.

        Displays a dialog with 8 color buttons (indices 0-7) for user to select.
        """
        from PySide6.QtCore import Qt
        from PySide6.QtWidgets import QDialog, QGridLayout, QLabel, QPushButton

        parent = self._advanced_tab
        if not (parent and hasattr(parent, 'style_config') and parent.style_config):
            return

        branch_colors = parent.style_config.branch_colors
        if not branch_colors or len(branch_colors) < 8:
            print("Warning: branch_colors not properly initialized")
            return

        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Color from Pool")
        dialog.setFixedSize(280, 180)

        # Create layout
        layout = QGridLayout(dialog)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)

        # Add label
        label = QLabel("Choose a color (indices 0-7):")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label, 0, 0, 1, 4)

        # Create 8 color buttons (2 rows x 4 columns)
        buttons = []
        for i in range(8):
            btn = QPushButton()
            btn.setFixedSize(50, 50)
            color = branch_colors[i] if i < len(branch_colors) else "#FFCCCCCC"
            btn.setStyleSheet(
                f"background-color: {color}; "
                "border: 2px solid #C8C8C8; "
                "border-radius: 6px;"
            )
            btn.setToolTip(f"Color Index {i}")

            # Store index for callback
            btn.setProperty("color_index", i)
            btn.clicked.connect(lambda _, b=btn: self._on_color_pool_selected(b, dialog))

            row = 1 + (i // 4)
            col = i % 4
            layout.addWidget(btn, row, col)
            buttons.append(btn)

        # Show dialog
        dialog.exec()

    def _on_color_pool_selected(self, button, dialog):
        """Handle color selection from pool selector dialog.

        Args:
            button: The clicked color button
            dialog: The selector dialog to close
        """
        color_index = button.property("color_index")

        # Update bg_color_index in current_style
        self.current_style["bg_color_index"] = color_index

        # Update button display color
        parent = self._advanced_tab
        if parent and hasattr(parent, 'style_config') and parent.style_config:
            branch_colors = parent.style_config.branch_colors
            if color_index < len(branch_colors):
                selected_color = branch_colors[color_index]
                if hasattr(self, 'bg_color_btn'):
                    self.bg_color_btn.setStyleSheet(
                        f"background-color: {selected_color}; "
                        "border: 1px solid #C8C8C8; "
                        "border-radius: 6px; "
                        "padding: 4px 24px 4px 12px; "
                        "font-size: 13px; "
                        "text-align: left;"
                    )

        # Close dialog
        dialog.accept()

        # Emit style changed
        self._emit_style_changed()

    def _on_bg_color_selected(self, hex_color: str):
        """Handle color selection from picker (root mode only)."""
        # Update the color in branch_colors
        # Use stored reference to AdvancedStyleTab instead of parent()
        parent = self._advanced_tab

        if parent and hasattr(parent, 'style_config') and parent.style_config:
            if self.is_root_mode:
                # Root mode: update branch_colors[9] directly (like CanvasPanel uses index 8)
                if (hasattr(parent.style_config, 'branch_colors') and
                    parent.style_config.branch_colors and
                    len(parent.style_config.branch_colors) > 9):
                    parent.style_config.branch_colors[9] = hex_color

                    # CRITICAL: Update current_style to match CanvasPanel behavior
                    self.current_style["bg_color"] = hex_color

                    # Update button color directly (like CanvasPanel)
                    if hasattr(self, 'bg_color_btn'):
                        self.bg_color_btn.setStyleSheet(
                            f"background-color: {hex_color}; "
                            "border: 1px solid #C8C8C8; "
                            "border-radius: 6px; "
                            "padding: 4px 24px 4px 12px; "
                            "font-size: 13px; "
                            "text-align: left;"
                        )

                    # Emit style changed to trigger redraw
                    self._emit_style_changed()
                else:
                    print("Warning: branch_colors not properly initialized or index 9 out of range")
            else:
                # Normal mode: update branch_colors at bg_color_index
                color_index = self.current_style.get("bg_color_index", 0)

                if (hasattr(parent.style_config, 'branch_colors') and
                    parent.style_config.branch_colors and
                    color_index < len(parent.style_config.branch_colors)):
                    parent.style_config.branch_colors[color_index] = hex_color

                    # Update button color directly
                    if hasattr(self, 'bg_color_btn'):
                        self.bg_color_btn.setStyleSheet(
                            f"background-color: {hex_color}; "
                            "border: 1px solid #C8C8C8; "
                            "border-radius: 6px; "
                            "padding: 4px 24px 4px 12px; "
                            "font-size: 13px; "
                            "text-align: left;"
                        )

                    # Emit style changed to trigger redraw
                    self._emit_style_changed()
                else:
                    print(f"Warning: branch_colors not properly initialized or index {color_index} out of range")

    def _on_brightness_changed(self, value: int):
        """Handle background brightness change."""
        self.current_style["brightness"] = value / 100.0
        self._emit_style_changed()

    def _on_opacity_changed(self, value: int):
        """Handle background opacity change."""
        self.current_style["opacity"] = value
        self._emit_style_changed()

    def _emit_style_changed(self):
        """Emit style changed signal with only changed fields."""
        # If last_emitted_style is None, this means we haven't emitted anything yet
        # Initialize it with current state so future changes can be detected
        if self.last_emitted_style is None:
            self.last_emitted_style = dict(self.current_style)
            return  # Don't emit on initialization

        # Calculate which fields have changed
        changed_fields = {}
        for key, value in self.current_style.items():
            if key not in self.last_emitted_style or self.last_emitted_style[key] != value:
                changed_fields[key] = value

        # Update last emitted style
        self.last_emitted_style = dict(self.current_style)

        # Only emit if there are changes
        if changed_fields:
            self.style_changed.emit(changed_fields)

    def get_style(self) -> dict:
        """Get current node style."""
        return self.current_style.copy()

    def set_style(self, style: dict):
        """Set node style programmatically.

        Args:
            style: Dictionary containing node style properties
        """
        # If bg_color is not in style but we can get it from parent, add it
        if "bg_color" not in style and self._advanced_tab:
            parent = self._advanced_tab
            if hasattr(parent, 'style_config') and parent.style_config:
                branch_colors = parent.style_config.branch_colors
                if branch_colors:
                    if self.is_root_mode:
                        # Root mode: use branch_colors[9]
                        if len(branch_colors) > 9:
                            style = dict(style)  # Create a copy to avoid modifying original
                            style["bg_color"] = branch_colors[9]
                    else:
                        # Normal mode: use bg_color_index
                        color_index = style.get("bg_color_index", 0)
                        if color_index < len(branch_colors):
                            style = dict(style)  # Create a copy to avoid modifying original
                            style["bg_color"] = branch_colors[color_index]

        self.current_style.update(style)

        # Update last_emitted_style to match current state
        # This ensures the next change will only emit the actually changed fields
        self.last_emitted_style = dict(self.current_style)

        # Update UI if initialized
        if self._initialized:
            if "shape" in style:
                # Update preview button
                self.style_btn.set_value(style["shape"])

                # Update radius visibility based on shape
                # Only show radius for rounded_rect and rect (shapes that support border radius)
                container_shapes = ["rounded_rect", "rect"]
                show_radius = style["shape"] in container_shapes
                if hasattr(self, 'radius_spin'):
                    self.radius_spin.setVisible(show_radius)

                    # Also hide/show the label
                    layout = self._content_widget.layout()
                    if layout:
                        for i in range(layout.count()):
                            item = layout.itemAt(i)
                            widget = item.widget() if item else None
                            if widget and isinstance(widget, QLabel) and widget.text() == "Radius:":
                                widget.setVisible(show_radius)
                                break

            if "radius" in style:
                self.radius_spin.setValue(style["radius"])

            if "padding_w" in style:
                self.padding_w_spin.setValue(style["padding_w"])
            if "padding_h" in style:
                self.padding_h_spin.setValue(style["padding_h"])

            if "max_text_width" in style:
                self.max_text_width_spin.setValue(style["max_text_width"])

            # Update background color button
            if "bg_color" in style and hasattr(self, 'bg_color_btn'):
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
