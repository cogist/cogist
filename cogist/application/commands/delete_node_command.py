"""
Delete Node Command - Application Layer

Command to delete a node from the mind map.
Supports undo/redo functionality.
"""

from typing import TYPE_CHECKING

from cogist.application.commands.command import Command

if TYPE_CHECKING:
    from cogist.domain.entities.node import Node


class DeleteNodeCommand(Command):
    """
    Command to delete a node and all its children.

    Attributes:
        parent_node: Parent node (to restore child after undo)
        node_to_delete: The node to be deleted
        original_index: Original index in parent's children list
    """

    def __init__(self, parent_node: "Node", node_to_delete: "Node"):
        """
        Initialize the delete node command.

        Args:
            parent_node: Parent node (to restore child after undo)
            node_to_delete: The node to be deleted
        """
        self.parent_node = parent_node
        self.node_to_delete = node_to_delete
        self.original_index: int | None = None

    def execute(self) -> None:
        """
        Execute the command - delete the node.

        This removes the node from its parent and stores the index for undo.
        All children will also be removed.
        """
        # Store original index for proper restoration
        if self.node_to_delete in self.parent_node.children:
            self.original_index = self.parent_node.children.index(self.node_to_delete)
            self.parent_node.remove_child(self.node_to_delete)

    def undo(self) -> None:
        """
        Undo the command - restore the deleted node.

        This adds the node back to its original position in parent's children.
        All descendants are also restored with their locked positions preserved.
        """
        if self.original_index is not None:
            # Insert back at original position
            self.parent_node.children.insert(self.original_index, self.node_to_delete)

            # Restore locked position state for the node and all descendants
            self._restore_locked_positions(self.node_to_delete)

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
