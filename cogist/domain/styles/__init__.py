"""Style system for mind map visualization."""

from .enums import NodeRole, PriorityLevel, SpacingLevel
from .extended_styles import (
    BackgroundStyle,
    BorderStyle,
    ColorScheme,
    EdgeConfig,
    EdgeStyle,
    NodeShape,
    RoleBasedStyle,
    SpacingConfig,
    Template,
)
from .style_config import LegacyEdgeConfig, MindMapStyle
from .style_resolver import (
    deserialize_color_scheme,
    deserialize_style,
    deserialize_template,
    resolve_style,
    serialize_color_scheme,
    serialize_style,
    serialize_template,
)
from .templates import (
    create_default_template,
)

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
    "RoleBasedStyle",
    "ColorScheme",
    "Template",

    # Style resolver
    "resolve_style",
    "serialize_style",
    "deserialize_style",
    "serialize_template",
    "deserialize_template",
    "serialize_color_scheme",
    "deserialize_color_scheme",

    # Main style configuration
    "MindMapStyle",
    "LegacyEdgeConfig",  # For backward compatibility

    # Default template creator
    "create_default_template",
]
