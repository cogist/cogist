"""Style resolver - merges templates and color schemes into final styles."""

from .enums import NodeRole
from .extended_styles import (
    BackgroundStyle,
    BorderStyle,
    ColorScheme,
    EdgeConfig,
    NodeShape,
    RoleBasedStyle,
    RoleStyle,  # NEW: Flat role-based style
    SpacingConfig,
    Template,
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
        "branch_colors": style_config.branch_colors,
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
        branch_colors=data.get("branch_colors", []),
    )

    # Deserialize role styles
    if "role_styles" in data:
        for role_str, role_data in data["role_styles"].items():
            role = NodeRole(role_str)
            style.role_styles[role] = deserialize_role_style(role_data)

    return style


def serialize_template(template: Template) -> dict:
    """Serialize Template to JSON-compatible dict."""
    return {
        "name": template.name,
        "description": template.description,
        "role_styles": {
            role.value: serialize_role_based_style(style)
            for role, style in template.role_styles.items()
        },
        "spacing": {
            "parent_child_spacing": template.spacing.parent_child_spacing.value,
            "sibling_spacing": template.spacing.sibling_spacing.value,
        },
        "default_color_scheme": template.default_color_scheme,
        "recommended_layout": template.recommended_layout,
    }


def deserialize_template(data: dict) -> Template:
    """Deserialize Template from JSON-compatible dict."""
    from .enums import SpacingLevel

    role_styles = {
        NodeRole(role): deserialize_role_based_style(role, style_data)
        for role, style_data in data["role_styles"].items()
    }

    spacing_data = data.get("spacing", {})
    spacing = SpacingConfig(
        parent_child_spacing=SpacingLevel(spacing_data.get("parent_child_spacing", "normal")),
        sibling_spacing=SpacingLevel(spacing_data.get("sibling_spacing", "normal")),
    )

    return Template(
        name=data["name"],
        description=data.get("description", ""),
        role_styles=role_styles,
        spacing=spacing,
        default_color_scheme=data.get("default_color_scheme", "default"),
        recommended_layout=data.get("recommended_layout"),
    )


def serialize_color_scheme(scheme: ColorScheme) -> dict:
    """Serialize ColorScheme to JSON-compatible dict."""
    return {
        "name": scheme.name,
        "description": scheme.description,
        "role_configs": {
            role.value: {
                "bg_color": config.bg_color,
                "border_color": config.border_color,
                "text_color": config.text_color,
                "rainbow_bg_enabled": config.rainbow_bg_enabled,
                "rainbow_border_enabled": config.rainbow_border_enabled,
                "brightness_amount": config.brightness_amount,
                "opacity_amount": config.opacity_amount,
            }
            for role, config in scheme.role_configs.items()
        },
        "branch_colors": scheme.branch_colors,
        "use_rainbow_branches": scheme.use_rainbow_branches,
        "canvas_bg_color": scheme.canvas_bg_color,
        "edge_color": scheme.edge_color,
    }


def deserialize_color_scheme(data: dict) -> ColorScheme:
    """Deserialize ColorScheme from JSON-compatible dict.

    Note: Old format with role_configs, canvas_bg_color, edge_color is deprecated.
    New format only has branch_colors (9 colors).
    """
    return ColorScheme(
        name=data["name"],
        description=data.get("description", ""),
        branch_colors=data.get("branch_colors", []),
        default_use_rainbow_branches=data.get("default_use_rainbow_branches"),
    )


# Helper functions for nested structures

def serialize_role_based_style(style: RoleBasedStyle) -> dict:
    """Serialize RoleBasedStyle to dict."""
    return {
        "shape": {
            "shape_type": style.shape.shape_type,
            "basic_shape": style.shape.basic_shape,
            "border_radius": style.shape.border_radius,
            "svg_path": style.shape.svg_path,
            "custom_params": style.shape.custom_params,
        },
        "background": {
            "bg_type": style.background.bg_type,
            "gradient_type": style.background.gradient_type,
            "gradient_colors": style.background.gradient_colors,
            "gradient_angle": style.background.gradient_angle,
            "texture_type": style.background.texture_type,
            "texture_opacity": style.background.texture_opacity,
            "image_path": style.background.image_path,
            "image_scale": style.background.image_scale,
            "image_opacity": style.background.image_opacity,
        },
        "border": {
            "border_type": style.border.border_type,
            "border_width": style.border.border_width,
            "border_radius": style.border.border_radius,
            "border_style": style.border.border_style,
            "svg_path": style.border.svg_path,
            "svg_repeat": style.border.svg_repeat,
            "image_path": style.border.image_path,
            "image_scale": style.border.image_scale,
            "gradient_type": style.border.gradient_type,
            "gradient_colors": style.border.gradient_colors,
            "gradient_angle": style.border.gradient_angle,
        },
        "padding_w": style.padding_w,
        "padding_h": style.padding_h,
        "max_text_width": style.max_text_width,
        "font_size": style.font_size,
        "font_weight": style.font_weight,
        "font_italic": style.font_italic,
        "font_family": style.font_family,
        "shadow_enabled": style.shadow_enabled,
        "shadow_offset_x": style.shadow_offset_x,
        "shadow_offset_y": style.shadow_offset_y,
        "shadow_blur": style.shadow_blur,
        "shadow_color": style.shadow_color,
        # Spacing configuration (per-role)
        "parent_child_spacing": style.parent_child_spacing,
        "sibling_spacing": style.sibling_spacing,
        # Connector configuration (per-role)
        "connector_shape": style.connector_shape,
        "connector_style": style.connector_style,
        "line_width": style.line_width,
        "connector_color": style.connector_color,
    }


def deserialize_role_based_style(role: NodeRole, data: dict) -> RoleBasedStyle:
    """Deserialize RoleBasedStyle from dict."""
    shape_data = data.get("shape", {})
    background_data = data.get("background", {})
    border_data = data.get("border", {})

    return RoleBasedStyle(
        role=role,
        shape=NodeShape(
            shape_type=shape_data.get("shape_type", "basic"),
            basic_shape=shape_data.get("basic_shape", "rounded_rect"),
            border_radius=shape_data.get("border_radius", 8),
            svg_path=shape_data.get("svg_path"),
            custom_params=shape_data.get("custom_params", {}),
        ),
        background=BackgroundStyle(
            bg_type=background_data.get("bg_type", "solid"),
            gradient_type=background_data.get("gradient_type"),
            gradient_colors=background_data.get("gradient_colors"),
            gradient_angle=background_data.get("gradient_angle", 0.0),
            texture_type=background_data.get("texture_type"),
            texture_opacity=background_data.get("texture_opacity", 0.3),
            image_path=background_data.get("image_path"),
            image_scale=background_data.get("image_scale", 1.0),
            image_opacity=background_data.get("image_opacity", 1.0),
        ),
        border=BorderStyle(
            border_type=border_data.get("border_type", "simple"),
            border_width=border_data.get("border_width", 0),
            border_radius=border_data.get("border_radius", 8),
            border_style=border_data.get("border_style", "solid"),
            svg_path=border_data.get("svg_path"),
            svg_repeat=border_data.get("svg_repeat", False),
            image_path=border_data.get("image_path"),
            image_scale=border_data.get("image_scale", 1.0),
            gradient_type=border_data.get("gradient_type"),
            gradient_colors=border_data.get("gradient_colors"),
            gradient_angle=border_data.get("gradient_angle", 0.0),
        ),
        padding_w=data.get("padding_w", 12),
        padding_h=data.get("padding_h", 8),
        max_text_width=data.get("max_text_width", 250),
        font_size=data.get("font_size", 14),
        font_weight=data.get("font_weight", "Normal"),
        font_italic=data.get("font_italic", False),
        font_family=data.get("font_family", "Arial"),
        shadow_enabled=data.get("shadow_enabled", False),
        shadow_offset_x=data.get("shadow_offset_x", 2),
        shadow_offset_y=data.get("shadow_offset_y", 2),
        shadow_blur=data.get("shadow_blur", 4),
        shadow_color=data.get("shadow_color"),
        # Spacing configuration (per-role)
        parent_child_spacing=data.get("parent_child_spacing", 80.0),
        sibling_spacing=data.get("sibling_spacing", 60.0),
        # Connector configuration (per-role)
        connector_shape=data.get("connector_shape", "bezier"),
        connector_style=data.get("connector_style", "solid"),
        line_width=data.get("line_width", 2.0),
        connector_color_index=data.get("connector_color_index", 0),
        connector_brightness=data.get("connector_brightness", 1.0),
        connector_opacity=data.get("connector_opacity", 255),
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



