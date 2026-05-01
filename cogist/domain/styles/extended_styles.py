"""Extended style data structures for advanced styling support.

This module contains the new style system architecture that supports:
- Template and ColorScheme separation
- Role-based styling (ROOT, PRIMARY, SECONDARY, etc.)
- Abstract spacing levels for layout compatibility
- Advanced features: SVG borders, textures, gradients, shadows, etc.
"""

from dataclasses import dataclass, field

from .enums import NodeRole, SpacingLevel


@dataclass
class SpacingConfig:
    """Spacing configuration using abstract levels for layout compatibility."""

    parent_child_spacing: SpacingLevel = SpacingLevel.NORMAL
    sibling_spacing: SpacingLevel = SpacingLevel.NORMAL


@dataclass
class NodeShape:
    """Node shape configuration (supports basic and custom shapes).

    Shape categories:
    - Container shapes (with background fill): rounded_rect, rect, circle, ellipse
    - Decorative line shapes (transparent background): bottom_line, left_line
    - No shape: none (pure text only)
    """

    shape_type: str = "basic"  # basic / svg / custom

    # Basic shape
    # Container shapes: rounded_rect, rect, circle, ellipse
    # Decorative lines: bottom_line, left_line
    # No shape: none
    basic_shape: str = "rounded_rect"
    border_radius: int = 8  # Corner radius (only for container shapes)

    # SVG shape (for fan, scroll, etc.)
    svg_path: str | None = None  # SVG path data

    # Custom shape parameters
    custom_params: dict[str, float] = field(default_factory=dict)


@dataclass
class BackgroundStyle:
    """Background style (supports solid, gradient, texture, image)."""

    bg_type: str = "solid"  # solid / gradient / texture / image

    # New fields for color pool reference and adjustment
    enabled: bool = True  # Whether to show background
    color_index: int = 0  # Index into ColorScheme.color_pool
    brightness: float = 1.0  # Brightness adjustment (0.5-1.5)
    opacity: int = 255  # Opacity adjustment (0-255)

    # Gradient background
    gradient_type: str | None = None  # linear / radial
    gradient_colors: list[str] | None = None
    gradient_angle: float = 0.0

    # Texture background (paper, canvas, wood)
    texture_type: str | None = None  # paper / canvas / wood / custom
    texture_opacity: float = 0.3  # Texture opacity

    # Image background
    image_path: str | None = None
    image_scale: float = 1.0
    image_opacity: float = 1.0


@dataclass
class BorderStyle:
    """Border style (supports simple, SVG, image, gradient borders)."""

    # Basic border
    border_type: str = "simple"  # simple / svg / image / gradient
    border_width: int = 0
    border_radius: int = 8

    # New fields for color pool reference and adjustment
    enabled: bool = True  # Whether to show border
    color_index: int = 0  # Index into ColorScheme.color_pool
    brightness: float = 1.0  # Brightness adjustment (0.5-1.5)
    opacity: int = 255  # Opacity adjustment (0-255)

    # Simple border style
    border_style: str = "solid"  # solid / dashed / dotted / dash_dot

    # SVG border (Chinese cloud patterns, etc.)
    svg_path: str | None = None  # SVG path data
    svg_repeat: bool = False  # Whether to repeat/tile

    # Image border (ink effect, etc.)
    image_path: str | None = None  # Image path
    image_scale: float = 1.0  # Scale factor

    # Gradient border
    gradient_type: str | None = None  # linear / radial
    gradient_colors: list[str] | None = None
    gradient_angle: float = 0.0  # Gradient angle


@dataclass
class EdgeStyle:
    """Edge style (supports simple and complex styles)."""

    # Basic edge
    connector_shape: str = "bezier"  # bezier / straight / orthogonal
    line_width: float = 2.0

    # Simple line style
    line_style: str = "solid"  # solid / dashed / dotted / dash_dot

    # Gradient configuration (only for bezier)
    enable_gradient: bool = True  # Enable width gradient for bezier curves
    gradient_ratio: float = 0.5  # end_width / start_width ratio (0.3-1.0)

    # Gradient edge (color gradient, not width)
    gradient_enabled: bool = False
    gradient_start_color: str | None = None
    gradient_end_color: str | None = None

    # Brush stroke effect (Chinese style)
    brush_effect: bool = False
    brush_pressure: float = 1.0  # Pressure value (affects thickness variation)
    brush_texture: str | None = None  # Brush texture

    # Arrow decorations
    arrow_start: str | None = None  # none / triangle / circle / diamond / custom
    arrow_end: str | None = None
    arrow_svg: str | None = None  # Custom SVG arrow (Chinese knot, flower, etc.)

    # Dash pattern
    dash_pattern: list[float] | None = None  # [dash_length, gap_length, ...]


@dataclass
class EdgeConfig:
    """Edge configuration (includes style and layout)."""

    # Default style
    default_style: EdgeStyle = field(default_factory=EdgeStyle)

    # Custom styles by role (optional)
    role_styles: dict[NodeRole, EdgeStyle] = field(default_factory=dict)


@dataclass
class RoleStyle:
    """Flat role-based style configuration (NEW ARCHITECTURE).

    All style fields at the same level. Colors reference ColorScheme.color_pool
    via index, with brightness and opacity adjustments.

    This replaces the old nested structure (RoleBasedStyle with BackgroundStyle,
    BorderStyle, etc.) for a simpler, more maintainable design.
    """

    role: NodeRole

    # === Shape ===
    shape_type: str = "basic"  # basic / svg / custom
    basic_shape: str = "rounded_rect"  # rounded_rect, rect, circle, ellipse, bottom_line, left_line, none
    border_radius: int = 8

    # === Background (flat fields) ===
    bg_enabled: bool = True
    bg_color_index: int = 0  # Index into color_pool
    bg_brightness: float = 1.0  # 0.5-1.5
    bg_opacity: int = 255  # 0-255

    # === Border (flat fields) ===
    border_enabled: bool = True
    border_width: int = 0
    border_color_index: int = 0  # Index into color_pool
    border_brightness: float = 1.0
    border_opacity: int = 255
    border_style: str = "solid"  # solid / dashed / dotted / dash_dot

    # === Connector (flat fields) ===
    connector_shape: str = "bezier"  # bezier / straight / orthogonal / rounded_orthogonal
    connector_color_index: int = 0  # Index into color_pool
    connector_brightness: float = 1.0
    connector_opacity: int = 255
    line_width: float = 2.0
    connector_style: str = "solid"  # solid / dashed / dotted

    # === Text ===
    text_color: str | None = None  # Auto-calculated if None (based on background luminance)
    font_size: int = 14
    font_weight: str = "Normal"  # Normal / Bold / Light
    font_italic: bool = False
    font_family: str = "Arial"
    font_underline: bool = False
    font_strikeout: bool = False

    # === Shadow ===
    shadow_enabled: bool = False
    shadow_offset_x: int = 2
    shadow_offset_y: int = 2
    shadow_blur: int = 4
    shadow_color: str | None = None  # Default: none (black semi-transparent if enabled)

    # === Spacing ===
    parent_child_spacing: float = 80.0
    sibling_spacing: float = 60.0

    # === Padding ===
    padding_w: int = 12
    padding_h: int = 8
    max_text_width: int = 250


# === DEPRECATED CLASSES (Will be removed in future versions) ===
# These classes are kept temporarily for migration purposes only.
# Use RoleStyle instead.

@dataclass
class RoleBasedStyle:
    """DEPRECATED: Use RoleStyle instead.

    Old nested structure that will be removed. Kept for backward compatibility during migration.
    """
    role: NodeRole
    shape: NodeShape = field(default_factory=NodeShape)
    background: BackgroundStyle = field(default_factory=BackgroundStyle)
    border: BorderStyle = field(default_factory=BorderStyle)
    padding_w: int = 12
    padding_h: int = 8
    max_text_width: int = 250
    font_size: int = 14
    font_weight: str = "Normal"
    font_italic: bool = False
    font_family: str = "Arial"
    font_underline: bool = False
    font_strikeout: bool = False
    shadow_enabled: bool = False
    shadow_offset_x: int = 2
    shadow_offset_y: int = 2
    shadow_blur: int = 4
    shadow_color: str | None = None
    parent_child_spacing: float = 80.0
    sibling_spacing: float = 60.0
    text_color: str | None = None
    connector_shape: str = "bezier"
    connector_style: str = "solid"
    line_width: float = 2.0
    connector_color_index: int = 0
    connector_brightness: float = 1.0
    connector_opacity: int = 255


@dataclass
class ColorScheme:
    """Color scheme (pure color pool only).

    Contains only the color palette. No style properties.

    NOTE: Colors should be loaded from JSON configuration files,
    not hardcoded here. This default is only for backward compatibility.
    """

    name: str
    description: str

    # Color pool (8 branch colors using HexArgb format)
    # Indices [0-7]: Branch colors for rainbow mode
    # NOTE: Colors are now loaded from assets/color_schemes/*.json
    color_pool: list[str] = field(default_factory=list)  # Renamed from branch_colors

    # Special colors dictionary
    special_colors: dict[str, str] = field(default_factory=dict)

    # Optional defaults
    default_use_rainbow_branches: bool | None = None


@dataclass
class Template:
    """DEPRECATED: Use MindMapStyle directly.

    Old template structure. Kept for backward compatibility during migration.
    New architecture uses MindMapStyle with embedded role_styles.
    """

    name: str
    description: str

    # Role styles (font, shape, border, etc., without colors)
    role_styles: dict[NodeRole, RoleBasedStyle]

    # Spacing configuration (abstract levels)
    spacing: SpacingConfig = field(default_factory=SpacingConfig)

    # Recommended default color scheme
    default_color_scheme: str = "default"

    # Recommended layout (optional)
    recommended_layout: str | None = None  # LayoutAlgorithm name


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
