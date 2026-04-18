"""Layout algorithms - Domain Layer

Provides layout algorithm implementations and base classes.
"""

from .base import (
    BaseLayout,
    BaseLayoutConfig,
    DefaultLayoutConfig,
    LayoutConfigType,
    LayoutMetadata,
    DEFAULT_LAYOUT_CONFIG,
)
from .default_layout import DefaultLayout
from .registry import LayoutRegistry, layout_registry

__all__ = [
    'BaseLayout',
    'BaseLayoutConfig',
    'DefaultLayoutConfig',
    'LayoutConfigType',
    'LayoutMetadata',
    'DEFAULT_LAYOUT_CONFIG',
    'DefaultLayout',
    'LayoutRegistry',
    'layout_registry',
]
