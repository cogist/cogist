"""Drag Handler - Application Layer

Coordinates drag operations between Presentation and Domain layers.
"""

from typing import Protocol

from cogist.domain.entities import Node
from cogist.domain.value_objects.position import Position


class INodeProvider(Protocol):
    """Interface for providing node information to DragHandler.

    Implemented by Presentation Layer to abstract UI dependencies.
    """

    def get_node_position(self, node_id: str) -> tuple[float, float]:
        """Get the position of a node."""
        ...

    def get_node_bounds(self, node_id: str) -> tuple[float, float, float, float]:
        """Get the bounding box of a node (x, y, width, height)."""
        ...

    def get_all_node_ids(self) -> list[str]:
        """Get all node IDs in the scene."""
        ...


class DragHandler:
    """Handles drag detection logic.

    Coordinates between UI events and domain logic to detect
    potential parent nodes during drag operations.
    """

    def __init__(self, root_node: Node, node_provider: INodeProvider):
        """Initialize DragHandler.

        Args:
            root_node: The root node of the mind map tree
            node_provider: Interface to access node information
        """
        self.root_node = root_node
        self.node_provider = node_provider

    def detect_potential_parent(
        self,
        dragged_node_id: str,
        mouse_pos: Position
    ) -> Node | None:
        """Detect the best potential parent based on anchor point distance.

        Uses current position to determine which side the node is on.
        Distance is calculated from dragged node center to candidate's anchor point.

        Args:
            dragged_node_id: ID of the node being dragged
            mouse_pos: Current mouse position (used for reference, actual detection uses node positions)

        Returns:
            The best candidate parent node, or None if no valid candidate
        """
        # Find the dragged node in the tree
        dragged_node = self._find_node_by_id(self.root_node, dragged_node_id)
        if not dragged_node:
            return None

        # Get dragged node position
        dragged_pos = self.node_provider.get_node_position(dragged_node_id)
        dragged_bounds = self.node_provider.get_node_bounds(dragged_node_id)

        # Calculate dragged node center
        dragged_center_x = dragged_pos[0] + dragged_bounds[2] / 2
        dragged_center_y = dragged_pos[1] + dragged_bounds[3] / 2

        # Determine current side based on root position
        root_pos = self.node_provider.get_node_position(self.root_node.id)
        root_x = root_pos[0]
        is_currently_right = dragged_center_x >= root_x

        best_candidate = None
        best_distance = float('inf')

        # Iterate through all nodes to find potential parents
        for node_id in self.node_provider.get_all_node_ids():
            if node_id == dragged_node_id:
                continue  # Skip self

            target_node = self._find_node_by_id(self.root_node, node_id)
            if not target_node:
                continue

            # Cannot be descendant (would create cycle)
            if target_node in dragged_node.get_all_descendants():
                continue

            # Get target node position and bounds
            target_pos = self.node_provider.get_node_position(node_id)
            target_bounds = self.node_provider.get_node_bounds(node_id)

            # For right-side dragged node, look for nodes on the left (smaller x)
            # For left-side dragged node, look for nodes on the right (larger x)
            # Compare using target's top-left x coordinate (not center)
            if is_currently_right:
                if target_pos[0] >= dragged_center_x:
                    continue  # Skip nodes on the right or same x
            else:
                if target_pos[0] <= dragged_center_x:
                    continue  # Skip nodes on the left or same x

            # Calculate anchor point for candidate node
            # Right side: use right edge center; Left side: use left edge center
            if is_currently_right:
                # Candidate is on left, use its right edge as anchor
                anchor_x = target_pos[0] + target_bounds[2]
                anchor_y = target_pos[1] + target_bounds[3] / 2
            else:
                # Candidate is on right, use its left edge as anchor
                anchor_x = target_pos[0]
                anchor_y = target_pos[1] + target_bounds[3] / 2

            # Calculate Euclidean distance from dragged center to candidate anchor
            dx = dragged_center_x - anchor_x
            dy = dragged_center_y - anchor_y
            distance = (dx * dx + dy * dy) ** 0.5

            if distance < best_distance:
                best_distance = distance
                best_candidate = target_node

        return best_candidate

    def _find_node_by_id(self, node: Node, target_id: str) -> Node | None:
        """Find a node by ID using depth-first search.

        Args:
            node: Current node to check
            target_id: Target node ID

        Returns:
            The found node, or None if not found
        """
        if node.id == target_id:
            return node

        for child in node.children:
            result = self._find_node_by_id(child, target_id)
            if result:
                return result

        return None
