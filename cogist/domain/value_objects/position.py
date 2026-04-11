"""
Position Value Object - Domain Layer

Immutable value object representing 2D coordinates.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    """
    Position value object.

    Represents a 2D coordinate in the mind map space.

    Attributes:
        x: X coordinate
        y: Y coordinate
    """

    x: float = 0.0
    y: float = 0.0

    def __post_init__(self):
        """Validate coordinates after initialization."""
        if not isinstance(self.x, (int, float)):
            raise ValueError("x must be a number")
        if not isinstance(self.y, (int, float)):
            raise ValueError("y must be a number")
