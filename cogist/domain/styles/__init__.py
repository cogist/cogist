"""Style system for mind map visualization."""

from .enums import NodeRole, PriorityLevel, SpacingLevel
from .extended_styles import (
    BackgroundStyle,
    BorderStyle,
    ColorScheme,
    EdgeConfig,
    EdgeStyle,
    NodeShape,
    RoleBasedStyle,  # DEPRECATED: Use RoleStyle
    RoleStyle,  # NEW: Flat role-based style
    SpacingConfig,
    Template,  # DEPRECATED: Use MindMapStyle directly
)
from .style_config import MindMapStyle
from .style_resolver import (
    deserialize_color_scheme,
    deserialize_style,
    deserialize_template,
    serialize_color_scheme,
    serialize_style,
    serialize_template,
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
    "BackgroundStyle",
    "BorderStyle",
    "EdgeStyle",
    "EdgeConfig",
    "RoleBasedStyle",  # DEPRECATED: Use RoleStyle
    "RoleStyle",  # NEW: Flat role-based style (authoritative)
    "ColorScheme",
    "Template",  # DEPRECATED: Use MindMapStyle directly

    # Style resolver
    "serialize_style",
    "deserialize_style",
    "serialize_template",
    "deserialize_template",
    "serialize_color_scheme",
    "deserialize_color_scheme",

    # Main style configuration
    "MindMapStyle",
]
