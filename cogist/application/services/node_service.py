"""
Node Service - Application Layer

Provides high-level API for node operations.
Encapsulates business logic for node manipulation.
"""

from cogist.application.commands.add_node_command import AddNodeCommand
from cogist.application.commands.command_history import CommandHistory
from cogist.application.commands.delete_node_command import DeleteNodeCommand
from cogist.application.commands.edit_text_command import EditTextCommand
from cogist.domain.entities.node import Node


class NodeService:
    """
    Service for node operations.

    Provides high-level methods for common node operations,
    integrating with the Command pattern for undo/redo support.
    """

    def __init__(self, command_history: CommandHistory | None = None):
        """
        Initialize the node service.

        Args:
            command_history: Optional command history for undo/redo
        """
        self.command_history = command_history or CommandHistory()

    def add_child_node(
        self, parent_node: Node, text: str = "New Node", auto_execute: bool = True
    ) -> Node | None:
        """
        Add a child node to the specified parent.

        Args:
            parent_node: Parent node to add child to
            text: Text content for the new node
            auto_execute: If True, execute the command immediately

        Returns:
            The newly created node, or None if not executed
        """
        command = AddNodeCommand(parent_node, text)

        if auto_execute:
            command.execute()
            self.command_history.push(command)

        return command.new_node

    def delete_node(self, node: Node, auto_execute: bool = True) -> None:
        """
        Delete a node and all its children.

        Args:
            node: Node to delete
            auto_execute: If True, execute the command immediately
        """
        if node.is_root:
            raise ValueError("Cannot delete root node")

        if node.parent is None:
            raise ValueError("Node has no parent")

        command = DeleteNodeCommand(node.parent, node)

        if auto_execute:
            command.execute()
            self.command_history.push(command)

    def edit_node_text(
        self, node: Node, new_text: str, auto_execute: bool = True
    ) -> None:
        """
        Edit the text content of a node.

        Args:
            node: Node to edit
            new_text: New text content
            auto_execute: If True, execute the command immediately
        """
        command = EditTextCommand(node, new_text)

        if auto_execute:
            command.execute()
            self.command_history.push(command)

    def undo(self) -> bool:
        """
        Undo the last operation.

        Returns:
            True if undo was successful, False if nothing to undo
        """
        return self.command_history.undo()

    def redo(self) -> bool:
        """
        Redo the last undone operation.

        Returns:
            True if redo was successful, False if nothing to redo
        """
        return self.command_history.redo()

    def can_undo(self) -> bool:
        """Check if there's an operation to undo."""
        return self.command_history.can_undo()

    def can_redo(self) -> bool:
        """Check if there's an operation to redo."""
        return self.command_history.can_redo()
