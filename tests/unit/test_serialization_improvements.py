"""Unit tests for serialization improvements."""

from cogist.domain.styles.enums import NodeRole
from cogist.domain.styles.extended_styles import RoleStyle
from cogist.domain.styles.style_config import DEFAULT_BRANCH_COLORS, MindMapStyle
from cogist.domain.styles.style_resolver import deserialize_style, serialize_style
from cogist.infrastructure.io.cgs_serializer import CGSSerializer


def _create_test_template() -> MindMapStyle:
    """Create a default MindMapStyle for testing purposes.

    This is a test-only helper function. Production code should load
    templates from JSON files (user directory or built-in assets).
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
        bg_color_index=9,
        bg_brightness=1.0,
        bg_opacity=255,
        border_enabled=True,
        border_width=3,
        border_color_index=9,
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
        max_text_width=0,
    )

    return style


class TestStyleSerialization:
    """Test MindMapStyle serialization without template/color_scheme references."""

    def test_serialize_style_no_template_name(self):
        """serialize_style should NOT include template_name."""
        style = _create_test_template()
        data = serialize_style(style)

        assert "template_name" not in data
        assert "color_scheme_name" not in data

    def test_serialize_style_includes_spacing_config(self):
        """serialize_style should include spacing configurations in role_styles."""
        style = _create_test_template()
        data = serialize_style(style)

        # Spacing is now per-role, not global
        assert "role_styles" in data
        assert "primary" in data["role_styles"]
        assert "parent_child_spacing" in data["role_styles"]["primary"]
        assert "sibling_spacing" in data["role_styles"]["primary"]

    def test_serialize_style_no_connector_config(self):
        """serialize_style should NOT include per-depth connector config (uses role-based)."""
        style = _create_test_template()
        data = serialize_style(style)

        assert "connector_config_by_depth" not in data
        assert "max_text_width_by_depth" not in data

    def test_deserialize_style_no_template_name(self):
        """deserialize_style should work without template_name."""
        data = {
            "name": "Test Style",
            "branch_colors": ["#FFFFFFFF"] * 10,
            "role_styles": {
                "root": {
                    "role": "root",
                    "parent_child_spacing": 80.0,
                    "sibling_spacing": 60.0,
                }
            },
        }

        style = deserialize_style(data)

        assert style.name == "Test Style"
        assert style.role_styles[NodeRole.ROOT].parent_child_spacing == 80.0
        assert style.role_styles[NodeRole.ROOT].sibling_spacing == 60.0
        assert not hasattr(style, "template_name") or style.template_name is None

    def test_serialize_deserialize_roundtrip(self):
        """Style should survive serialize -> deserialize roundtrip."""
        original = _create_test_template()

        # Serialize
        data = serialize_style(original)

        # Deserialize
        restored = deserialize_style(data)

        # Verify key fields
        assert restored.name == original.name
        # Spacing is now per-role
        assert restored.role_styles[NodeRole.PRIMARY].parent_child_spacing == original.role_styles[NodeRole.PRIMARY].parent_child_spacing
        assert restored.role_styles[NodeRole.PRIMARY].sibling_spacing == original.role_styles[NodeRole.PRIMARY].sibling_spacing


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
        style = _create_test_template()

        assert not hasattr(style, "edge") or style.edge is None

    def test_serialize_style_no_edge_field(self):
        """serialize_style should NOT produce edge field."""
        style = _create_test_template()
        data = serialize_style(style)

        assert "edge" not in data
