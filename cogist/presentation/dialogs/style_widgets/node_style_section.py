"""Node style section widget.

Provides controls for customizing node appearance including shape, colors,
padding, and font properties. Implements lazy initialization for better performance.
"""

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QSpinBox,
)

from cogist.presentation.widgets import VisualPreviewButton
from cogist.presentation.widgets.node_shape_previews import (
    generate_bottom_line_preview,
    generate_circle_preview,
    generate_left_line_preview,
    generate_rounded_rect_preview,
)

from .collapsible_panel import CollapsiblePanel


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
            "shape": "rounded_rect",
            "radius": 10,
            "padding_w": 20,
            "padding_h": 16,
            "max_text_width": 250,  # Default max text width
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
        layout.setContentsMargins(self.GROUP_MARGIN, 6, self.GROUP_MARGIN, 16)
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
