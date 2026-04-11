"""
Color Value Object - Domain Layer

Immutable value object representing colors.
"""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Color:
    """
    Color value object.

    Represents a color in HEX or RGB format.

    Attributes:
        hex_value: Color in HEX format (e.g., "#2196F3")
    """

    hex_value: str = "#2196F3"

    def __post_init__(self):
        """Validate HEX color format after initialization."""
        if not self._is_valid_hex_color(self.hex_value):
            raise ValueError(f"Invalid HEX color: {self.hex_value}")

    @staticmethod
    def _is_valid_hex_color(color: str) -> bool:
        """Validate HEX color format."""
        pattern = r"^#[0-9A-Fa-f]{6}$"
        return bool(re.match(pattern, color))

    def to_rgb(self) -> tuple:
        """Convert HEX to RGB tuple."""
        hex_value = self.hex_value.lstrip("#")
        return tuple(int(hex_value[i : i + 2], 16) for i in (0, 2, 4))

    def lighter(self, factor: float = 1.2) -> "Color":
        """
        Create a lighter version of this color.

        Args:
            factor: Lightness factor (1.0 = original, >1.0 = lighter)

        Returns:
            New Color instance with increased brightness
        """
        r, g, b = self.to_rgb()
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        return Color(f"#{r:02X}{g:02X}{b:02X}")

    def darker(self, factor: float = 0.8) -> "Color":
        """
        Create a darker version of this color.

        Args:
            factor: Darkness factor (1.0 = original, <1.0 = darker)

        Returns:
            New Color instance with decreased brightness
        """
        r, g, b = self.to_rgb()
        r = max(0, int(r * factor))
        g = max(0, int(g * factor))
        b = max(0, int(b * factor))
        return Color(f"#{r:02X}{g:02X}{b:02X}")
