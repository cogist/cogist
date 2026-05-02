"""Color picker dialog with advanced features.

Provides a reusable color picker with:
- Standard Qt color dialog
- Recent colors tracking
- Screen-aware positioning
"""

from PySide6.QtCore import Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QColorDialog, QWidget


class ColorPicker(QColorDialog):
    """Enhanced color picker dialog."""

    color_selected = Signal(str)  # Emits hex color string (#RRGGBB)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        # Configure dialog for real-time preview
        self.setOptions(
            QColorDialog.NoButtons  # No OK/Cancel - apply immediately
            | QColorDialog.DontUseNativeDialog
        )

        # Connect signals - emit on color change for real-time preview
        self.currentColorChanged.connect(self._on_color_changed)

        # Recent colors (max 16)
        self._recent_colors: list[str] = []

    def _on_color_changed(self, color: QColor):
        """Handle color change for real-time preview."""
        # Convert to hex string with alpha (always output ARGB format)
        # When ShowAlphaChannel is disabled, alpha defaults to 255 (opaque)
        hex_color = color.name(QColor.NameFormat.HexArgb)
        self.color_selected.emit(hex_color)

    def set_current_color(self, hex_color: str):
        """Set current color from hex string.

        Args:
            hex_color: Color in #RRGGBB or #AARRGGBB format
        """
        # Parse hex color
        if hex_color.startswith("#"):
            hex_color = hex_color[1:]

        # Handle different formats
        if len(hex_color) == 6:
            # #RRGGBB format - add opaque alpha
            color = QColor(f"#{hex_color}")
            color.setAlpha(255)
        elif len(hex_color) == 8:
            # #AARRGGBB format
            alpha = int(hex_color[0:2], 16)
            rgb = hex_color[2:]
            color = QColor(f"#{rgb}")
            color.setAlpha(alpha)
        else:
            # Invalid format - use black
            color = QColor("#FF000000")

        # Temporarily block signals to prevent triggering color_selected
        # when setting the initial color (which would update the button incorrectly)
        self.blockSignals(True)
        self.setCurrentColor(color)
        self.blockSignals(False)

    def add_recent_color(self, hex_color: str):
        """Add color to recent colors list.

        Args:
            hex_color: Color in hex format
        """
        if hex_color not in self._recent_colors:
            self._recent_colors.insert(0, hex_color)
            # Keep only last 16 colors
            if len(self._recent_colors) > 16:
                self._recent_colors = self._recent_colors[:16]
            self.setCustomColors(self._recent_colors)

    def get_recent_colors(self) -> list[str]:
        """Get recent colors list."""
        return self._recent_colors.copy()


def create_color_picker(parent: QWidget | None = None) -> ColorPicker:
    """Create a color picker instance.

    Args:
        parent: Parent widget

    Returns:
        ColorPicker instance
    """
    return ColorPicker(parent)
