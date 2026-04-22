"""Border drawing strategies package.

Provides strategy pattern implementation for node border/shape rendering.
"""

from .base import BorderStrategy
from .container_borders import CircleBorder, RoundedRectBorder
from .decorative_lines import BottomLineBorder, LeftLineBorder
from .registry import BorderStrategyRegistry

__all__ = [
    "BorderStrategy",
    "RoundedRectBorder",
    "CircleBorder",
    "BottomLineBorder",
    "LeftLineBorder",
    "BorderStrategyRegistry",
]
