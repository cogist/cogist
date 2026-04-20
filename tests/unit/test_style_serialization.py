"""Test style serialization and deserialization."""

import json

from cogist.domain.styles import (
    NodeRole,
    SpacingLevel,
    ColorScheme,
    Template,
    RoleBasedStyle,
    SpacingConfig,
    serialize_template,
    deserialize_template,
    serialize_color_scheme,
    deserialize_color_scheme,
)


def test_template_serialization():
    """Test template serialization and deserialization."""
    # Create a template
    template = Template(
        name="Modern",
        description="A modern template",
        role_styles={
            NodeRole.ROOT: RoleBasedStyle(
                role=NodeRole.ROOT,
                font_size=22,
                font_weight="Bold",
                shadow_enabled=True,
                shadow_blur=8,
            ),
            NodeRole.PRIMARY: RoleBasedStyle(
                role=NodeRole.PRIMARY,
                font_size=18,
            ),
        },
        spacing=SpacingConfig(
            parent_child_spacing=SpacingLevel.NORMAL,
            sibling_spacing=SpacingLevel.COMPACT,
        ),
        default_color_scheme="blue",
        recommended_layout="balanced_tree",
    )
    
    # Serialize
    data = serialize_template(template)
    json_str = json.dumps(data, indent=2)
    print("Serialized template:")
    print(json_str[:200] + "...")
    
    # Deserialize
    restored = deserialize_template(data)
    
    # Verify
    assert restored.name == template.name
    assert restored.description == template.description
    assert len(restored.role_styles) == len(template.role_styles)
    assert restored.spacing.parent_child_spacing == SpacingLevel.NORMAL
    assert restored.spacing.sibling_spacing == SpacingLevel.COMPACT
    assert restored.default_color_scheme == "blue"
    assert restored.recommended_layout == "balanced_tree"
    
    # Verify role styles
    root_style = restored.role_styles[NodeRole.ROOT]
    assert root_style.font_size == 22
    assert root_style.font_weight == "Bold"
    assert root_style.shadow_enabled is True
    assert root_style.shadow_blur == 8
    
    print("✅ Template serialization test passed")


def test_color_scheme_serialization():
    """Test color scheme serialization and deserialization."""
    # Create a color scheme
    scheme = ColorScheme(
        name="Blue Theme",
        description="A blue color scheme",
        node_colors={
            NodeRole.ROOT: "#2196F3",
            NodeRole.PRIMARY: "#4CAF50",
            NodeRole.SECONDARY: "#FF9800",
        },
        border_colors={
            NodeRole.ROOT: "#1976D2",
        },
        text_colors={
            NodeRole.ROOT: "#FFFFFF",
        },
        branch_colors=["#FF6B6B", "#4ECDC4"],
        use_rainbow_branches=True,
        canvas_bg_color="#F5F5F5",
        edge_color="#999999",
    )
    
    # Serialize
    data = serialize_color_scheme(scheme)
    json_str = json.dumps(data, indent=2)
    print("\nSerialized color scheme:")
    print(json_str[:200] + "...")
    
    # Deserialize
    restored = deserialize_color_scheme(data)
    
    # Verify
    assert restored.name == scheme.name
    assert restored.description == scheme.description
    assert restored.node_colors[NodeRole.ROOT] == "#2196F3"
    assert restored.node_colors[NodeRole.PRIMARY] == "#4CAF50"
    assert restored.border_colors is not None
    assert restored.border_colors[NodeRole.ROOT] == "#1976D2"
    assert restored.text_colors is not None
    assert restored.text_colors[NodeRole.ROOT] == "#FFFFFF"
    assert len(restored.branch_colors) == 2
    assert restored.use_rainbow_branches is True
    assert restored.canvas_bg_color == "#F5F5F5"
    assert restored.edge_color == "#999999"
    
    print("✅ Color scheme serialization test passed")


def test_round_trip():
    """Test that serialize -> deserialize preserves all data."""
    # Create complex template with advanced features
    template = Template(
        name="Chinese Style",
        description="Traditional Chinese style",
        role_styles={
            NodeRole.ROOT: RoleBasedStyle(
                role=NodeRole.ROOT,
                font_size=24,
                font_family="KaiTi",
                shadow_enabled=True,
                shadow_blur=10,
                shadow_color="#00000060",
            ),
        },
        spacing=SpacingConfig(
            parent_child_spacing=SpacingLevel.RELAXED,
            sibling_spacing=SpacingLevel.RELAXED,
        ),
        default_color_scheme="traditional",
    )
    
    # Round trip
    data = serialize_template(template)
    restored = deserialize_template(data)
    
    # Deep comparison
    assert restored.name == template.name
    assert restored.description == template.description
    assert len(restored.role_styles) == len(template.role_styles)
    
    root_original = template.role_styles[NodeRole.ROOT]
    root_restored = restored.role_styles[NodeRole.ROOT]
    
    assert root_restored.font_size == root_original.font_size
    assert root_restored.font_family == root_original.font_family
    assert root_restored.shadow_enabled == root_original.shadow_enabled
    assert root_restored.shadow_blur == root_original.shadow_blur
    assert root_restored.shadow_color == root_original.shadow_color
    
    print("✅ Round-trip test passed")


def test_json_compatibility():
    """Test that serialized data is valid JSON."""
    template = Template(
        name="Test",
        description="Test template",
        role_styles={
            NodeRole.ROOT: RoleBasedStyle(role=NodeRole.ROOT),
        },
    )
    
    color_scheme = ColorScheme(
        name="Test Colors",
        description="Test colors",
    )
    
    # Serialize to JSON string
    template_json = json.dumps(serialize_template(template))
    color_json = json.dumps(serialize_color_scheme(color_scheme))
    
    # Parse back
    template_data = json.loads(template_json)
    color_data = json.loads(color_json)
    
    # Deserialize
    restored_template = deserialize_template(template_data)
    restored_color = deserialize_color_scheme(color_data)
    
    assert restored_template.name == "Test"
    assert restored_color.name == "Test Colors"
    
    print("✅ JSON compatibility test passed")


if __name__ == "__main__":
    test_template_serialization()
    test_color_scheme_serialization()
    test_round_trip()
    test_json_compatibility()
    
    print("\n🎉 All serialization tests passed!")
