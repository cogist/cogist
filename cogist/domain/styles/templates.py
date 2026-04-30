"""Preset templates for mind map styling.

This module provides factory functions to create default MindMapStyle instances
using the new flat RoleStyle architecture.
"""

from .enums import NodeRole
from .extended_styles import RoleStyle
from .style_config import DEFAULT_BRANCH_COLORS, MindMapStyle


def create_default_template() -> MindMapStyle:
    """Create a default MindMapStyle with flat RoleStyle structure.

    Returns:
        MindMapStyle instance with embedded role configurations
    """
    style = MindMapStyle(
        name="Default",
        use_rainbow_branches=False,
        branch_colors=DEFAULT_BRANCH_COLORS.copy(),
    )

    # Create role styles with flat structure
    style.role_styles[NodeRole.ROOT] = RoleStyle(
        role=NodeRole.ROOT,
        shape_type="basic",
        basic_shape="rounded_rect",
        border_radius=12,
        bg_enabled=True,
        bg_color_index=0,  # Use branch_colors[0]
        bg_brightness=1.0,
        bg_opacity=255,
        border_enabled=True,
        border_width=3,
        border_color_index=0,
        border_brightness=1.0,
        border_opacity=255,
        border_style="solid",
        connector_shape="bezier",
        connector_color_index=0,
        connector_brightness=1.0,
        connector_opacity=255,
        line_width=2.0,
        connector_style="solid",
        text_color=None,  # Auto-calculated
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
        parent_child_spacing=80.0,
        sibling_spacing=60.0,
        padding_w=20,
        padding_h=16,
        max_text_width=300,
    )

    style.role_styles[NodeRole.PRIMARY] = RoleStyle(
        role=NodeRole.PRIMARY,
        shape_type="basic",
        basic_shape="rounded_rect",
        border_radius=8,
        bg_enabled=True,
        bg_color_index=0,
        bg_brightness=1.0,
        bg_opacity=255,
        border_enabled=True,
        border_width=2,
        border_color_index=0,
        border_brightness=1.0,
        border_opacity=255,
        border_style="solid",
        connector_shape="bezier",
        connector_color_index=0,
        connector_brightness=1.0,
        connector_opacity=255,
        line_width=2.0,
        connector_style="solid",
        text_color=None,
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
        parent_child_spacing=80.0,
        sibling_spacing=60.0,
        padding_w=16,
        padding_h=12,
        max_text_width=250,
    )

    style.role_styles[NodeRole.SECONDARY] = RoleStyle(
        role=NodeRole.SECONDARY,
        shape_type="basic",
        basic_shape="rounded_rect",
        border_radius=6,
        bg_enabled=True,
        bg_color_index=0,
        bg_brightness=1.0,
        bg_opacity=255,
        border_enabled=True,
        border_width=2,
        border_color_index=0,
        border_brightness=1.0,
        border_opacity=255,
        border_style="solid",
        connector_shape="bezier",
        connector_color_index=0,
        connector_brightness=1.0,
        connector_opacity=255,
        line_width=2.0,
        connector_style="solid",
        text_color=None,
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
        parent_child_spacing=60.0,
        sibling_spacing=45.0,
        padding_w=12,
        padding_h=10,
        max_text_width=200,
    )

    style.role_styles[NodeRole.TERTIARY] = RoleStyle(
        role=NodeRole.TERTIARY,
        shape_type="basic",
        basic_shape="rounded_rect",
        border_radius=4,
        bg_enabled=True,
        bg_color_index=0,
        bg_brightness=1.0,
        bg_opacity=255,
        border_enabled=True,
        border_width=1,
        border_color_index=0,
        border_brightness=1.0,
        border_opacity=255,
        border_style="solid",
        connector_shape="bezier",
        connector_color_index=0,
        connector_brightness=1.0,
        connector_opacity=255,
        line_width=1.5,
        connector_style="solid",
        text_color=None,
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
        parent_child_spacing=50.0,
        sibling_spacing=35.0,
        padding_w=10,
        padding_h=8,
        max_text_width=0,  # Unlimited for TERTIARY
    )

    return style


# Note: Template and ColorScheme registries will be loaded from files in the future.
# Currently, only create_default_template() is used for initialization.
