"""Style resolver - merges templates and color schemes into final styles."""


from .enums import NodeRole
from .extended_styles import (
    BackgroundStyle,
    BorderStyle,
    ColorScheme,
    EdgeConfig,
    NodeShape,
    RoleBasedStyle,
    SpacingConfig,
    Template,
)
from .style_config import MindMapStyle


def resolve_style(
    style_config: MindMapStyle,
    template_registry: dict[str, Template],
    color_scheme_registry: dict[str, ColorScheme],
) -> None:
    """Resolve template and color scheme into final renderable styles.

    This function merges the template's geometry/appearance with the color
    scheme's colors to produce the final resolved styles.

    Args:
        style_config: The MindMapStyle to update
        template_registry: Registry of available templates
        color_scheme_registry: Registry of available color schemes
    """
    # Get template and color scheme
    template = template_registry.get(style_config.template_name)
    color_scheme = color_scheme_registry.get(style_config.color_scheme_name)

    if not template or not color_scheme:
        # Fallback to defaults if not found
        if not template:
            template = list(template_registry.values())[0] if template_registry else None
        if not color_scheme:
            color_scheme = list(color_scheme_registry.values())[0] if color_scheme_registry else None

    if not template or not color_scheme:
        return  # Cannot resolve without both

    # Store resolved references
    style_config.resolved_template = template
    style_config.resolved_color_scheme = color_scheme

    # Update canvas background from color scheme
    style_config.canvas_bg_color = color_scheme.canvas_bg_color

    # Resolve role-based styles by merging template + colors
    for role, template_style in template.role_styles.items():
        # Create a deep copy of the template style
        _deep_copy_role_style(template_style)

        # Apply colors from color scheme
        if role in color_scheme.node_colors:
            # Note: We store colors separately, NodeItem will combine them
            pass  # Colors are applied at render time

        # Store in a temporary resolved dict (for future use)
        # For now, we keep the legacy depth_styles for backward compatibility
        # TODO: Migrate to role-based rendering


def _deep_copy_role_style(style: RoleBasedStyle) -> RoleBasedStyle:
    """Create a deep copy of a RoleBasedStyle."""
    return RoleBasedStyle(
        role=style.role,
        shape=NodeShape(
            shape_type=style.shape.shape_type,
            basic_shape=style.shape.basic_shape,
            border_radius=style.shape.border_radius,
            svg_path=style.shape.svg_path,
            custom_params=dict(style.shape.custom_params),
        ),
        background=BackgroundStyle(
            bg_type=style.background.bg_type,
            gradient_type=style.background.gradient_type,
            gradient_colors=style.background.gradient_colors.copy() if style.background.gradient_colors else None,
            gradient_angle=style.background.gradient_angle,
            texture_type=style.background.texture_type,
            texture_opacity=style.background.texture_opacity,
            image_path=style.background.image_path,
            image_scale=style.background.image_scale,
            image_opacity=style.background.image_opacity,
        ),
        border=BorderStyle(
            border_type=style.border.border_type,
            border_width=style.border.border_width,
            border_radius=style.border.border_radius,
            border_style=style.border.border_style,
            svg_path=style.border.svg_path,
            svg_repeat=style.border.svg_repeat,
            image_path=style.border.image_path,
            image_scale=style.border.image_scale,
            gradient_type=style.border.gradient_type,
            gradient_colors=style.border.gradient_colors.copy() if style.border.gradient_colors else None,
            gradient_angle=style.border.gradient_angle,
        ),
        padding_w=style.padding_w,
        padding_h=style.padding_h,
        font_size=style.font_size,
        font_weight=style.font_weight,
        font_style=style.font_style,
        font_family=style.font_family,
        shadow_enabled=style.shadow_enabled,
        shadow_offset_x=style.shadow_offset_x,
        shadow_offset_y=style.shadow_offset_y,
        shadow_blur=style.shadow_blur,
        shadow_color=style.shadow_color,
    )


def serialize_style(style_config: MindMapStyle) -> dict:
    """Serialize MindMapStyle to JSON-compatible dict.

    Args:
        style_config: The style configuration to serialize

    Returns:
        Dictionary representation suitable for JSON serialization
    """
    return {
        "name": style_config.name,
        "template_name": style_config.template_name,
        "color_scheme_name": style_config.color_scheme_name,
        "canvas_bg_color": style_config.canvas_bg_color,
        "edge": serialize_edge_config(style_config.edge),
    }


def deserialize_style(data: dict) -> MindMapStyle:
    """Deserialize MindMapStyle from JSON-compatible dict.

    Args:
        data: Dictionary representation from JSON

    Returns:
        MindMapStyle instance
    """

    style = MindMapStyle(
        name=data.get("name", "Default"),
        template_name=data.get("template_name", "default"),
        color_scheme_name=data.get("color_scheme_name", "default"),
        canvas_bg_color=data.get("canvas_bg_color", "#FFFFFF"),
    )

    # Deserialize edge config
    if "edge" in data:
        style.edge = deserialize_edge_config(data["edge"])

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
        "node_colors": {role.value: color for role, color in scheme.node_colors.items()},
        "border_colors": {role.value: color for role, color in scheme.border_colors.items()} if scheme.border_colors else None,
        "text_colors": {role.value: color for role, color in scheme.text_colors.items()} if scheme.text_colors else None,
        "branch_colors": scheme.branch_colors,
        "use_rainbow_branches": scheme.use_rainbow_branches,
        "canvas_bg_color": scheme.canvas_bg_color,
        "edge_color": scheme.edge_color,
    }


def deserialize_color_scheme(data: dict) -> ColorScheme:
    """Deserialize ColorScheme from JSON-compatible dict."""
    node_colors = {
        NodeRole(role): color
        for role, color in data.get("node_colors", {}).items()
    }

    border_colors = None
    if data.get("border_colors"):
        border_colors = {
            NodeRole(role): color
            for role, color in data["border_colors"].items()
        }

    text_colors = None
    if data.get("text_colors"):
        text_colors = {
            NodeRole(role): color
            for role, color in data["text_colors"].items()
        }

    return ColorScheme(
        name=data["name"],
        description=data.get("description", ""),
        node_colors=node_colors,
        border_colors=border_colors,
        text_colors=text_colors,
        branch_colors=data.get("branch_colors", []),
        use_rainbow_branches=data.get("use_rainbow_branches", False),
        canvas_bg_color=data.get("canvas_bg_color", "#FFFFFF"),
        edge_color=data.get("edge_color", "#666666"),
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
        "font_size": style.font_size,
        "font_weight": style.font_weight,
        "font_style": style.font_style,
        "font_family": style.font_family,
        "shadow_enabled": style.shadow_enabled,
        "shadow_offset_x": style.shadow_offset_x,
        "shadow_offset_y": style.shadow_offset_y,
        "shadow_blur": style.shadow_blur,
        "shadow_color": style.shadow_color,
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
        font_size=data.get("font_size", 14),
        font_weight=data.get("font_weight", "Normal"),
        font_style=data.get("font_style", "Normal"),
        font_family=data.get("font_family", "Arial"),
        shadow_enabled=data.get("shadow_enabled", False),
        shadow_offset_x=data.get("shadow_offset_x", 2),
        shadow_offset_y=data.get("shadow_offset_y", 2),
        shadow_blur=data.get("shadow_blur", 4),
        shadow_color=data.get("shadow_color"),
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
        "connector_type": style.connector_type,
        "line_width": style.line_width,
        "line_style": style.line_style,
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
        connector_type=data.get("connector_type", "bezier"),
        line_width=data.get("line_width", 2.0),
        line_style=data.get("line_style", "solid"),
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


# Legacy serialization functions (for backward compatibility)

def serialize_node_style(style) -> dict:
    """Serialize legacy NodeStyleConfig to dict."""
    return {
        "shape": style.shape,
        "font_size": style.font_size,
        "font_weight": style.font_weight,
        "font_family": style.font_family,
        "font_italic": style.font_italic,
        "font_underline": style.font_underline,
        "font_strikeout": style.font_strikeout,
        "padding_width": style.padding_width,
        "padding_height": style.padding_height,
        "border_radius": style.border_radius,
        "max_text_width": style.max_text_width,
        "border_style": style.border_style,
        "border_width": style.border_width,
        "bg_color": style.bg_color,
        "text_color": style.text_color,
        "border_color": style.border_color,
    }


def deserialize_node_style(data: dict):
    """Deserialize legacy NodeStyleConfig from dict."""
    from .style_config import NodeStyleConfig

    return NodeStyleConfig(
        shape=data.get("shape", "rounded_rect"),
        font_size=data.get("font_size", 16),
        font_weight=data.get("font_weight", "Normal"),
        font_family=data.get("font_family", "Arial"),
        font_italic=data.get("font_italic", False),
        font_underline=data.get("font_underline", False),
        font_strikeout=data.get("font_strikeout", False),
        padding_width=data.get("padding_width", 10),
        padding_height=data.get("padding_height", 8),
        border_radius=data.get("border_radius", 8),
        max_text_width=data.get("max_text_width", 250.0),
        border_style=data.get("border_style", "solid"),
        border_width=data.get("border_width", 2),
        bg_color=data.get("bg_color"),
        text_color=data.get("text_color", "#000000"),
        border_color=data.get("border_color"),
    )


def serialize_priority_scheme(scheme) -> dict:
    """Serialize legacy PriorityScheme to dict."""
    return {
        "name": scheme.name,
        "levels": {
            str(level.value): {
                "level": level.value,
                "name": definition.name,
                "style_override": serialize_node_style(definition.style_override),
            }
            for level, definition in scheme.levels.items()
        },
    }


def deserialize_priority_scheme(data: dict):
    """Deserialize legacy PriorityScheme from dict."""
    from .enums import PriorityLevel
    from .style_config import PriorityDefinition, PriorityScheme

    levels = {}
    for level_str, level_data in data.get("levels", {}).items():
        level = PriorityLevel(int(level_str))
        levels[level] = PriorityDefinition(
            level=level,
            name=level_data["name"],
            style_override=deserialize_node_style(level_data["style_override"]),
        )

    return PriorityScheme(
        name=data.get("name", "Default"),
        levels=levels,
    )


def serialize_layout_config(layout) -> dict:
    """Serialize legacy LayoutConfig to dict."""
    return {
        "level_spacing_depth_0": layout.level_spacing_depth_0,
        "level_spacing_depth_1": layout.level_spacing_depth_1,
        "level_spacing_depth_2_plus": layout.level_spacing_depth_2_plus,
        "sibling_spacing_depth_0_1": layout.sibling_spacing_depth_0_1,
        "sibling_spacing_depth_2": layout.sibling_spacing_depth_2,
        "sibling_spacing_depth_3_plus": layout.sibling_spacing_depth_3_plus,
    }


def deserialize_layout_config(data: dict):
    """Deserialize legacy LayoutConfig from dict."""
    from .style_config import LayoutConfig

    return LayoutConfig(
        level_spacing_depth_0=data.get("level_spacing_depth_0", 80.0),
        level_spacing_depth_1=data.get("level_spacing_depth_1", 60.0),
        level_spacing_depth_2_plus=data.get("level_spacing_depth_2_plus", 40.0),
        sibling_spacing_depth_0_1=data.get("sibling_spacing_depth_0_1", 60.0),
        sibling_spacing_depth_2=data.get("sibling_spacing_depth_2", 45.0),
        sibling_spacing_depth_3_plus=data.get("sibling_spacing_depth_3_plus", 35.0),
    )
