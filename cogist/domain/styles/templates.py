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


# Template registry
NODE_TEMPLATES: dict[str, Template] = {}


def _init_templates():
    """Initialize the template registry with preset templates."""
    global NODE_TEMPLATES

    NODE_TEMPLATES = {
        "modern": Template(
            name="Modern",
            description="Clean and modern with rounded corners",
            role_styles={
                NodeRole.ROOT: RoleBasedStyle(
                    role=NodeRole.ROOT,
                    shape=NodeShape(shape_type="basic", basic_shape="rounded_rect", border_radius=16),
                    background=BackgroundStyle(bg_type="solid"),
                    border=BorderStyle(border_type="simple", border_width=2, border_radius=16, border_style="solid"),
                    padding_w=24,
                    padding_h=18,
                ),
                NodeRole.PRIMARY: RoleBasedStyle(
                    role=NodeRole.PRIMARY,
                    shape=NodeShape(shape_type="basic", basic_shape="rounded_rect", border_radius=12),
                    background=BackgroundStyle(bg_type="solid"),
                    border=BorderStyle(border_type="simple", border_width=1, border_radius=12, border_style="solid"),
                    padding_w=20,
                    padding_h=14,
                ),
                NodeRole.SECONDARY: RoleBasedStyle(
                    role=NodeRole.SECONDARY,
                    shape=NodeShape(shape_type="basic", basic_shape="rounded_rect", border_radius=8),
                    background=BackgroundStyle(bg_type="solid"),
                    border=BorderStyle(border_type="simple", border_width=1, border_radius=8, border_style="solid"),
                    padding_w=16,
                    padding_h=12,
                ),
                NodeRole.TERTIARY: RoleBasedStyle(
                    role=NodeRole.TERTIARY,
                    shape=NodeShape(shape_type="basic", basic_shape="rounded_rect", border_radius=6),
                    background=BackgroundStyle(bg_type="solid"),
                    border=BorderStyle(border_type="simple", border_width=1, border_radius=6, border_style="solid"),
                    padding_w=12,
                    padding_h=10,
                ),
            },
            spacing=SpacingConfig(parent_child_spacing=SpacingLevel.NORMAL, sibling_spacing=SpacingLevel.NORMAL),
            default_color_scheme="default",
            recommended_layout="balanced_tree",
        ),
        "minimal": Template(
            name="Minimal",
            description="Simple and minimal with no borders",
            role_styles={
                NodeRole.ROOT: RoleBasedStyle(
                    role=NodeRole.ROOT,
                    shape=NodeShape(shape_type="basic", basic_shape="rectangle", border_radius=0),
                    background=BackgroundStyle(bg_type="solid"),
                    border=BorderStyle(border_type="simple", border_width=0, border_radius=0, border_style="solid"),
                    padding_w=16,
                    padding_h=12,
                ),
                NodeRole.PRIMARY: RoleBasedStyle(
                    role=NodeRole.PRIMARY,
                    shape=NodeShape(shape_type="basic", basic_shape="rectangle", border_radius=0),
                    background=BackgroundStyle(bg_type="solid"),
                    border=BorderStyle(border_type="simple", border_width=0, border_radius=0, border_style="solid"),
                    padding_w=12,
                    padding_h=8,
                ),
                NodeRole.SECONDARY: RoleBasedStyle(
                    role=NodeRole.SECONDARY,
                    shape=NodeShape(shape_type="basic", basic_shape="rectangle", border_radius=0),
                    background=BackgroundStyle(bg_type="solid"),
                    border=BorderStyle(border_type="simple", border_width=0, border_radius=0, border_style="solid"),
                    padding_w=10,
                    padding_h=6,
                ),
                NodeRole.TERTIARY: RoleBasedStyle(
                    role=NodeRole.TERTIARY,
                    shape=NodeShape(shape_type="basic", basic_shape="rectangle", border_radius=0),
                    background=BackgroundStyle(bg_type="solid"),
                    border=BorderStyle(border_type="simple", border_width=0, border_radius=0, border_style="solid"),
                    padding_w=8,
                    padding_h=4,
                ),
            },
            spacing=SpacingConfig(parent_child_spacing=SpacingLevel.COMPACT, sibling_spacing=SpacingLevel.COMPACT),
            default_color_scheme="default",
            recommended_layout="balanced_tree",
        ),
        "professional": Template(
            name="Professional",
            description="Classic professional look with subtle borders",
            role_styles={
                NodeRole.ROOT: RoleBasedStyle(
                    role=NodeRole.ROOT,
                    shape=NodeShape(shape_type="basic", basic_shape="rectangle", border_radius=4),
                    background=BackgroundStyle(bg_type="solid"),
                    border=BorderStyle(border_type="simple", border_width=2, border_radius=4, border_style="solid"),
                    padding_w=20,
                    padding_h=16,
                ),
                NodeRole.PRIMARY: RoleBasedStyle(
                    role=NodeRole.PRIMARY,
                    shape=NodeShape(shape_type="basic", basic_shape="rectangle", border_radius=2),
                    background=BackgroundStyle(bg_type="solid"),
                    border=BorderStyle(border_type="simple", border_width=1, border_radius=2, border_style="solid"),
                    padding_w=16,
                    padding_h=12,
                ),
                NodeRole.SECONDARY: RoleBasedStyle(
                    role=NodeRole.SECONDARY,
                    shape=NodeShape(shape_type="basic", basic_shape="rectangle", border_radius=2),
                    background=BackgroundStyle(bg_type="solid"),
                    border=BorderStyle(border_type="simple", border_width=1, border_radius=2, border_style="solid"),
                    padding_w=14,
                    padding_h=10,
                ),
                NodeRole.TERTIARY: RoleBasedStyle(
                    role=NodeRole.TERTIARY,
                    shape=NodeShape(shape_type="basic", basic_shape="rectangle", border_radius=0),
                    background=BackgroundStyle(bg_type="solid"),
                    border=BorderStyle(border_type="simple", border_width=1, border_radius=0, border_style="solid"),
                    padding_w=12,
                    padding_h=8,
                ),
            },
            spacing=SpacingConfig(parent_child_spacing=SpacingLevel.RELAXED, sibling_spacing=SpacingLevel.NORMAL),
            default_color_scheme="default",
            recommended_layout="balanced_tree",
        ),
        "colorful": Template(
            name="Colorful",
            description="Vibrant design with rounded shapes",
            role_styles={
                NodeRole.ROOT: RoleBasedStyle(
                    role=NodeRole.ROOT,
                    shape=NodeShape(shape_type="basic", basic_shape="rounded_rect", border_radius=20),
                    background=BackgroundStyle(bg_type="solid"),
                    border=BorderStyle(border_type="simple", border_width=3, border_radius=20, border_style="solid"),
                    padding_w=28,
                    padding_h=20,
                ),
                NodeRole.PRIMARY: RoleBasedStyle(
                    role=NodeRole.PRIMARY,
                    shape=NodeShape(shape_type="basic", basic_shape="rounded_rect", border_radius=16),
                    background=BackgroundStyle(bg_type="solid"),
                    border=BorderStyle(border_type="simple", border_width=2, border_radius=16, border_style="solid"),
                    padding_w=24,
                    padding_h=16,
                ),
                NodeRole.SECONDARY: RoleBasedStyle(
                    role=NodeRole.SECONDARY,
                    shape=NodeShape(shape_type="basic", basic_shape="rounded_rect", border_radius=12),
                    background=BackgroundStyle(bg_type="solid"),
                    border=BorderStyle(border_type="simple", border_width=1, border_radius=12, border_style="solid"),
                    padding_w=20,
                    padding_h=14,
                ),
                NodeRole.TERTIARY: RoleBasedStyle(
                    role=NodeRole.TERTIARY,
                    shape=NodeShape(shape_type="basic", basic_shape="rounded_rect", border_radius=8),
                    background=BackgroundStyle(bg_type="solid"),
                    border=BorderStyle(border_type="simple", border_width=1, border_radius=8, border_style="solid"),
                    padding_w=16,
                    padding_h=12,
                ),
            },
            spacing=SpacingConfig(parent_child_spacing=SpacingLevel.SPACIOUS, sibling_spacing=SpacingLevel.RELAXED),
            default_color_scheme="rainbow",
            recommended_layout="balanced_tree",
        ),
    }


# Color scheme registry
COLOR_SCHEMES: dict[str, ColorScheme] = {}


def _init_color_schemes():
    """Initialize the color scheme registry with preset color schemes."""
    global COLOR_SCHEMES

    COLOR_SCHEMES = {
        "default": ColorScheme(
            name="Default",
            description="Classic blue color scheme",
            node_colors={
                NodeRole.ROOT: "#2196F3",
                NodeRole.PRIMARY: "#4CAF50",
                NodeRole.SECONDARY: "#FF9800",
                NodeRole.TERTIARY: "#9E9E9E",
            },
            canvas_bg_color="#FFFFFF",
            edge_color="#666666",
            use_rainbow_branches=False,
        ),
        "rainbow": ColorScheme(
            name="Rainbow",
            description="Colorful rainbow branches",
            node_colors={
                NodeRole.ROOT: "#2196F3",
                NodeRole.PRIMARY: "#4CAF50",
                NodeRole.SECONDARY: "#FF9800",
                NodeRole.TERTIARY: "#9E9E9E",
            },
            branch_colors=[
                "#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8",
                "#F7DC6F", "#BB8FCE", "#85C1E2", "#F8B739", "#52B788",
            ],
            use_rainbow_branches=True,
            canvas_bg_color="#FFFFFF",
            edge_color="#666666",
        ),
        "sunset": ColorScheme(
            name="Sunset",
            description="Warm sunset colors",
            node_colors={
                NodeRole.ROOT: "#FF5722",
                NodeRole.PRIMARY: "#FF9800",
                NodeRole.SECONDARY: "#FFC107",
                NodeRole.TERTIARY: "#795548",
            },
            canvas_bg_color="#FFF8E1",
            edge_color="#8D6E63",
            use_rainbow_branches=False,
        ),
        "ocean": ColorScheme(
            name="Ocean",
            description="Cool ocean blue colors",
            node_colors={
                NodeRole.ROOT: "#0D47A1",
                NodeRole.PRIMARY: "#1976D2",
                NodeRole.SECONDARY: "#42A5F5",
                NodeRole.TERTIARY: "#90CAF9",
            },
            canvas_bg_color="#E3F2FD",
            edge_color="#1565C0",
            use_rainbow_branches=False,
        ),
        "forest": ColorScheme(
            name="Forest",
            description="Natural green colors",
            node_colors={
                NodeRole.ROOT: "#2E7D32",
                NodeRole.PRIMARY: "#43A047",
                NodeRole.SECONDARY: "#66BB6A",
                NodeRole.TERTIARY: "#A5D6A7",
            },
            canvas_bg_color="#E8F5E9",
            edge_color="#388E3C",
            use_rainbow_branches=False,
        ),
        "dark": ColorScheme(
            name="Dark",
            description="Dark mode colors",
            node_colors={
                NodeRole.ROOT: "#7C4DFF",
                NodeRole.PRIMARY: "#536DFE",
                NodeRole.SECONDARY: "#40C4FF",
                NodeRole.TERTIARY: "#B388FF",
            },
            canvas_bg_color="#121212",
            edge_color="#424242",
            use_rainbow_branches=False,
        ),
        "pastel": ColorScheme(
            name="Pastel",
            description="Soft pastel colors",
            node_colors={
                NodeRole.ROOT: "#F8BBD9",
                NodeRole.PRIMARY: "#C5E1A5",
                NodeRole.SECONDARY: "#FFE082",
                NodeRole.TERTIARY: "#B3E5FC",
            },
            canvas_bg_color="#FAFAFA",
            edge_color="#BDBDBD",
            use_rainbow_branches=False,
        ),
    }


# Initialize on module load
_init_color_schemes()
_init_templates()
