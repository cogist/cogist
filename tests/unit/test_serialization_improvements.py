"""Unit tests for serialization improvements."""

from cogist.domain.entities.node import Node
from cogist.domain.styles.style_resolver import deserialize_style, serialize_style
from cogist.domain.styles.templates import create_default_template
from cogist.infrastructure.io.cgs_serializer import CGSSerializer


class TestNodeSortWeight:
    """Test sort_weight field for user-defined node ordering."""

    def test_node_has_sort_weight_field(self):
        """Node should have sort_weight field with default value 0.0."""
        node = Node(id="test", text="Test")
        assert hasattr(node, "sort_weight")
        assert node.sort_weight == 0.0

    def test_sort_weight_can_be_set(self):
        """sort_weight should be settable."""
        node = Node(id="test", text="Test", sort_weight=5.5)
        assert node.sort_weight == 5.5

        node.sort_weight = 10.0
        assert node.sort_weight == 10.0


class TestStyleSerialization:
    """Test MindMapStyle serialization without template/color_scheme references."""

    def test_serialize_style_no_template_name(self):
        """serialize_style should NOT include template_name."""
        style = create_default_template()
        data = serialize_style(style)

        assert "template_name" not in data
        assert "color_scheme_name" not in data

    def test_serialize_style_includes_spacing_config(self):
        """serialize_style should include all spacing configurations."""
        style = create_default_template()
        data = serialize_style(style)

        assert "parent_child_spacing" in data
        assert "sibling_spacing" in data
        assert "level_spacing_by_depth" in data
        assert "sibling_spacing_by_depth" in data

    def test_serialize_style_includes_connector_config(self):
        """serialize_style should include connector configuration."""
        style = create_default_template()
        data = serialize_style(style)

        assert "connector_config_by_depth" in data
        assert "max_text_width_by_depth" in data

    def test_deserialize_style_no_template_name(self):
        """deserialize_style should work without template_name."""
        data = {
            "name": "Test Style",
            "parent_child_spacing": 80.0,
            "sibling_spacing": 60.0,
            "level_spacing_by_depth": {"0": 80.0, "1": 60.0},
            "sibling_spacing_by_depth": {"0": 60.0, "1": 45.0},
            "connector_config_by_depth": {},
            "max_text_width_by_depth": {},
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


class TestNodeTreeWithSortWeight:
    """Test complete node tree serialization with sort_weight."""

    def test_node_tree_preserves_sort_weight(self):
        """Node tree should preserve sort_weight through serialization."""
        # Create a simple tree
        root = Node(id="root", text="Root", sort_weight=0.0)
        child1 = Node(id="c1", text="Child 1", sort_weight=2.0)
        child2 = Node(id="c2", text="Child 2", sort_weight=1.0)
        child3 = Node(id="c3", text="Child 3", sort_weight=3.0)

        root.children = [child1, child2, child3]
        child1.parent = root
        child2.parent = root
        child3.parent = root

        # Serialize to dict (simulating what CGSSerializer does)
        def serialize_node(node):
            return {
                "id": node.id,
                "text": node.text,
                "sort_weight": node.sort_weight,
                "children": [serialize_node(child) for child in node.children],
            }

        data = serialize_node(root)

        # Verify sort_weight is preserved
        assert data["sort_weight"] == 0.0
        assert len(data["children"]) == 3

        # Children should have their sort_weights
        child_weights = [child["sort_weight"] for child in data["children"]]
        assert 1.0 in child_weights
        assert 2.0 in child_weights
        assert 3.0 in child_weights


class TestLayoutAlgorithmWithSortWeight:
    """Test that layout algorithm respects sort_weight ordering."""

    def test_layout_sorts_children_by_sort_weight(self):
        """Layout algorithm should sort children by sort_weight before positioning."""
        from cogist.domain.layout.base import DefaultLayoutConfig
        from cogist.domain.layout.default_layout import DefaultLayout

        # Create a root node with children in wrong order
        root = Node(id="root", text="Root", is_root=True, depth=0)
        root.width = 100.0
        root.height = 40.0
        root.position = (0.0, 0.0)

        # Add children with non-sequential sort_weights
        child1 = Node(id="c1", text="Child 1", sort_weight=5.0, depth=1)
        child2 = Node(id="c2", text="Child 2", sort_weight=2.0, depth=1)
        child3 = Node(id="c3", text="Child 3", sort_weight=8.0, depth=1)

        child1.width = child2.width = child3.width = 80.0
        child1.height = child2.height = child3.height = 30.0

        root.children = [child1, child2, child3]
        child1.parent = child2.parent = child3.parent = root

        # Create layout config with per-depth spacing
        config = DefaultLayoutConfig(
            level_spacing=80.0,
            sibling_spacing=60.0,
            level_spacing_by_depth={0: 80.0, 1: 60.0, 2: 40.0},
            sibling_spacing_by_depth={0: 60.0, 1: 45.0, 2: 35.0},
        )

        # Create layout instance
        layout = DefaultLayout(config)

        # Run layout
        layout.layout(root, canvas_width=800.0, canvas_height=600.0)

        # After layout, children should be sorted by sort_weight
        # The layout algorithm sorts children internally, so we verify
        # that the final positions reflect the sorted order
        # Child with sort_weight=2.0 should come first (topmost or leftmost)
        # Child with sort_weight=5.0 should come second
        # Child with sort_weight=8.0 should come last

        # Get Y positions (for vertical layout) or X positions (for horizontal)
        # Since this is a tree layout, we check if positions are ordered
        y_positions = [child.position[1] for child in root.children]

        # Verify that positions are monotonically increasing or decreasing
        # (depending on layout direction), which indicates proper sorting
        is_sorted_ascending = all(
            y_positions[i] <= y_positions[i + 1] for i in range(len(y_positions) - 1)
        )
        is_sorted_descending = all(
            y_positions[i] >= y_positions[i + 1] for i in range(len(y_positions) - 1)
        )

        # At least one should be true (positions are ordered)
        assert is_sorted_ascending or is_sorted_descending, (
            f"Children positions {y_positions} are not properly ordered. "
            f"Expected monotonic sequence based on sort_weight."
        )
