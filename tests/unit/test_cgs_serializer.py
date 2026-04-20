"""Test CGS file format serialization and deserialization."""

import tempfile
from pathlib import Path

from cogist.domain.styles import (
    ColorScheme,
    MindMapStyle,
    NodeRole,
    RoleBasedStyle,
    SpacingConfig,
    SpacingLevel,
    Template,
)
from cogist.infrastructure.io.cgs_serializer import CGSSerializer


def create_test_node_data() -> dict:
    """Create sample node tree data for testing."""
    return {
        "root": {
            "id": "node_001",
            "text": "中心主题",
            "width": 120.0,
            "height": 40.0,
            "position": {"x": 0.0, "y": 0.0},
            "is_root": True,
            "depth": 0,
            "role": "root",
            "children": [
                {
                    "id": "node_002",
                    "text": "分支一",
                    "width": 100.0,
                    "height": 35.0,
                    "position": {"x": 150.0, "y": -50.0},
                    "is_root": False,
                    "depth": 1,
                    "role": "primary",
                    "children": [
                        {
                            "id": "node_003",
                            "text": "子节点",
                            "width": 90.0,
                            "height": 30.0,
                            "position": {"x": 280.0, "y": -50.0},
                            "is_root": False,
                            "depth": 2,
                            "role": "secondary",
                            "children": [],
                        }
                    ],
                }
            ],
        }
    }


def create_test_style_config() -> MindMapStyle:
    """Create sample style configuration for testing."""
    style = MindMapStyle(
        template_name="test",
        color_scheme_name="test",
    )

    # Create template
    template = Template(
        name="test",
        description="Test template",
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
    )

    # Create color scheme
    color_scheme = ColorScheme(
        name="test",
        description="Test colors",
        node_colors={
            NodeRole.ROOT: "#FF0000",
            NodeRole.PRIMARY: "#00FF00",
        },
    )

    # Set resolved references
    style.resolved_template = template
    style.resolved_color_scheme = color_scheme

    return style


def test_serialize_without_style():
    """Test serialization without style configuration."""
    node_data = create_test_node_data()

    # Serialize
    cgs_bytes = CGSSerializer.serialize(node_data)

    # Verify it's valid ZIP
    assert len(cgs_bytes) > 0
    assert cgs_bytes[:4] == b'PK\x03\x04'  # ZIP magic number

    print("✅ Serialize without style test passed")


def test_serialize_with_style():
    """Test serialization with style configuration."""
    node_data = create_test_node_data()
    style_config = create_test_style_config()

    # Serialize
    cgs_bytes = CGSSerializer.serialize(node_data, style_config)

    # Verify
    assert len(cgs_bytes) > 0

    # Deserialize to verify
    result = CGSSerializer.deserialize(cgs_bytes)

    assert 'nodes' in result
    assert 'style' in result
    assert result['nodes']['root']['id'] == 'node_001'
    assert result['style'].template_name == 'test'

    print("✅ Serialize with style test passed")


def test_deserialize_structure():
    """Test deserialization returns correct structure."""
    node_data = create_test_node_data()
    style_config = create_test_style_config()

    # Serialize and deserialize
    cgs_bytes = CGSSerializer.serialize(node_data, style_config)
    result = CGSSerializer.deserialize(cgs_bytes)

    # Verify structure
    assert 'nodes' in result
    assert 'style' in result
    assert 'assets' in result
    assert 'manifest' in result

    # Verify nodes
    assert result['nodes']['root']['text'] == '中心主题'
    assert len(result['nodes']['root']['children']) == 1

    # Verify style
    assert result['style'].resolved_template is not None
    assert result['style'].resolved_color_scheme is not None
    assert result['style'].resolved_template.role_styles[NodeRole.ROOT].font_size == 22

    # Verify manifest
    assert result['manifest']['format_version'] == 1
    assert result['manifest']['metadata']['node_count'] == 3
    assert result['manifest']['metadata']['max_depth'] == 2

    print("✅ Deserialize structure test passed")


def test_save_and_load_file():
    """Test saving to and loading from .cgs file."""
    node_data = create_test_node_data()
    style_config = create_test_style_config()

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test.cgs"

        # Save
        saved_path = CGSSerializer.save_to_file(file_path, node_data, style_config)
        assert saved_path.exists()
        assert saved_path.suffix == '.cgs'

        # Load
        result = CGSSerializer.load_from_file(saved_path)

        # Verify
        assert result['nodes']['root']['id'] == 'node_001'
        assert result['style'].template_name == 'test'
        assert result['manifest']['metadata']['node_count'] == 3

        print("✅ Save and load file test passed")


def test_assets_handling():
    """Test asset files handling."""
    node_data = create_test_node_data()

    # Create mock assets
    assets = {
        'images/test.png': b'\x89PNG\r\n\x1a\n',  # PNG header
        'vectors/test.svg': b'<svg></svg>',
    }

    # Serialize with assets
    cgs_bytes = CGSSerializer.serialize(node_data, assets=assets)

    # Deserialize
    result = CGSSerializer.deserialize(cgs_bytes)

    # Verify assets
    assert 'assets/images/test.png' in result['assets']
    assert 'assets/vectors/test.svg' in result['assets']
    assert result['assets']['assets/images/test.png'] == b'\x89PNG\r\n\x1a\n'

    # Verify manifest includes assets
    assert 'assets' in result['manifest']['files']

    print("✅ Assets handling test passed")


def test_manifest_metadata():
    """Test manifest metadata accuracy."""
    # Create a deeper tree
    node_data = {
        "root": {
            "id": "r1",
            "text": "Root",
            "children": [
                {
                    "id": "c1",
                    "text": "Child 1",
                    "children": [
                        {
                            "id": "gc1",
                            "text": "Grandchild",
                            "children": []
                        }
                    ]
                }
            ]
        }
    }

    cgs_bytes = CGSSerializer.serialize(node_data)
    result = CGSSerializer.deserialize(cgs_bytes)

    # Verify metadata
    assert result['manifest']['metadata']['node_count'] == 3
    assert result['manifest']['metadata']['max_depth'] == 2
    assert 'created_at' in result['manifest']
    assert 'modified_at' in result['manifest']

    print("✅ Manifest metadata test passed")


def test_format_version_validation():
    """Test format version validation."""
    node_data = create_test_node_data()

    # Valid format
    cgs_bytes = CGSSerializer.serialize(node_data)
    result = CGSSerializer.deserialize(cgs_bytes)
    assert result['manifest']['format_version'] == 1

    print("✅ Format version validation test passed")


def test_round_trip_preserves_data():
    """Test that serialize -> deserialize preserves all data."""
    node_data = create_test_node_data()
    style_config = create_test_style_config()

    # Round trip
    cgs_bytes = CGSSerializer.serialize(node_data, style_config)
    result = CGSSerializer.deserialize(cgs_bytes)

    # Verify node data preserved
    original_root = node_data['root']
    loaded_root = result['nodes']['root']

    assert loaded_root['id'] == original_root['id']
    assert loaded_root['text'] == original_root['text']
    assert loaded_root['width'] == original_root['width']
    assert loaded_root['position'] == original_root['position']

    # Verify style preserved
    assert result['style'].template_name == style_config.template_name
    assert result['style'].color_scheme_name == style_config.color_scheme_name
    assert result['style'].resolved_template.name == "test"
    assert result['style'].resolved_color_scheme.name == "test"

    print("✅ Round-trip data preservation test passed")


if __name__ == "__main__":
    test_serialize_without_style()
    test_serialize_with_style()
    test_deserialize_structure()
    test_save_and_load_file()
    test_assets_handling()
    test_manifest_metadata()
    test_format_version_validation()
    test_round_trip_preserves_data()

    print("\n🎉 All CGS serializer tests passed!")
