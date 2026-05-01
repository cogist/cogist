"""Style resolver - merges templates and color schemes into final styles."""

from .enums import NodeRole
from .extended_styles import (
    ColorScheme,
    EdgeConfig,
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
    """Deserialize RoleStyle from dict (flat structure)."""
    return RoleStyle(
        role=NodeRole(data.get("role", "root")),
        # Shape
        shape_type=data.get("shape_type", "basic"),
        basic_shape=data.get("basic_shape", "rounded_rect"),
        border_radius=data.get("border_radius", 8),
        # Background
        bg_enabled=data.get("bg_enabled", True),
        bg_color_index=data.get("bg_color_index", 0),
        bg_brightness=data.get("bg_brightness", 1.0),
        bg_opacity=data.get("bg_opacity", 255),
        # Border
        border_enabled=data.get("border_enabled", True),
        border_width=data.get("border_width", 0),
        border_color_index=data.get("border_color_index", 0),
        border_brightness=data.get("border_brightness", 1.0),
        border_opacity=data.get("border_opacity", 255),
        border_style=data.get("border_style", "solid"),
        # Connector
        connector_shape=data.get("connector_shape", "bezier"),
        connector_color_index=data.get("connector_color_index", 0),
        connector_brightness=data.get("connector_brightness", 1.0),
        connector_opacity=data.get("connector_opacity", 255),
        line_width=data.get("line_width", 2.0),
        connector_style=data.get("connector_style", "solid"),
        # Text
        text_color=data.get("text_color"),
        font_size=data.get("font_size", 14),
        font_weight=data.get("font_weight", "Normal"),
        font_italic=data.get("font_italic", False),
        font_family=data.get("font_family", "Arial"),
        font_underline=data.get("font_underline", False),
        font_strikeout=data.get("font_strikeout", False),
        # Shadow
        shadow_enabled=data.get("shadow_enabled", False),
        shadow_offset_x=data.get("shadow_offset_x", 2),
        shadow_offset_y=data.get("shadow_offset_y", 2),
        shadow_blur=data.get("shadow_blur", 4),
        shadow_color=data.get("shadow_color"),
        # Spacing
        parent_child_spacing=data.get("parent_child_spacing", 80.0),
        sibling_spacing=data.get("sibling_spacing", 60.0),
        # Padding
        padding_w=data.get("padding_w", 12),
        padding_h=data.get("padding_h", 8),
        max_text_width=data.get("max_text_width", 250),
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

    Args:
        data: Dictionary representation from JSON

    Returns:
        MindMapStyle instance
    """
    style = MindMapStyle(
        name=data.get("name", "Default"),
        use_rainbow_branches=data.get("use_rainbow_branches", False),
        color_pool=data.get("color_pool", []),  # Renamed from branch_colors
        special_colors=data.get("special_colors", {}),
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

    Supports both old format (branch_colors) and new format (color_pool).
    """
    # Support backward compatibility: check for old field name
    color_pool = data.get("color_pool") or data.get("branch_colors", [])
    special_colors = data.get("special_colors", {})
    return ColorScheme(
        name=data["name"],
        description=data.get("description", ""),
        color_pool=color_pool,
        special_colors=special_colors,
    )


def serialize_edge_config(edge: EdgeConfig) -> dict:
    """Serialize EdgeConfig to dict."""
    return {
        "default_style": serialize_edge_style(edge.default_style),
        "role_styles": {
            role.value: serialize_edge_style(style)
            for role, style in edge.role_styles.items()
        },
    }


def deserialize_edge_config(data: dict) -> EdgeConfig:
    """Deserialize EdgeConfig from dict."""
    default_style = deserialize_edge_style(data.get("default_style", {}))
    role_styles = {
        NodeRole(role): deserialize_edge_style(style_data)
        for role, style_data in data.get("role_styles", {}).items()
    }

    return EdgeConfig(
        default_style=default_style,
        role_styles=role_styles,
    )


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
    """Deserialize EdgeStyle from dict."""
    from .extended_styles import EdgeStyle

    return EdgeStyle(
        connector_shape=data.get("connector_shape", "bezier"),
        line_width=data.get("line_width", 2.0),
        line_style=data.get("line_style", "solid"),
        enable_gradient=data.get("enable_gradient", True),
        gradient_ratio=data.get("gradient_ratio", 0.5),
        gradient_enabled=data.get("gradient_enabled", False),
        gradient_start_color=data.get("gradient_start_color"),
        gradient_end_color=data.get("gradient_end_color"),
        brush_effect=data.get("brush_effect", False),
        brush_pressure=data.get("brush_pressure", 1.0),
        brush_texture=data.get("brush_texture"),
        arrow_start=data.get("arrow_start"),
        arrow_end=data.get("arrow_end"),
        arrow_svg=data.get("arrow_svg"),
        dash_pattern=data.get("dash_pattern"),
    )



