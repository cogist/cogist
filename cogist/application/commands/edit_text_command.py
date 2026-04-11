"""
Edit Text Command - Application Layer

Command to edit the text content of a node.
Supports undo/redo functionality.
"""

from typing import TYPE_CHECKING

from cogist.application.commands.command import Command

if TYPE_CHECKING:
    from cogist.domain.entities.node import Node


class EditTextCommand(Command):
    """
    Command to edit the text content of a node.

    Attributes:
        node: The node to edit
        old_text: Original text content (stored for undo)
        new_text: New text content
    """

    def __init__(self, node: "Node", new_text: str):
        """
        Initialize the edit text command.

        Args:
            node: The node to edit
            new_text: New text content
        """
        self.node = node
        self.new_text = new_text
        self.old_text: str = node.text

    def execute(self) -> None:
        """
        Execute the command - update the node text.

        This changes the text content of the node.
        """
        self.node.text = self.new_text

    def undo(self) -> None:
        """
        Undo the command - restore the original text.

        This reverts the text back to what it was before the command.
        """
        self.node.text = self.old_text
