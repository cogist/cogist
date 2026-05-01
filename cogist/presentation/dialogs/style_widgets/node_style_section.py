"""Node style section widget.

Provides controls for customizing node appearance including shape, colors,
padding, and font properties. Implements lazy initialization for better performance.
"""

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
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
from .menu_button import MenuButton


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

        # State
        self._initialized = False
        self.current_style = self._get_default_style()
        self.last_emitted_style = None  # Track last emitted style to detect changes

        # Connect toggle signal for lazy initialization
        self.toggled.connect(self._on_toggled)

    def _get_default_style(self) -> dict:
        """Get default node style - used only during initialization before real data is loaded."""
        # This should be overwritten by set_style() before any UI interaction
        return {
            "enabled": True,
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
        self.bg_enabled_toggle.set_checked(self.current_style.get("enabled", True))
        self.bg_enabled_toggle.toggled.connect(self._on_bg_enabled_changed)
        bg_switch_row.addWidget(self.bg_enabled_toggle)

        # Create a container widget to ensure proper height in grid layout
        bg_switch_container = QWidget()
        bg_switch_container.setLayout(bg_switch_row)
        bg_switch_container.setFixedHeight(self.WIDGET_HEIGHT)  # Match other widgets height

        layout.addWidget(bg_switch_container, row, 0, 1, 2)
        row += 1

        # Background color (placeholder - will be implemented later)
        self.bg_color_label = QLabel("Color:")
        self.bg_color_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.bg_color_label.setFixedWidth(self._label_width)
        layout.addWidget(self.bg_color_label, row, 0)

        self.bg_color_btn = MenuButton("Color 1", self.WIDGET_HEIGHT)
        self.bg_color_btn.setStyleSheet(self._button_style())
        self.bg_color_btn.clicked.connect(self._on_bg_color_clicked)
        layout.addWidget(self.bg_color_btn, row, 1)
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
        enabled = self.current_style.get("enabled", True)

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
        self.current_style["enabled"] = checked

        # Update visibility of background controls
        self._update_background_controls_visibility()

        # Emit style changed event
        self._emit_style_changed()

    def _on_bg_color_clicked(self):
        """Handle background color button click (placeholder)."""
        # TODO: Implement color picker dialog
        pass

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
