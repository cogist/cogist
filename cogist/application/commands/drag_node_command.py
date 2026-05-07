"""
Drag Node Command - Application Layer

Command for dragging a node with full undo/redo support.
Captures only the minimal state needed to restore the structure.
"""


from typing import TYPE_CHECKING

from cogist.application.commands.command import Command

if TYPE_CHECKING:
    from cogist.domain.entities.node import Node


class DragNodeCommand(Command):
    """
    Command for dragging a node with undo/redo support.

    Records two scenarios:
    1. Simple drag (no layout rebalance): Only old_parent and old_index
    2. Complex drag (with layout rebalance): Plus old_side_primary_nodes

    The undo() method only restores data structure - layout is triggered
    by the Presentation Layer after undo completes.
    """

    def __init__(
        self,
        dragged_node: "Node",
        old_parent: "Node | None",
        new_parent: "Node",
        old_index: int,
        old_left_primary_node_ids: list[str] | None = None,
        is_cross_side: bool = False,
    ):
        """
        Initialize the drag node command.

        Args:
            dragged_node: The node being dragged
            old_parent: Parent before drag
            new_parent: Parent after drag
            old_index: Original index in old_parent's children list
            old_left_primary_node_ids: IDs of primary nodes that were on left side before drag (optional)
            is_cross_side: Whether drag crossed from left to right or vice versa
        """
        self.dragged_node = dragged_node
        self.old_parent = old_parent
        self.new_parent = new_parent
        self.old_index = old_index
        self.old_left_primary_node_ids = old_left_primary_node_ids
        self.is_cross_side = is_cross_side

    def execute(self) -> None:
        """Execute the drag - apply new position and parent."""
        # Remove from old parent
        if self.old_parent and self.dragged_node in self.old_parent.children:
            self.old_parent.remove_child(self.dragged_node)

        # Add to new parent
        self.new_parent.add_child(self.dragged_node)

        # Update depths recursively
        self._update_depths_recursive(self.dragged_node)

    def undo(self) -> None:
        """
        Undo the drag - restore data structure only.

        This restores:
        1. Parent-child relationships
        2. Sibling order in old parent
        3. Primary nodes side information (if recorded)

        Note: Does NOT call layout.layout() - that's handled by Presentation Layer.
        """
        # Remove from new parent
        if self.dragged_node in self.new_parent.children:
            self.new_parent.remove_child(self.dragged_node)

        # Restore to old parent at original index
        if self.old_parent:
            # Insert at original index
            self.old_parent.children.insert(self.old_index, self.dragged_node)
            self.dragged_node.parent = self.old_parent
            self.dragged_node.depth = self.old_parent.depth + 1

            # If we have left side primary node IDs, restore side information
            if self.old_left_primary_node_ids:
                self._restore_primary_nodes_sides()
        else:
            # Should not happen for non-root nodes
            self.dragged_node.parent = None
            self.dragged_node.depth = 0

        # Update depths for all affected nodes
        if self.old_parent:
            self._update_depths_recursive(self.old_parent)
        self._update_depths_recursive(self.new_parent)

    def _restore_primary_nodes_sides(self) -> None:
        """
        Restore the side (left/right) information for primary nodes.

        This sets temporary position[0] values to guide the layout algorithm:
        - Left side nodes: position[0] = -400.0
        - Right side nodes: position[0] = 800.0

        The layout algorithm will use these as hints to reassign nodes to correct sides.

        Note: Uses node IDs for memory efficiency - only stores ID strings instead of node references.
        """
        if not self.old_left_primary_node_ids:
            return

        # Find root node by looking up any node from the ID list
        root = None
        left_nodes = []
        for node_id in self.old_left_primary_node_ids:
            node = self._find_node_by_id(node_id)
            if node and node.parent and node.parent.is_root:
                root = node.parent
                left_nodes.append(node)

        if not root or not left_nodes:
            return

        # Set left side nodes to negative X (will be assigned to left by layout)
        for node in left_nodes:
            node.position = (-400.0, node.position[1])

        # Set right side nodes to positive X (will be assigned to right by layout)
        for node in root.children:
            if node.id not in self.old_left_primary_node_ids:
                node.position = (800.0, node.position[1])

    def _find_node_by_id(self, node_id: str) -> "Node | None":
        """
        Find a node by ID starting from the dragged node's hierarchy.

        Args:
            node_id: The ID of the node to find

        Returns:
            The node if found, None otherwise
        """
        # Start from dragged node and traverse up to find root
        current = self.dragged_node
        while current.parent:
            current = current.parent

        # Now current should be root, search down
        return self._search_node_by_id_recursive(current, node_id)

    def _search_node_by_id_recursive(
        self, node: "Node", node_id: str
    ) -> "Node | None":
        """Recursively search for a node by ID."""
        if node.id == node_id:
            return node

        for child in node.children:
            result = self._search_node_by_id_recursive(child, node_id)
            if result:
                return result

        return None

    def _update_depths_recursive(self, node: "Node") -> None:
        """Update depth for a node and all its descendants."""
        if node.parent:
            node.depth = node.parent.depth + 1
        else:
            node.depth = 0

        for child in node.children:
            self._update_depths_recursive(child)
