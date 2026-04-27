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

        Uses current VISUAL position to determine which side the node is on.
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

        # CRITICAL: Determine current side based on VISUAL position (dragged_pos[0])
        # NOT logical position (dragged_node.position[0]), because during drag the node
        # may have crossed sides visually but its logical position hasn't been updated yet.
        # This ensures parent detection works correctly during cross-side drags.
        root_pos = self.node_provider.get_node_position(self.root_node.id)
        root_x = root_pos[0]
        is_currently_right = dragged_pos[0] >= root_x

        # CRITICAL: NodeItem's rect is centered, so scenePos() returns center point.
        # To get edges, we need: left = center_x - width/2, right = center_x + width/2
        if is_currently_right:
            dragged_anchor_x = dragged_pos[0] - dragged_bounds[2] / 2  # Left edge = center - half_width
            dragged_anchor_y = dragged_pos[1]
        else:
            dragged_anchor_x = dragged_pos[0] + dragged_bounds[2] / 2  # Right edge = center + half_width
            dragged_anchor_y = dragged_pos[1]

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

            # CRITICAL: Check if candidate is on the SAME side as the dragged node
            # Right nodes should only find right-side parents (including root)
            # Left nodes should only find left-side parents (including root)
            # IMPORTANT: Use candidate's VISUAL position (target_pos[0]), not logical position
            # because during drag, candidates may have been moved visually and we need to
            # match their current visual position with the dragged node's visual position.
            target_is_right = target_pos[0] >= root_x

            # Skip candidates on DIFFERENT sides (but allow root node)
            # Right nodes need right-side parents, left nodes need left-side parents
            if not target_node.is_root and target_is_right != is_currently_right:
                continue

            # FIX: Compare using anchor points, not center coordinates
            # CRITICAL: NodeItem's rect is centered, so:
            #   left_edge = center_x - width/2
            #   right_edge = center_x + width/2
            # For right-side dragged node: find candidates whose right edge anchor is to the left of dragged node's left edge anchor
            # For left-side dragged node: find candidates whose left edge anchor is to the right of dragged node's right edge anchor
            if is_currently_right:
                candidate_anchor_x = target_pos[0] + target_bounds[2] / 2  # Candidate's right edge = center + half_width
                if candidate_anchor_x >= dragged_anchor_x:
                    continue  # Skip candidates on the right or same x
            else:
                candidate_anchor_x = target_pos[0] - target_bounds[2] / 2  # Candidate's left edge = center - half_width
                if candidate_anchor_x <= dragged_anchor_x:
                    continue  # Skip candidates on the left or same x

            # Calculate anchor point for candidate node
            # CRITICAL: NodeItem's rect is centered, so:
            #   Right side: right edge = center_x + width/2
            #   Left side: left edge = center_x - width/2
            if is_currently_right:
                # Candidate is on left, use its right edge as anchor
                anchor_x = target_pos[0] + target_bounds[2] / 2
                anchor_y = target_pos[1]
            else:
                # Candidate is on right, use its left edge as anchor
                anchor_x = target_pos[0] - target_bounds[2] / 2
                anchor_y = target_pos[1]

            # Calculate Euclidean distance between two anchor points
            dx = dragged_anchor_x - anchor_x
            dy = dragged_anchor_y - anchor_y
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
