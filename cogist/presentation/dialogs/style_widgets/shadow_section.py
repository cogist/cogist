"""Shadow effect section widget.

Provides controls for configuring node shadow effects.
Implements lazy initialization for better performance.
"""

from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import QGridLayout, QLabel, QPushButton
from qtpy.compat import isalive

from .collapsible_panel import CollapsiblePanel
from .color_picker import create_color_picker
from .dialog_utils import position_color_dialog
from .spinbox import SpinBox


class ShadowSection(CollapsiblePanel):
    """Font Shadow effect configuration settings with lazy initialization.

    Signals:
        shadow_changed(dict): Emitted when shadow configuration changes
    """

    shadow_changed = Signal(dict)

    # UI constants (fallback value, will use parent's LABEL_WIDTH if available)
    LABEL_WIDTH = 90
    WIDGET_HEIGHT = 32
    GROUP_MARGIN = 10

    def __init__(self, parent=None):
        super().__init__("Font Shadow", collapsed=True, parent=parent)

        # Get LABEL_WIDTH from parent (AdvancedStyleTab) if available, otherwise use class default
        self._label_width = getattr(parent, 'LABEL_WIDTH', self.LABEL_WIDTH) if parent else self.LABEL_WIDTH

        # State
        self._initialized = False
        self.current_shadow = {}  # Will be populated by set_shadow() from style_config

        # Color picker (lazy creation)
        self._color_picker = None

        # Connect toggle signal for lazy initialization
        self.toggled.connect(self._on_toggled)

    def _on_toggled(self, checked: bool):
        """Handle expand/collapse events."""
        if checked and not self._initialized:
            # Hide content widget before initialization to prevent flicker
            self._content_widget.setVisible(False)

            # Initialize content
            self._init_content()
            self._initialized = True

            # Show content widget after initialization is complete
            self._content_widget.setVisible(True)

    def _init_content(self):
        """Initialize content on first expand (lazy initialization)."""
        layout = QGridLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(self.GROUP_MARGIN, 6, self.GROUP_MARGIN, 16)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)

        row = 0

        # Offset X
        offset_x_label = QLabel("Offset X:")
        offset_x_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        offset_x_label.setFixedWidth(self._label_width)
        offset_x_label.setStyleSheet("QLabel { font-size: 13px; color: #333333; }")
        layout.addWidget(offset_x_label, row, 0)

        self.shadow_offset_x_spin = SpinBox()
        self.shadow_offset_x_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.shadow_offset_x_spin.setRange(-20, 20)
        self.shadow_offset_x_spin.setValue(self.current_shadow["offset_x"])
        self.shadow_offset_x_spin.setAlignment(Qt.AlignLeft)
        self.shadow_offset_x_spin.valueChanged.connect(self._on_shadow_changed)
        layout.addWidget(self.shadow_offset_x_spin, row, 1)
        row += 1

        # Offset Y
        offset_y_label = QLabel("Offset Y:")
        offset_y_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        offset_y_label.setFixedWidth(self._label_width)
        offset_y_label.setStyleSheet("QLabel { font-size: 13px; color: #333333; }")
        layout.addWidget(offset_y_label, row, 0)

        self.shadow_offset_y_spin = SpinBox()
        self.shadow_offset_y_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.shadow_offset_y_spin.setRange(-20, 20)
        self.shadow_offset_y_spin.setValue(self.current_shadow["offset_y"])
        self.shadow_offset_y_spin.setAlignment(Qt.AlignLeft)
        self.shadow_offset_y_spin.valueChanged.connect(self._on_shadow_changed)
        layout.addWidget(self.shadow_offset_y_spin, row, 1)
        row += 1

        # Blur
        blur_label = QLabel("Blur:")
        blur_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        blur_label.setFixedWidth(self._label_width)
        blur_label.setStyleSheet("QLabel { font-size: 13px; color: #333333; }")
        layout.addWidget(blur_label, row, 0)

        self.shadow_blur_spin = SpinBox()
        self.shadow_blur_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.shadow_blur_spin.setRange(0, 20)
        self.shadow_blur_spin.setValue(self.current_shadow["blur"])
        self.shadow_blur_spin.setAlignment(Qt.AlignLeft)
        self.shadow_blur_spin.valueChanged.connect(self._on_shadow_changed)
        layout.addWidget(self.shadow_blur_spin, row, 1)
        row += 1

        # Color
        color_label = QLabel("Color:")
        color_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        color_label.setFixedWidth(self._label_width)
        color_label.setStyleSheet("QLabel { font-size: 13px; color: #333333; }")
        layout.addWidget(color_label, row, 0)

        self.shadow_color_btn = QPushButton()
        self.shadow_color_btn.setFixedHeight(self.WIDGET_HEIGHT)
        # Set initial color from current_shadow (loaded from config via set_shadow)
        # Trust data integrity: color must exist in current_shadow
        shadow_color = self.current_shadow["color"]

        # Convert #AARRGGBB to rgba() format for Qt CSS
        if len(shadow_color) == 9 and shadow_color.startswith("#"):
            # #AARRGGBB format
            alpha = int(shadow_color[1:3], 16)
            red = int(shadow_color[3:5], 16)
            green = int(shadow_color[5:7], 16)
            blue = int(shadow_color[7:9], 16)
            self.shadow_color_btn.setStyleSheet(
                f"background-color: rgba({red}, {green}, {blue}, {alpha}); "
                "border: 1px solid #ccc; border-radius: 4px;"
            )
        else:
            # Fallback for other formats (should not happen)
            self.shadow_color_btn.setStyleSheet(
                f"background-color: {shadow_color}; border: 1px solid #ccc; border-radius: 4px;"
            )

        self.shadow_color_btn.clicked.connect(self._pick_color)
        layout.addWidget(self.shadow_color_btn, row, 1)

        self.setLayout(layout)

    def _on_shadow_changed(self):
        """Handle shadow parameter changes."""
        self.current_shadow["offset_x"] = self.shadow_offset_x_spin.value()
        self.current_shadow["offset_y"] = self.shadow_offset_y_spin.value()
        self.current_shadow["blur"] = self.shadow_blur_spin.value()
        # Emit with shadow_ prefix to match role_style field names
        self.shadow_changed.emit({
            "shadow_offset_x": self.current_shadow["offset_x"],
            "shadow_offset_y": self.current_shadow["offset_y"],
            "shadow_blur": self.current_shadow["blur"],
        })

    def _pick_color(self):
        """Open non-modal color picker dialog for shadow color."""
        # Get parent window for proper dialog lifecycle
        top_level = self.window() if self.window() else self

        # Check if color picker still exists (may have been deleted by WA_DeleteOnClose)
        if self._color_picker is None or not isalive(self._color_picker):
            self._color_picker = create_color_picker(top_level)
            self._color_picker.color_selected.connect(self._on_shadow_color_selected)
            # Ensure dialog closes when parent window closes
            self._color_picker.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

            # Enable alpha channel for shadow color (shadows need transparency)
            from qtpy.QtWidgets import QColorDialog
            self._color_picker.setOption(QColorDialog.ShowAlphaChannel, True)

        # Set current color (MUST call before show!)
        # Trust data integrity: color must exist in current_shadow
        current_color = self.current_shadow["color"]
        self._color_picker.set_current_color(current_color)

        # Show color picker
        self._color_picker.show()
        self._color_picker.raise_()
        self._color_picker.activateWindow()

        # Position dialog
        position_color_dialog(self._color_picker, self.shadow_color_btn)

    def _on_shadow_color_selected(self, hex_color: str):
        """Handle shadow color selection from picker."""
        self.current_shadow["color"] = hex_color

        # Convert #AARRGGBB to rgba() format for Qt CSS
        if len(hex_color) == 9 and hex_color.startswith("#"):
            # #AARRGGBB format
            alpha = int(hex_color[1:3], 16)
            red = int(hex_color[3:5], 16)
            green = int(hex_color[5:7], 16)
            blue = int(hex_color[7:9], 16)
            self.shadow_color_btn.setStyleSheet(
                f"background-color: rgba({red}, {green}, {blue}, {alpha}); "
                "border: 1px solid #ccc; border-radius: 4px;"
            )
        else:
            # Fallback for other formats (should not happen)
            self.shadow_color_btn.setStyleSheet(
                f"background-color: {hex_color}; border: 1px solid #ccc; border-radius: 4px;"
            )
        # Emit with shadow_ prefix to match role_style field names
        self.shadow_changed.emit({
            "shadow_color": hex_color,
        })

    def _emit_shadow_changed(self):
        """Emit shadow changed signal."""
        self.shadow_changed.emit(self.current_shadow.copy())

    def get_shadow(self) -> dict:
        """Get current shadow configuration."""
        return self.current_shadow.copy()

    def set_shadow(self, shadow: dict):
        """Set shadow configuration programmatically."""
        self.current_shadow.update(shadow)

        if self._initialized:
            # Note: 'enabled' is handled by NodeStyleSection, not here
            if "offset_x" in shadow:
                self.shadow_offset_x_spin.setValue(shadow["offset_x"])
            if "offset_y" in shadow:
                self.shadow_offset_y_spin.setValue(shadow["offset_y"])
            if "blur" in shadow:
                self.shadow_blur_spin.setValue(shadow["blur"])
            if "color" in shadow:
                # Convert #AARRGGBB to rgba() format for Qt CSS
                color_value = shadow["color"]
                if len(color_value) == 9 and color_value.startswith("#"):
                    # #AARRGGBB format
                    alpha = int(color_value[1:3], 16)
                    red = int(color_value[3:5], 16)
                    green = int(color_value[5:7], 16)
                    blue = int(color_value[7:9], 16)
                    self.shadow_color_btn.setStyleSheet(
                        f"background-color: rgba({red}, {green}, {blue}, {alpha}); "
                        "border: 1px solid #ccc; border-radius: 4px;"
                    )
                else:
                    # Fallback for other formats (should not happen)
                    self.shadow_color_btn.setStyleSheet(
                        f"background-color: {color_value}; border: 1px solid #ccc; border-radius: 4px;"
                    )
