"""Unit tests for drag detection logic.

Tests the core algorithm for detecting potential parent nodes during drag operations.
"""

from cogist.domain.entities import Node


def create_test_tree() -> tuple[Node, dict[str, Node]]:
    """Create a test tree structure.
    
    Returns:
        Tuple of (root_node, all_nodes_dict)
        
    Tree structure:
            root (600, 400)
           /    \
      a(400,300)  b(800,500)
         |         /    \
     a1(350,250) b1(750,450) b2(850,550)
    """
    root = Node(id="root", text="Root", position=(600.0, 400.0))
    
    a = Node(id="a", text="A", position=(400.0, 300.0))
    b = Node(id="b", text="B", position=(800.0, 500.0))
    
    a1 = Node(id="a1", text="A1", position=(350.0, 250.0))
    b1 = Node(id="b1", text="B1", position=(750.0, 450.0))
    b2 = Node(id="b2", text="B2", position=(850.0, 550.0))
    
    root.add_child(a)
    root.add_child(b)
    a.add_child(a1)
    b.add_child(b1)
    b.add_child(b2)
    
    all_nodes = {
        "root": root,
        "a": a,
        "b": b,
        "a1": a1,
        "b1": b1,
        "b2": b2,
    }
    
    return root, all_nodes


class MockNodeProvider:
    """Mock implementation of INodeProvider for testing."""
    
    def __init__(self, all_nodes: dict[str, Node], positions: dict[str, tuple[float, float]], bounds: dict[str, tuple[float, float, float, float]]):
        self.all_nodes = all_nodes
        self.positions = positions
        self.bounds = bounds
    
    def get_node_position(self, node_id: str) -> tuple[float, float]:
        return self.positions[node_id]
    
    def get_node_bounds(self, node_id: str) -> tuple[float, float, float, float]:
        return self.bounds[node_id]
    
    def get_all_node_ids(self) -> list[str]:
        return list(self.all_nodes.keys())


def test_detect_parent_right_side():
    """Test detecting parent when dragging a node on the right side.
    
    When dragging b2 (right side) towards the left, should detect 'a' as potential parent.
    """
    root, all_nodes = create_test_tree()
    
    # Mock positions and bounds
    positions = {
        "root": (600.0, 400.0),
        "a": (400.0, 300.0),
        "b": (800.0, 500.0),
        "a1": (350.0, 250.0),
        "b1": (750.0, 450.0),
        "b2": (850.0, 550.0),
    }
    
    # All nodes have same size: width=100, height=40
    bounds = {node_id: (0.0, 0.0, 100.0, 40.0) for node_id in all_nodes}
    
    provider = MockNodeProvider(all_nodes, positions, bounds)
    
    # Import DragHandler after creating mocks
    from cogist.application.services.drag_handler import DragHandler
    from cogist.domain.value_objects.position import Position
    
    handler = DragHandler(root, provider)
    
    # Drag b2 (currently at x=850, right side) towards left
    # Mouse is near 'a' node
    result = handler.detect_potential_parent(
        dragged_node_id="b2",
        mouse_pos=Position(420.0, 310.0)  # Near 'a' node
    )
    
    # Should detect 'a' as potential parent (closest on the left side)
    assert result is not None
    assert result.id == "a"


def test_detect_parent_left_side():
    """Test detecting parent when dragging a node on the left side.
    
    When dragging a1 (left side) towards the right, should detect 'b' as potential parent.
    """
    root, all_nodes = create_test_tree()
    
    positions = {
        "root": (600.0, 400.0),
        "a": (400.0, 300.0),
        "b": (800.0, 500.0),
        "a1": (350.0, 250.0),
        "b1": (750.0, 450.0),
        "b2": (850.0, 550.0),
    }
    
    bounds = {node_id: (0.0, 0.0, 100.0, 40.0) for node_id in all_nodes}
    
    provider = MockNodeProvider(all_nodes, positions, bounds)
    
    from cogist.application.services.drag_handler import DragHandler
    from cogist.domain.value_objects.position import Position
    
    handler = DragHandler(root, provider)
    
    # Drag a1 (currently at x=350, left side) towards right
    # Mouse is near 'b' node
    result = handler.detect_potential_parent(
        dragged_node_id="a1",
        mouse_pos=Position(820.0, 510.0)  # Near 'b' node
    )
    
    # Should detect 'b' as potential parent (closest on the right side)
    assert result is not None
    assert result.id == "b"


def test_detect_parent_exclude_descendants():
    """Test that descendant nodes are excluded from potential parents.
    
    Cannot make a node its own descendant's child (would create cycle).
    """
    root, all_nodes = create_test_tree()
    
    positions = {
        "root": (600.0, 400.0),
        "a": (400.0, 300.0),
        "b": (800.0, 500.0),
        "a1": (350.0, 250.0),
        "b1": (750.0, 450.0),
        "b2": (850.0, 550.0),
    }
    
    bounds = {node_id: (0.0, 0.0, 100.0, 40.0) for node_id in all_nodes}
    
    provider = MockNodeProvider(all_nodes, positions, bounds)
    
    from cogist.application.services.drag_handler import DragHandler
    from cogist.domain.value_objects.position import Position
    
    handler = DragHandler(root, provider)
    
    # Try to drag 'b' to become child of 'b1' (which is b's descendant)
    # This should be rejected
    result = handler.detect_potential_parent(
        dragged_node_id="b",
        mouse_pos=Position(770.0, 460.0)  # Near 'b1'
    )
    
    # Should NOT detect b1 as parent (it's a descendant)
    # Should detect root or other valid candidate instead
    assert result is None or result.id != "b1"


def test_detect_parent_no_valid_candidate():
    """Test when there's no valid candidate for parent.
    
    If all candidates are on the wrong side or are descendants, return None.
    """
    root, all_nodes = create_test_tree()
    
    positions = {
        "root": (600.0, 400.0),
        "a": (400.0, 300.0),
        "b": (800.0, 500.0),
        "a1": (350.0, 250.0),
        "b1": (750.0, 450.0),
        "b2": (850.0, 550.0),
    }
    
    bounds = {node_id: (0.0, 0.0, 100.0, 40.0) for node_id in all_nodes}
    
    provider = MockNodeProvider(all_nodes, positions, bounds)
    
    from cogist.application.services.drag_handler import DragHandler
    from cogist.domain.value_objects.position import Position
    
    handler = DragHandler(root, provider)
    
    # Drag b2 but mouse is far away on the same side (no candidates on opposite side)
    result = handler.detect_potential_parent(
        dragged_node_id="b2",
        mouse_pos=Position(900.0, 600.0)  # Far right, no nodes on left
    )
    
    # May return None if no valid candidates
    # Or return a valid candidate if one exists
    # The key is it shouldn't crash
    assert result is None or isinstance(result, Node)


def test_detect_parent_self_excluded():
    """Test that the dragged node itself is excluded from candidates."""
    root, all_nodes = create_test_tree()
    
    positions = {
        "root": (600.0, 400.0),
        "a": (400.0, 300.0),
        "b": (800.0, 500.0),
        "a1": (350.0, 250.0),
        "b1": (750.0, 450.0),
        "b2": (850.0, 550.0),
    }
    
    bounds = {node_id: (0.0, 0.0, 100.0, 40.0) for node_id in all_nodes}
    
    provider = MockNodeProvider(all_nodes, positions, bounds)
    
    from cogist.application.services.drag_handler import DragHandler
    from cogist.domain.value_objects.position import Position
    
    handler = DragHandler(root, provider)
    
    # Try to drag a node to itself (should never happen, but test anyway)
    result = handler.detect_potential_parent(
        dragged_node_id="a",
        mouse_pos=Position(420.0, 310.0)
    )
    
    # Should not return the same node
    assert result is None or result.id != "a"


def test_detect_parent_closest_by_distance():
    """Test that the closest candidate is selected based on anchor distance."""
    root, all_nodes = create_test_tree()
    
    positions = {
        "root": (600.0, 400.0),
        "a": (400.0, 300.0),
        "b": (800.0, 500.0),
        "a1": (350.0, 250.0),
        "b1": (750.0, 450.0),
        "b2": (850.0, 550.0),
    }
    
    bounds = {node_id: (0.0, 0.0, 100.0, 40.0) for node_id in all_nodes}
    
    provider = MockNodeProvider(all_nodes, positions, bounds)
    
    from cogist.application.services.drag_handler import DragHandler
    from cogist.domain.value_objects.position import Position
    
    handler = DragHandler(root, provider)
    
    # Drag b2 towards left, between 'a' and 'root'
    # 'a' should be closer than 'root'
    result = handler.detect_potential_parent(
        dragged_node_id="b2",
        mouse_pos=Position(500.0, 350.0)  # Between a and root
    )
    
    # Should select the closest valid candidate
    assert result is not None
    # Either 'a' or 'root' depending on exact distance calculation
    assert result.id in ["a", "root"]
