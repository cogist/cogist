"""Position value object."""

from dataclasses import dataclass


@dataclass
class Position:
    """Represents a 2D position.
    
    Attributes:
        x: X coordinate
        y: Y coordinate
    """
    x: float
    y: float
