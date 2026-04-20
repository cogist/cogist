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
from .style_config import MindMapStyle


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
            font_family="Arial",
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
            font_family="Arial",
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
            font_family="Arial",
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
            font_family="Arial",
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
            NodeRole.ROOT: "#2196F3",
            NodeRole.PRIMARY: "#4CAF50",
            NodeRole.SECONDARY: "#FF9800",
            NodeRole.TERTIARY: "#9E9E9E",
        },
        canvas_bg_color="#FFFFFF",
        edge_color="#666666",
    )

    # Create MindMapStyle with references
    style = MindMapStyle(
        name="Default",
        template_name="default",
        color_scheme_name="default",
    )

    # Store resolved references (in production, these would come from registries)
    style.resolved_template = template
    style.resolved_color_scheme = color_scheme
    style.canvas_bg_color = color_scheme.canvas_bg_color

    return style
