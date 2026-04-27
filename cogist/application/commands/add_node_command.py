"""
Add Node Command - Application Layer

Command to add a new node to the mind map.
Supports undo/redo functionality.
"""

from typing import TYPE_CHECKING

from cogist.application.commands.command import Command

if TYPE_CHECKING:
    from cogist.domain.entities.node import Node


class AddNodeCommand(Command):
    """
    Command to add a child node to a parent node.

    Attributes:
        parent_node: The parent node to add child to
        new_node: The new node to be added
        node_text: Text content for the new node
    """

    def __init__(self, parent_node: "Node", node_text: str = "New Node"):
        """
        Initialize the add node command.

        Args:
            parent_node: Parent node to add child to
            node_text: Text content for the new node
        """
        self.parent_node = parent_node
        self.node_text = node_text
        self.new_node: Node | None = None

    def execute(self) -> None:
        """
        Execute the command - add the new node.

        This creates a new node and adds it as a child to the parent node.
        The layout will need to be recalculated after this operation.
        """
        import uuid

        from cogist.domain.entities.node import Node

        # Create new node only if it doesn't exist (for redo, reuse existing node)
        if self.new_node is None:
            # Create new node with unique ID
            self.new_node = Node(id=str(uuid.uuid4()), text=self.node_text)

            # Lock the new node's position to prevent layout rebalancing from moving it
            self.new_node.is_locked_position = True

        # Add to parent
        self.parent_node.add_child(self.new_node)

    def undo(self) -> None:
        """
        Undo the command - remove the new node.

        This removes the node from its parent.
        The layout will need to be recalculated after this operation.
        """
        if self.new_node and self.new_node in self.parent_node.children:
            self.parent_node.remove_child(self.new_node)
