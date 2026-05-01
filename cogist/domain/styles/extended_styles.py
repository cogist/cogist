"""Extended style data structures for advanced styling support.

This module contains the new style system architecture that supports:
- Template and ColorScheme separation
- Role-based styling (ROOT, PRIMARY, SECONDARY, etc.)
- Abstract spacing levels for layout compatibility
- Advanced features: SVG borders, textures, gradients, shadows, etc.
"""

from dataclasses import dataclass

from .enums import NodeRole

# === DEPRECATED CLASSES (Removed) ===
# The following classes have been removed as they are no longer used:
# - SpacingConfig: Replaced by direct fields in RoleStyle
# - NodeShape: Replaced by flat fields in RoleStyle (shape_type, basic_shape, etc.)
# - BackgroundStyle: Replaced by flat fields in RoleStyle (bg_enabled, bg_color_index, etc.)
# - BorderStyle: Replaced by flat fields in RoleStyle (border_enabled, border_width, etc.)
# - RoleBasedStyle: Replaced by RoleStyle (flat structure)
# - EdgeConfig: Not used in current architecture
# - Template: Replaced by MindMapStyle + ColorScheme separation
#
# Use RoleStyle and MindMapStyle instead.


@dataclass
class EdgeStyle:
    """Edge style (supports simple and complex styles).

    IMPORTANT: NO hardcoded default values! All defaults must come from template files.
    """

    # Basic edge
    connector_shape: str
    line_width: float

    # Simple line style
    line_style: str

    # Gradient configuration (only for bezier)
    enable_gradient: bool
    gradient_ratio: float

    # Gradient edge (color gradient, not width)
    gradient_enabled: bool
    gradient_start_color: str | None
    gradient_end_color: str | None

    # Brush stroke effect (Chinese style)
    brush_effect: bool
    brush_pressure: float
    brush_texture: str | None

    # Arrow decorations
    arrow_start: str | None
    arrow_end: str | None
    arrow_svg: str | None

    # Dash pattern
    dash_pattern: list[float] | None


@dataclass
class RoleStyle:
    """Flat role-based style configuration (NEW ARCHITECTURE).

    All style fields at the same level. Colors reference ColorScheme.color_pool
    via index, with brightness and opacity adjustments.

    This replaces the old nested structure (RoleBasedStyle with BackgroundStyle,
    BorderStyle, etc.) for a simpler, more maintainable design.

    IMPORTANT: NO hardcoded default values! All defaults must come from template files.
    """

    role: NodeRole

    # === Shape ===
    shape_type: str
    basic_shape: str
    border_radius: int

    # === Background (flat fields) ===
    bg_enabled: bool
    bg_color_index: int
    bg_brightness: float
    bg_opacity: int

    # === Border (flat fields) ===
    border_enabled: bool
    border_width: int
    border_color_index: int
    border_brightness: float
    border_opacity: int
    border_style: str

    # === Connector (flat fields) ===
    connector_shape: str
    connector_color_index: int
    connector_brightness: float
    connector_opacity: int
    line_width: float
    connector_style: str

    # === Text ===
    text_color: str | None
    font_size: int
    font_weight: str
    font_italic: bool
    font_family: str
    font_underline: bool
    font_strikeout: bool

    # === Shadow ===
    shadow_enabled: bool
    shadow_offset_x: int
    shadow_offset_y: int
    shadow_blur: int
    shadow_color: str | None

    # === Spacing ===
    parent_child_spacing: float
    sibling_spacing: float

    # === Padding ===
    padding_w: int
    padding_h: int
    max_text_width: int


# === DEPRECATED CLASSES (Will be removed in future versions) ===
# These classes are kept temporarily for migration purposes only.
# Use RoleStyle instead.

@dataclass
class ColorScheme:
    """Color scheme (pure color pool only).

    Contains only the color palette. No style properties.

    IMPORTANT: NO hardcoded default values! All colors must come from JSON files.
    """

    name: str
    description: str

    # Color pool (8 branch colors using HexArgb format)
    # Indices [0-7]: Branch colors for rainbow mode
    color_pool: list[str]

    # Special colors dictionary
    special_colors: dict[str, str]


# Import MindMapStyle from style_config to avoid circular imports
# MindMapStyle will be updated to use template_name and color_scheme_name


def get_rainbow_branch_color(branch_idx: int, color_pool: list[str]) -> str:
    """Get color for a rainbow branch by index.

    Args:
        branch_idx: Index of the branch (0-based)
        color_pool: List of available colors

    Returns:
        Color string in hex format
    """
    if not color_pool:
        return "#FF666666"  # Default gray color

    # Rainbow branches only use indices 0-7 (first 8 colors)
    pool_size = min(8, len(color_pool))

    # Cycle through colors if more branches than colors
    return color_pool[branch_idx % pool_size]
