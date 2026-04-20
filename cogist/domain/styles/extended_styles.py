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
    """Node shape configuration (supports basic and custom shapes)."""
    
    shape_type: str = "basic"  # basic / svg / custom
    
    # Basic shape
    basic_shape: str = "rounded_rect"  # rounded_rect / circle / rect / ellipse / none
    border_radius: int = 8  # Corner radius
    
    # SVG shape (for fan, scroll, etc.)
    svg_path: str | None = None  # SVG path data
    
    # Custom shape parameters
    custom_params: dict[str, float] = field(default_factory=dict)


@dataclass
class BackgroundStyle:
    """Background style (supports solid, gradient, texture, image)."""
    
    bg_type: str = "solid"  # solid / gradient / texture / image
    
    # Solid color (from ColorScheme.node_colors[role])
    
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
    connector_type: str = "bezier"  # straight / orthogonal / bezier / freehand
    line_width: float = 2.0
    
    # Simple line style
    line_style: str = "solid"  # solid / dashed / dotted / dash_dot
    
    # Gradient edge
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
class RoleBasedStyle:
    """Role-based style configuration (without colors).
    
    Colors come from ColorScheme, this only defines geometry and appearance.
    """
    role: NodeRole
    
    # === Node shape ===
    shape: NodeShape = field(default_factory=NodeShape)
    
    # === Background style ===
    background: BackgroundStyle = field(default_factory=BackgroundStyle)
    
    # === Border style ===
    border: BorderStyle = field(default_factory=BorderStyle)
    
    # === Padding ===
    padding_w: int = 12
    padding_h: int = 8
    
    # === Font properties (without colors) ===
    font_size: int = 14
    font_weight: str = "Normal"  # Normal / Bold / Light
    font_style: str = "Normal"  # Normal / Italic
    font_family: str = "Arial"
    
    # === Shadow effect ===
    shadow_enabled: bool = False
    shadow_offset_x: int = 2
    shadow_offset_y: int = 2
    shadow_blur: int = 4
    shadow_color: str | None = None  # Optional, default black semi-transparent
    
    # ❌ Does NOT contain any colors (colors come from ColorScheme)


@dataclass
class ColorScheme:
    """Color scheme (pure color definitions)."""
    
    name: str
    description: str
    
    # Node colors by role
    node_colors: dict[NodeRole, str] = field(default_factory=lambda: {
        NodeRole.ROOT: "#2196F3",
        NodeRole.PRIMARY: "#4CAF50",
        NodeRole.SECONDARY: "#FF9800",
        NodeRole.TERTIARY: "#9E9E9E",
    })
    
    # Border colors (optional, if not provided use darker version of node color)
    border_colors: dict[NodeRole, str] | None = None
    
    # Text colors (optional, if not provided auto-select black/white based on brightness)
    text_colors: dict[NodeRole, str] | None = None
    
    # Branch color pool (for rainbow branches)
    branch_colors: list[str] = field(default_factory=lambda: [
        "#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8",
        "#F7DC6F", "#BB8FCE", "#85C1E2", "#F8B739", "#52B788",
    ])
    
    # Enable rainbow branches
    use_rainbow_branches: bool = False
    
    # Base colors
    canvas_bg_color: str = "#FFFFFF"
    edge_color: str = "#666666"


@dataclass
class Template:
    """Template: Role-based style definitions (without colors)."""
    
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
