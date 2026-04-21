"""Shadow effect section widget.

Provides controls for configuring node shadow effects.
Implements lazy initialization for better performance.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton, QSpinBox

from .collapsible_panel import CollapsiblePanel


class ShadowSection(CollapsiblePanel):
    """Font Shadow effect configuration settings with lazy initialization.

    Signals:
        shadow_changed(dict): Emitted when shadow configuration changes
    """

    shadow_changed = Signal(dict)

    # UI constants
    LABEL_WIDTH = 75
    WIDGET_HEIGHT = 32
    GROUP_MARGIN = 10

    def __init__(self, parent=None):
        super().__init__("Font Shadow", collapsed=True, parent=parent)

        # State
        self._initialized = False
        self.current_shadow = self._get_default_shadow()

        # Connect toggle signal for lazy initialization
        self.toggled.connect(self._on_toggled)

    def _get_default_shadow(self) -> dict:
        """Get default shadow configuration."""
        return {
            "enabled": False,
            "offset_x": 2,
            "offset_y": 2,
            "blur": 4,
            "color": "#000000",
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
        layout.setContentsMargins(self.GROUP_MARGIN, 16, self.GROUP_MARGIN, 16)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)

        row = 0

        # Offset X
        offset_x_label = QLabel("Offset X:")
        offset_x_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        offset_x_label.setMinimumWidth(self.LABEL_WIDTH)
        offset_x_label.setStyleSheet("QLabel { font-size: 13px; color: #333333; }")
        layout.addWidget(offset_x_label, row, 0)

        self.shadow_offset_x_spin = QSpinBox()
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
        offset_y_label.setMinimumWidth(self.LABEL_WIDTH)
        offset_y_label.setStyleSheet("QLabel { font-size: 13px; color: #333333; }")
        layout.addWidget(offset_y_label, row, 0)

        self.shadow_offset_y_spin = QSpinBox()
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
        blur_label.setMinimumWidth(self.LABEL_WIDTH)
        blur_label.setStyleSheet("QLabel { font-size: 13px; color: #333333; }")
        layout.addWidget(blur_label, row, 0)

        self.shadow_blur_spin = QSpinBox()
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
        color_label.setMinimumWidth(self.LABEL_WIDTH)
        color_label.setStyleSheet("QLabel { font-size: 13px; color: #333333; }")
        layout.addWidget(color_label, row, 0)

        self.shadow_color_btn = QPushButton()
        self.shadow_color_btn.setFixedHeight(self.WIDGET_HEIGHT)
        self.shadow_color_btn.setStyleSheet(
            f"background-color: {self.current_shadow['color']}; "
            "border: 1px solid #ccc; border-radius: 4px;"
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
        """Open color picker dialog for shadow color."""
        from PySide6.QtWidgets import QColorDialog

        current_color = self.current_shadow.get("color", "#000000")
        color = QColorDialog.getColor(QColor(current_color), self, "Select Shadow Color", QColorDialog.ShowAlphaChannel)

        if color.isValid():
            # Use name(QColor.HexArgb) to preserve alpha channel
            color_name = color.name(QColor.HexArgb)
            self.current_shadow["color"] = color_name
            self.shadow_color_btn.setStyleSheet(
                f"background-color: {color_name}; border: 1px solid #ccc; border-radius: 4px;"
            )
            # Emit with shadow_ prefix to match role_style field names
            self.shadow_changed.emit({
                "shadow_color": color_name,
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
            if "enabled" in shadow:
                self.shadow_enabled_check.setChecked(shadow["enabled"])
            if "offset_x" in shadow:
                self.shadow_offset_x_spin.setValue(shadow["offset_x"])
            if "offset_y" in shadow:
                self.shadow_offset_y_spin.setValue(shadow["offset_y"])
            if "blur" in shadow:
                self.shadow_blur_spin.setValue(shadow["blur"])
            if "color" in shadow:
                self.shadow_color_btn.setStyleSheet(
                    f"background-color: {shadow['color']}; border: 1px solid #ccc; border-radius: 4px;"
                )
