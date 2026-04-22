"""Preset templates for mind map styling.

This module provides factory functions to create default MindMapStyle instances
using the new template + color scheme architecture.
"""

from .extended_styles import (
    BackgroundStyle,
    BorderStyle,
    ColorScheme,
    NodeRole,
    NodeShape,
    RoleBasedStyle,
    SpacingConfig,
    SpacingLevel,
    Template,
)
from .style_config import LegacyEdgeConfig, MindMapStyle


def create_default_template() -> MindMapStyle:
    """Create a default MindMapStyle with basic template and color scheme.

    Returns:
        MindMapStyle instance with resolved template and color scheme
    """
    # Create a simple default template
    role_styles = {
        NodeRole.ROOT: RoleBasedStyle(
            role=NodeRole.ROOT,
            shape=NodeShape(
                shape_type="basic",
                basic_shape="rounded_rect",
                border_radius=12,
            ),
            background=BackgroundStyle(bg_type="solid"),
            border=BorderStyle(
                border_type="simple",
                border_width=3,
                border_radius=12,
                border_style="solid",
            ),
            padding_w=20,
            padding_h=16,
            font_size=22,
            font_weight="Bold",
            font_style="Normal",
            font_family="Arial",
            font_underline=False,
            font_strikeout=False,
            shadow_enabled=False,
            shadow_offset_x=2,
            shadow_offset_y=2,
            shadow_blur=4,
            shadow_color=None,
        ),
        NodeRole.PRIMARY: RoleBasedStyle(
            role=NodeRole.PRIMARY,
            shape=NodeShape(
                shape_type="basic",
                basic_shape="rounded_rect",
                border_radius=8,
            ),
            background=BackgroundStyle(bg_type="solid"),
            border=BorderStyle(
                border_type="simple",
                border_width=2,
                border_radius=8,
                border_style="solid",
            ),
            padding_w=16,
            padding_h=12,
            font_size=18,
            font_weight="Normal",
            font_style="Normal",
            font_family="Arial",
            font_underline=False,
            font_strikeout=False,
            shadow_enabled=False,
            shadow_offset_x=2,
            shadow_offset_y=2,
            shadow_blur=4,
            shadow_color=None,
        ),
        NodeRole.SECONDARY: RoleBasedStyle(
            role=NodeRole.SECONDARY,
            shape=NodeShape(
                shape_type="basic",
                basic_shape="rounded_rect",
                border_radius=6,
            ),
            background=BackgroundStyle(bg_type="solid"),
            border=BorderStyle(
                border_type="simple",
                border_width=2,
                border_radius=6,
                border_style="solid",
            ),
            padding_w=12,
            padding_h=10,
            font_size=16,
            font_weight="Normal",
            font_style="Normal",
            font_family="Arial",
            font_underline=False,
            font_strikeout=False,
            shadow_enabled=False,
            shadow_offset_x=2,
            shadow_offset_y=2,
            shadow_blur=4,
            shadow_color=None,
        ),
        NodeRole.TERTIARY: RoleBasedStyle(
            role=NodeRole.TERTIARY,
            shape=NodeShape(
                shape_type="basic",
                basic_shape="rounded_rect",
                border_radius=4,
            ),
            background=BackgroundStyle(bg_type="solid"),
            border=BorderStyle(
                border_type="simple",
                border_width=1,
                border_radius=4,
                border_style="solid",
            ),
            padding_w=10,
            padding_h=8,
            font_size=14,
            font_weight="Normal",
            font_style="Normal",
            font_family="Arial",
            font_underline=False,
            font_strikeout=False,
            shadow_enabled=False,
            shadow_offset_x=2,
            shadow_offset_y=2,
            shadow_blur=4,
            shadow_color=None,
        ),
    }

    template = Template(
        name="default",
        description="Default template with rounded rectangles",
        role_styles=role_styles,
        spacing=SpacingConfig(
            parent_child_spacing=SpacingLevel.NORMAL,
            sibling_spacing=SpacingLevel.NORMAL,
        ),
        default_color_scheme="default",
    )

    # Create a default color scheme
    color_scheme = ColorScheme(
        name="default",
        description="Default blue color scheme",
        node_colors={
            NodeRole.ROOT: "#FF2196F3",
            NodeRole.PRIMARY: "#FF4CAF50",
            NodeRole.SECONDARY: "#FFFF9800",
            NodeRole.TERTIARY: "#FF9E9E9E",
        },
        # Border colors (same as node colors for decorative lines)
        border_colors={
            NodeRole.ROOT: "#FF2196F3",
            NodeRole.PRIMARY: "#FF4CAF50",
            NodeRole.SECONDARY: "#FFFF9800",
            NodeRole.TERTIARY: "#FF9E9E9E",
        },
        canvas_bg_color="#FFFFFFFF",
        edge_color="#FF666666",
    )

    # Create MindMapStyle with all style data explicitly initialized
    style = MindMapStyle(
        name="Default",
        template_name="default",
        color_scheme_name="default",
        # === Global spacing configuration (fallback for non-per-depth scenarios) ===
        parent_child_spacing=80.0,  # Horizontal spacing between parent and child
        sibling_spacing=60.0,       # Vertical spacing between siblings
        # === Per-depth spacing configuration (4 levels: root, level1, level2, level3+) ===
        level_spacing_by_depth={
            0: 80.0,   # Root → Level 1
            1: 60.0,   # Level 1 → Level 2
            2: 40.0,   # Level 2 → Level 3
            3: 30.0,   # Level 3+ → Level 4+ (all deeper levels)
        },
        sibling_spacing_by_depth={
            0: 60.0,   # Level 1 siblings
            1: 45.0,   # Level 2 siblings
            2: 35.0,   # Level 3 siblings
            3: 28.0,   # Level 3+ siblings (all deeper levels)
        },
        # === Per-depth connector configuration (4 levels: root, level1, level2, level3+) ===
        # Note: enable_gradient is automatically determined by connector_shape
        connector_config_by_depth={
            0: {"connector_shape": "bezier", "connector_style": "solid", "line_width": 2.0, "color": "#666666", "gradient_ratio": 0.33},  # Root → Level 1
            1: {"connector_shape": "bezier", "connector_style": "solid", "line_width": 2.0, "color": "#666666", "gradient_ratio": 0.33},  # Level 1 → Level 2
            2: {"connector_shape": "bezier", "connector_style": "solid", "line_width": 2.0, "color": "#666666", "gradient_ratio": 0.33},  # Level 2 → Level 3
            3: {"connector_shape": "bezier", "connector_style": "solid", "line_width": 2.0, "color": "#666666", "gradient_ratio": 0.33},  # Level 3+ (all deeper)
        },
        # === Legacy edge configuration (backward compatibility) ===
        # Note: enable_gradient and gradient_ratio are now in connector_config_by_depth
        edge=LegacyEdgeConfig(
            connector_shape="bezier",
            connector_style="solid",
            start_width=6.0,
            end_width=2.0,
            color="#666666",
        ),
    )

    # Store resolved references (in production, these would come from registries)
    style.resolved_template = template
    style.resolved_color_scheme = color_scheme
    style.canvas_bg_color = color_scheme.canvas_bg_color

    return style


# Note: Template and ColorScheme registries will be loaded from files in the future.
# Currently, only create_default_template() is used for initialization.
