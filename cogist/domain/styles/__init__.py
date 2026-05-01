"""Style system for mind map visualization."""

from .enums import NodeRole, PriorityLevel, SpacingLevel
from .extended_styles import (
    ColorScheme,
    EdgeConfig,
    EdgeStyle,
    NodeShape,
    RoleStyle,  # Flat role-based style
    SpacingConfig,
)
from .style_config import MindMapStyle
from .style_resolver import (
    deserialize_color_scheme,
    deserialize_style,
    serialize_color_scheme,
    serialize_style,
)

# Note: create_default_template() has been removed.
# - Production code should load templates from JSON files (template_loader.py)
# - Test code should use _create_test_template() helper in test files

__all__ = [
    # Enums
    "PriorityLevel",
    "NodeRole",
    "SpacingLevel",

    # Extended styles (new architecture - authoritative)
    "SpacingConfig",
    "NodeShape",
    "EdgeStyle",
    "EdgeConfig",
    "RoleStyle",  # Flat role-based style (authoritative)
    "ColorScheme",

    # Style resolver
    "serialize_style",
    "deserialize_style",
    "serialize_color_scheme",
    "deserialize_color_scheme",

    # Main style configuration
    "MindMapStyle",
]
