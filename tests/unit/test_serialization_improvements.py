"""Unit tests for serialization improvements."""

from cogist.domain.styles.style_resolver import deserialize_style, serialize_style
from cogist.domain.styles.templates import create_default_template
from cogist.infrastructure.io.cgs_serializer import CGSSerializer


class TestStyleSerialization:
    """Test MindMapStyle serialization without template/color_scheme references."""

    def test_serialize_style_no_template_name(self):
        """serialize_style should NOT include template_name."""
        style = create_default_template()
        data = serialize_style(style)

        assert "template_name" not in data
        assert "color_scheme_name" not in data

    def test_serialize_style_includes_spacing_config(self):
        """serialize_style should include spacing configurations."""
        style = create_default_template()
        data = serialize_style(style)

        assert "parent_child_spacing" in data
        assert "sibling_spacing" in data

    def test_serialize_style_no_connector_config(self):
        """serialize_style should NOT include per-depth connector config (uses role-based)."""
        style = create_default_template()
        data = serialize_style(style)

        assert "connector_config_by_depth" not in data
        assert "max_text_width_by_depth" not in data

    def test_deserialize_style_no_template_name(self):
        """deserialize_style should work without template_name."""
        data = {
            "name": "Test Style",
            "parent_child_spacing": 80.0,
            "sibling_spacing": 60.0,
            "canvas_bg_color": "#FFFFFF",
        }

        style = deserialize_style(data)

        assert style.name == "Test Style"
        assert style.parent_child_spacing == 80.0
        assert style.sibling_spacing == 60.0
        assert not hasattr(style, "template_name") or style.template_name is None

    def test_serialize_deserialize_roundtrip(self):
        """Style should survive serialize -> deserialize roundtrip."""
        original = create_default_template()

        # Serialize
        data = serialize_style(original)

        # Deserialize
        restored = deserialize_style(data)

        # Verify key fields
        assert restored.name == original.name
        assert restored.parent_child_spacing == original.parent_child_spacing
        assert restored.sibling_spacing == original.sibling_spacing
        assert restored.canvas_bg_color == original.canvas_bg_color


class TestViewportState:
    """Test viewport state persistence in CGS format."""

    def test_serialize_with_viewport_state(self):
        """CGSSerializer.serialize should accept viewport_state parameter."""
        root_data = {"root": {"id": "root", "text": "Root", "children": []}}
        viewport = {"center_x": 400.0, "center_y": 300.0, "zoom_level": 1.0}

        cgs_bytes = CGSSerializer.serialize(root_data, viewport_state=viewport)

        assert isinstance(cgs_bytes, bytes)
        assert len(cgs_bytes) > 0

    def test_deserialize_with_viewport_state(self):
        """CGSSerializer.deserialize should extract viewport state."""
        root_data = {"root": {"id": "root", "text": "Root", "children": []}}
        viewport = {"center_x": 400.0, "center_y": 300.0, "zoom_level": 1.5}

        # Serialize with viewport
        cgs_bytes = CGSSerializer.serialize(root_data, viewport_state=viewport)

        # Deserialize
        result = CGSSerializer.deserialize(cgs_bytes)

        assert "viewport" in result
        assert result["viewport"] is not None
        assert result["viewport"]["center_x"] == 400.0
        assert result["viewport"]["center_y"] == 300.0
        assert result["viewport"]["zoom_level"] == 1.5

    def test_deserialize_without_viewport_state(self):
        """CGSSerializer.deserialize should handle missing viewport gracefully."""
        root_data = {"root": {"id": "root", "text": "Root", "children": []}}

        # Serialize without viewport
        cgs_bytes = CGSSerializer.serialize(root_data)

        # Deserialize
        result = CGSSerializer.deserialize(cgs_bytes)

        assert "viewport" in result
        assert result["viewport"] is None


class TestLegacyEdgeConfigRemoval:
    """Test that LegacyEdgeConfig has been completely removed."""

    def test_mindmapstyle_has_no_edge_field(self):
        """MindMapStyle should NOT have edge field."""
        style = create_default_template()

        assert not hasattr(style, "edge") or style.edge is None

    def test_serialize_style_no_edge_field(self):
        """serialize_style should NOT produce edge field."""
        style = create_default_template()
        data = serialize_style(style)

        assert "edge" not in data
