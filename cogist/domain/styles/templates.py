"""Preset templates for mind map styling.

This module provides factory functions to create default MindMapStyle instances
using the new template + color scheme architecture.
"""

from .extended_styles import (
    BackgroundStyle,
    BorderStyle,
    ColorScheme,
    NodeColorConfig,
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
            max_text_width=300,  # ROOT nodes: widest (300px)
            font_size=22,
            font_weight="Bold",
            font_italic=False,
            font_family="Arial",
            font_underline=False,
            font_strikeout=False,
            shadow_enabled=False,
            shadow_offset_x=2,
            shadow_offset_y=2,
            shadow_blur=4,
            shadow_color=None,
            # Spacing configuration (per-role)
            parent_child_spacing=80.0,  # Root to Primary
            sibling_spacing=60.0,       # Root's children spacing
            # Connector configuration (per-role)
            connector_shape="bezier",
            connector_style="solid",
            line_width=2.0,
            connector_color_index=0,
            connector_brightness=1.0,
            connector_opacity=255,
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
            max_text_width=250,  # PRIMARY nodes: wide (250px)
            font_size=18,
            font_weight="Normal",
            font_italic=False,
            font_family="Arial",
            font_underline=False,
            font_strikeout=False,
            shadow_enabled=False,
            shadow_offset_x=2,
            shadow_offset_y=2,
            shadow_blur=4,
            shadow_color=None,
            # Spacing configuration (per-role)
            parent_child_spacing=80.0,  # Root to Primary
            sibling_spacing=60.0,       # Root's children spacing
            # Connector configuration (per-role)
            connector_shape="bezier",
            connector_style="solid",
            line_width=2.0,
            connector_color=None,
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
            max_text_width=200,  # SECONDARY nodes: medium (200px)
            font_size=16,
            font_weight="Normal",
            font_italic=False,
            font_family="Arial",
            font_underline=False,
            font_strikeout=False,
            shadow_enabled=False,
            shadow_offset_x=2,
            shadow_offset_y=2,
            shadow_blur=4,
            shadow_color=None,
            # Spacing configuration (per-role)
            parent_child_spacing=60.0,  # Primary to Secondary
            sibling_spacing=45.0,       # Primary's children spacing
            # Connector configuration (per-role)
            connector_shape="bezier",
            connector_style="solid",
            line_width=2.0,
            connector_color=None,
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
            max_text_width=0,  # TERTIARY nodes: unlimited width (no wrap)
            font_size=14,
            font_weight="Normal",
            font_italic=False,
            font_family="Arial",
            font_underline=False,
            font_strikeout=False,
            shadow_enabled=False,
            shadow_offset_x=2,
            shadow_offset_y=2,
            shadow_blur=4,
            shadow_color=None,
            # Spacing configuration (per-role)
            parent_child_spacing=40.0,  # Secondary to Tertiary
            sibling_spacing=35.0,       # Secondary's children spacing
            # Connector configuration (per-role)
            connector_shape="bezier",
            connector_style="solid",
            line_width=2.0,
            connector_color=None,
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
        role_configs={
            NodeRole.ROOT: NodeColorConfig(text_color=None, connector_color=None),
            NodeRole.PRIMARY: NodeColorConfig(text_color=None, connector_color=None),
            NodeRole.SECONDARY: NodeColorConfig(text_color=None, connector_color=None),
            NodeRole.TERTIARY: NodeColorConfig(text_color=None, connector_color=None),
        },
        canvas_bg_color="#FFFFFFFF",
        edge_color="#FF666666",
    )

    # Create MindMapStyle with all style data explicitly initialized
    style = MindMapStyle(
        name="Default",
        # === Global spacing configuration ===
        parent_child_spacing=80.0,  # Horizontal spacing between parent and child
        sibling_spacing=60.0,       # Vertical spacing between siblings
    )

    # Store resolved references (in production, these would come from registries)
    style.resolved_template = template
    style.resolved_color_scheme = color_scheme
    style.canvas_bg_color = color_scheme.canvas_bg_color

    return style


# Note: Template and ColorScheme registries will be loaded from files in the future.
# Currently, only create_default_template() is used for initialization.
