"""
Reparent Node Command - Application Layer

Command to move a node from one parent to another.
Supports undo/redo functionality for drag-and-drop operations.
"""

from typing import TYPE_CHECKING

from cogist.application.commands.command import Command

if TYPE_CHECKING:
    from cogist.domain.entities.node import Node


class ReparentNodeCommand(Command):
    """
    Command to reparent a node (move it to a new parent).

    This command handles the complete operation of:
    - Removing node from old parent
    - Adding node to new parent
    - Sorting children by Y position
    - Updating depths recursively
    - Managing locked position state

    Attributes:
        dragged_node: The node being moved
        old_parent: Original parent node
        new_parent: New parent node
        old_index: Original index in old parent's children list
        is_cross_side: Whether the drag crossed sides (left/right)
        subtree_flipped: Whether the subtree side was flipped
    """

    def __init__(
        self,
        dragged_node: "Node",
        old_parent: "Node | None",
        new_parent: "Node",
        old_index: int,
        is_cross_side: bool = False,
    ):
        """
        Initialize the reparent node command.

        Args:
            dragged_node: The node being moved
            old_parent: Original parent node (can be None if root)
            new_parent: New parent node
            old_index: Original index in old parent's children list
            is_cross_side: Whether the drag crossed sides
        """
        self.dragged_node = dragged_node
        self.old_parent = old_parent
        self.new_parent = new_parent
        self.old_index = old_index
        self.is_cross_side = is_cross_side
        self.subtree_flipped = False  # Track if subtree was flipped

    def execute(self) -> None:
        """
        Execute the command - move node to new parent.

        This removes the node from its old parent and adds it to the new parent.
        Children are sorted by Y position to maintain visual order.
        """
        # Remove from old parent if exists
        if self.old_parent and self.dragged_node in self.old_parent.children:
            self.old_parent.remove_child(self.dragged_node)

        # Add to new parent
        self.new_parent.add_child(self.dragged_node)

        # Sort children by Y position to maintain visual order
        # Note: This requires UI items to exist, so sorting happens in Presentation layer
        # For now, we just add the node; sorting will be handled by the view

        # Update depths recursively
        self._update_depths_recursive(self.dragged_node)

        # Mark top-level ancestor as locked
        top_level_node = self._get_top_level_ancestor(self.dragged_node)
        if top_level_node:
            top_level_node.is_locked_position = True

    def undo(self) -> None:
        """
        Undo the command - restore node to original parent.

        This reverses the reparenting operation, restoring the node to its
        original parent at the original index.
        """
        # Remove from new parent
        if self.dragged_node in self.new_parent.children:
            self.new_parent.remove_child(self.dragged_node)

        # Restore to old parent at original index
        if self.old_parent:
            # CRITICAL: Must set parent reference before inserting
            # children.insert() doesn't set parent, unlike add_child()
            self.dragged_node.parent = self.old_parent
            self.old_parent.children.insert(self.old_index, self.dragged_node)

            # Update depth for the restored node based on old parent
            self.dragged_node.depth = self.old_parent.depth + 1
        else:
            # If old_parent was None (root), this shouldn't happen for non-root nodes
            # but we handle it gracefully
            self.dragged_node.parent = None
            self.dragged_node.depth = 0

        # Restore locked position state for the node and all descendants
        self._restore_locked_positions(self.dragged_node)

        # Update depths recursively for all descendants
        for child in self.dragged_node.children:
            self._update_depths_recursive(child)

    def _update_depths_recursive(self, node: "Node") -> None:
        """
        Update depth for a node and all its descendants.

        Args:
            node: The node to update depths for
        """
        # Calculate new depth based on parent
        if node.parent:
            node.depth = node.parent.depth + 1
        else:
            node.depth = 0  # Root node

        # Recursively update children
        for child in node.children:
            self._update_depths_recursive(child)

    def _get_top_level_ancestor(self, node: "Node") -> "Node":
        """
        Get the direct child of root for this node.

        Args:
            node: The node to find top-level ancestor for

        Returns:
            The top-level ancestor (direct child of root)
        """
        current = node
        while current.parent and not current.parent.is_root:
            current = current.parent
        return current

    def _restore_locked_positions(self, node: "Node") -> None:
        """
        Recursively restore locked position state for a node and all descendants.

        Args:
            node: The node to restore locked positions for
        """
        # Set locked position flag
        node.is_locked_position = True

        # Recursively process children
        for child in node.children:
            self._restore_locked_positions(child)
