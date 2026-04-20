"""Test the new extended styles architecture."""

from cogist.domain.styles import (
    NodeRole,
    SpacingLevel,
    SpacingConfig,
    NodeShape,
    BackgroundStyle,
    BorderStyle,
    RoleBasedStyle,
    ColorScheme,
    Template,
)


def test_enums():
    """Test enum definitions."""
    # NodeRole
    assert NodeRole.ROOT == "root"
    assert NodeRole.PRIMARY == "primary"
    assert NodeRole.SECONDARY == "secondary"
    
    # SpacingLevel
    assert SpacingLevel.COMPACT == "compact"
    assert SpacingLevel.NORMAL == "normal"
    assert SpacingLevel.RELAXED == "relaxed"
    assert SpacingLevel.SPACIOUS == "spacious"
    
    print("✅ Enums test passed")


def test_spacing_config():
    """Test spacing configuration."""
    config = SpacingConfig(
        parent_child_spacing=SpacingLevel.COMPACT,
        sibling_spacing=SpacingLevel.RELAXED,
    )
    
    assert config.parent_child_spacing == SpacingLevel.COMPACT
    assert config.sibling_spacing == SpacingLevel.RELAXED
    
    # Test default values
    default_config = SpacingConfig()
    assert default_config.parent_child_spacing == SpacingLevel.NORMAL
    assert default_config.sibling_spacing == SpacingLevel.NORMAL
    
    print("✅ SpacingConfig test passed")


def test_node_shape():
    """Test node shape configuration."""
    # Basic shape
    basic_shape = NodeShape(
        shape_type="basic",
        basic_shape="rounded_rect",
        border_radius=8,
    )
    assert basic_shape.shape_type == "basic"
    assert basic_shape.basic_shape == "rounded_rect"
    
    # SVG shape
    svg_shape = NodeShape(
        shape_type="svg",
        svg_path="<path d='M...'/>",
    )
    assert svg_shape.shape_type == "svg"
    assert svg_shape.svg_path is not None
    
    print("✅ NodeShape test passed")


def test_background_style():
    """Test background style configuration."""
    # Solid background
    solid_bg = BackgroundStyle(bg_type="solid")
    assert solid_bg.bg_type == "solid"
    
    # Texture background
    texture_bg = BackgroundStyle(
        bg_type="texture",
        texture_type="paper",
        texture_opacity=0.5,
    )
    assert texture_bg.bg_type == "texture"
    assert texture_bg.texture_type == "paper"
    
    print("✅ BackgroundStyle test passed")


def test_border_style():
    """Test border style configuration."""
    # Simple border
    simple_border = BorderStyle(
        border_type="simple",
        border_width=2,
        border_style="solid",
    )
    assert simple_border.border_type == "simple"
    
    # SVG border
    svg_border = BorderStyle(
        border_type="svg",
        svg_path="<path d='M...'/>",
        svg_repeat=True,
    )
    assert svg_border.border_type == "svg"
    
    print("✅ BorderStyle test passed")


def test_role_based_style():
    """Test role-based style configuration."""
    style = RoleBasedStyle(
        role=NodeRole.ROOT,
        font_size=22,
        font_weight="Bold",
        shadow_enabled=True,
        shadow_blur=8,
    )
    
    assert style.role == NodeRole.ROOT
    assert style.font_size == 22
    assert style.shadow_enabled is True
    assert style.shadow_blur == 8
    
    # Check that nested objects are created
    assert isinstance(style.shape, NodeShape)
    assert isinstance(style.background, BackgroundStyle)
    assert isinstance(style.border, BorderStyle)
    
    print("✅ RoleBasedStyle test passed")


def test_color_scheme():
    """Test color scheme configuration."""
    scheme = ColorScheme(
        name="Blue Theme",
        description="A blue color scheme",
        node_colors={
            NodeRole.ROOT: "#2196F3",
            NodeRole.PRIMARY: "#4CAF50",
        },
        canvas_bg_color="#FFFFFF",
        edge_color="#666666",
    )
    
    assert scheme.name == "Blue Theme"
    assert scheme.node_colors[NodeRole.ROOT] == "#2196F3"
    assert len(scheme.branch_colors) == 10  # Default branch colors
    
    print("✅ ColorScheme test passed")


def test_template():
    """Test template configuration."""
    template = Template(
        name="Modern",
        description="A modern template",
        role_styles={
            NodeRole.ROOT: RoleBasedStyle(
                role=NodeRole.ROOT,
                font_size=22,
                font_weight="Bold",
            ),
            NodeRole.PRIMARY: RoleBasedStyle(
                role=NodeRole.PRIMARY,
                font_size=18,
            ),
        },
        spacing=SpacingConfig(
            parent_child_spacing=SpacingLevel.NORMAL,
            sibling_spacing=SpacingLevel.NORMAL,
        ),
        default_color_scheme="blue",
    )
    
    assert template.name == "Modern"
    assert len(template.role_styles) == 2
    assert template.default_color_scheme == "blue"
    
    print("✅ Template test passed")


def test_advanced_features():
    """Test advanced styling features."""
    # Chinese style with SVG and texture
    chinese_style = RoleBasedStyle(
        role=NodeRole.ROOT,
        shape=NodeShape(
            shape_type="svg",
            svg_path="<path d='M...'/>",  # Fan shape
        ),
        background=BackgroundStyle(
            bg_type="texture",
            texture_type="paper",  # Rice paper
            texture_opacity=0.5,
        ),
        border=BorderStyle(
            border_type="svg",
            svg_path="<path d='M...'/>",  # Cloud pattern
            svg_repeat=True,
        ),
        font_family="KaiTi",  # Chinese font
        shadow_enabled=True,
        shadow_blur=6,
    )
    
    assert chinese_style.shape.shape_type == "svg"
    assert chinese_style.background.bg_type == "texture"
    assert chinese_style.border.border_type == "svg"
    assert chinese_style.shadow_enabled is True
    
    print("✅ Advanced features test passed")


if __name__ == "__main__":
    test_enums()
    test_spacing_config()
    test_node_shape()
    test_background_style()
    test_border_style()
    test_role_based_style()
    test_color_scheme()
    test_template()
    test_advanced_features()
    
    print("\n🎉 All tests passed!")
