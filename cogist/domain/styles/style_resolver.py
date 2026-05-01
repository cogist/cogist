"""Style resolver - merges templates and color schemes into final styles."""

from .enums import NodeRole
from .extended_styles import (
    ColorScheme,
    RoleStyle,  # Flat role-based style
)
from .style_config import MindMapStyle


def serialize_role_style(role_style: RoleStyle) -> dict:
    """Serialize a single RoleStyle to dict (flat structure)."""
    return {
        "role": role_style.role.value,
        # Shape
        "shape_type": role_style.shape_type,
        "basic_shape": role_style.basic_shape,
        "border_radius": role_style.border_radius,
        # Background
        "bg_enabled": role_style.bg_enabled,
        "bg_color_index": role_style.bg_color_index,
        "bg_brightness": role_style.bg_brightness,
        "bg_opacity": role_style.bg_opacity,
        # Border
        "border_enabled": role_style.border_enabled,
        "border_width": role_style.border_width,
        "border_color_index": role_style.border_color_index,
        "border_brightness": role_style.border_brightness,
        "border_opacity": role_style.border_opacity,
        "border_style": role_style.border_style,
        # Connector
        "connector_shape": role_style.connector_shape,
        "connector_color_index": role_style.connector_color_index,
        "connector_brightness": role_style.connector_brightness,
        "connector_opacity": role_style.connector_opacity,
        "line_width": role_style.line_width,
        "connector_style": role_style.connector_style,
        # Text
        "text_color": role_style.text_color,
        "font_size": role_style.font_size,
        "font_weight": role_style.font_weight,
        "font_italic": role_style.font_italic,
        "font_family": role_style.font_family,
        "font_underline": role_style.font_underline,
        "font_strikeout": role_style.font_strikeout,
        # Shadow
        "shadow_enabled": role_style.shadow_enabled,
        "shadow_offset_x": role_style.shadow_offset_x,
        "shadow_offset_y": role_style.shadow_offset_y,
        "shadow_blur": role_style.shadow_blur,
        "shadow_color": role_style.shadow_color,
        # Spacing
        "parent_child_spacing": role_style.parent_child_spacing,
        "sibling_spacing": role_style.sibling_spacing,
        # Padding
        "padding_w": role_style.padding_w,
        "padding_h": role_style.padding_h,
        "max_text_width": role_style.max_text_width,
    }


def deserialize_role_style(data: dict) -> RoleStyle:
    """Deserialize RoleStyle from dict (flat structure).

    All fields are required - no defaults. Values must come from template files.
    """
    return RoleStyle(
        role=NodeRole(data["role"]),
        # Shape
        shape_type=data["shape_type"],
        basic_shape=data["basic_shape"],
        border_radius=data["border_radius"],
        # Background
        bg_enabled=data["bg_enabled"],
        bg_color_index=data["bg_color_index"],
        bg_brightness=data["bg_brightness"],
        bg_opacity=data["bg_opacity"],
        # Border
        border_enabled=data["border_enabled"],
        border_width=data["border_width"],
        border_color_index=data["border_color_index"],
        border_brightness=data["border_brightness"],
        border_opacity=data["border_opacity"],
        border_style=data["border_style"],
        # Connector
        connector_shape=data["connector_shape"],
        connector_color_index=data["connector_color_index"],
        connector_brightness=data["connector_brightness"],
        connector_opacity=data["connector_opacity"],
        line_width=data["line_width"],
        connector_style=data["connector_style"],
        # Text
        text_color=data.get("text_color"),  # Optional
        font_size=data["font_size"],
        font_weight=data["font_weight"],
        font_italic=data["font_italic"],
        font_family=data["font_family"],
        font_underline=data["font_underline"],
        font_strikeout=data["font_strikeout"],
        # Shadow
        shadow_enabled=data["shadow_enabled"],
        shadow_offset_x=data["shadow_offset_x"],
        shadow_offset_y=data["shadow_offset_y"],
        shadow_blur=data["shadow_blur"],
        shadow_color=data.get("shadow_color"),  # Optional
        # Spacing
        parent_child_spacing=data["parent_child_spacing"],
        sibling_spacing=data["sibling_spacing"],
        # Padding
        padding_w=data["padding_w"],
        padding_h=data["padding_h"],
        max_text_width=data["max_text_width"],
    )


def serialize_style(style_config: MindMapStyle) -> dict:
    """Serialize complete MindMapStyle to JSON-compatible dict.

    New architecture: Single self-contained structure with embedded
    color pool and role configurations.

    Args:
        style_config: The style configuration to serialize

    Returns:
        Dictionary representation suitable for JSON serialization
    """
    return {
        "name": style_config.name,
        "use_rainbow_branches": style_config.use_rainbow_branches,
        "color_pool": style_config.color_pool,  # Renamed from branch_colors
        "special_colors": style_config.special_colors,
        "role_styles": {
            role.value: serialize_role_style(role_style)
            for role, role_style in style_config.role_styles.items()
        },
    }


def deserialize_style(data: dict) -> MindMapStyle:
    """Deserialize MindMapStyle from JSON-compatible dict.

    New architecture: Self-contained structure with all data embedded.
    All fields are required - no defaults. Values must come from template files.

    NOTE: Template files may not include color_pool and special_colors.
    These will be loaded separately from color scheme files.

    Args:
        data: Dictionary representation from JSON

    Returns:
        MindMapStyle instance
    """
    style = MindMapStyle(
        name=data["name"],
        use_rainbow_branches=data.get("use_rainbow_branches", False),
        color_pool=data.get("color_pool", []),  # May be empty in template files
        special_colors=data.get("special_colors", {}),  # May be empty in template files
        role_styles={},  # Will be populated below
    )

    # Deserialize role styles
    if "role_styles" in data:
        for role_str, role_data in data["role_styles"].items():
            role = NodeRole(role_str)
            style.role_styles[role] = deserialize_role_style(role_data)

    return style


def serialize_color_scheme(scheme: ColorScheme) -> dict:
    """Serialize ColorScheme to JSON-compatible dict."""
    return {
        "name": scheme.name,
        "description": scheme.description,
        "color_pool": scheme.color_pool,  # Renamed from branch_colors
        "special_colors": scheme.special_colors,
    }


def deserialize_color_scheme(data: dict) -> ColorScheme:
    """Deserialize ColorScheme from JSON-compatible dict.

    All fields are required - no defaults. Values must come from JSON files.
    """
    return ColorScheme(
        name=data["name"],
        description=data["description"],
        color_pool=data["color_pool"],
        special_colors=data["special_colors"],
    )


# DEPRECATED: EdgeConfig serialization removed (not used in current architecture)
# Use RoleStyle.connector_* fields instead.


def serialize_edge_style(style) -> dict:
    """Serialize EdgeStyle to dict."""
    return {
        "connector_shape": style.connector_shape,
        "line_width": style.line_width,
        "line_style": style.line_style,
        "enable_gradient": style.enable_gradient,
        "gradient_ratio": style.gradient_ratio,
        "gradient_enabled": style.gradient_enabled,
        "gradient_start_color": style.gradient_start_color,
        "gradient_end_color": style.gradient_end_color,
        "brush_effect": style.brush_effect,
        "brush_pressure": style.brush_pressure,
        "brush_texture": style.brush_texture,
        "arrow_start": style.arrow_start,
        "arrow_end": style.arrow_end,
        "arrow_svg": style.arrow_svg,
        "dash_pattern": style.dash_pattern,
    }


def deserialize_edge_style(data: dict):
    """Deserialize EdgeStyle from dict.

    All fields are required - no defaults. Values must come from template files.
    """
    from .extended_styles import EdgeStyle

    return EdgeStyle(
        connector_shape=data["connector_shape"],
        line_width=data["line_width"],
        line_style=data["line_style"],
        enable_gradient=data["enable_gradient"],
        gradient_ratio=data["gradient_ratio"],
        gradient_enabled=data["gradient_enabled"],
        gradient_start_color=data.get("gradient_start_color"),  # Optional
        gradient_end_color=data.get("gradient_end_color"),  # Optional
        brush_effect=data["brush_effect"],
        brush_pressure=data["brush_pressure"],
        brush_texture=data.get("brush_texture"),  # Optional
        arrow_start=data.get("arrow_start"),  # Optional
        arrow_end=data.get("arrow_end"),  # Optional
        arrow_svg=data.get("arrow_svg"),  # Optional
        dash_pattern=data.get("dash_pattern"),  # Optional
    )



