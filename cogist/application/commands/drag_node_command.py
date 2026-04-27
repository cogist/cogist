"""
Drag Node Command - Application Layer

Command for dragging a node and optionally reparenting it.
Supports undo/redo for the final position and parent change.
"""


from cogist.application.commands.command import Command
from cogist.domain.node import Node


class DragNodeCommand(Command):
    """
    Command for dragging a node.

    This command captures the state before and after a drag operation,
    allowing for undo/redo of the position and parent changes.
    """

    def __init__(
        self,
        node: Node,
        old_position: tuple[float, float],
        new_position: tuple[float, float],
        old_parent: Node | None,
        new_parent: Node | None,
        old_is_right_side: bool,
        new_is_right_side: bool,
    ):
        """
        Initialize the drag node command.

        Args:
            node: The node being dragged
            old_position: Position before drag (x, y)
            new_position: Position after drag (x, y)
            old_parent: Parent before drag (or None)
            new_parent: Parent after drag (or None)
            old_is_right_side: Whether node was on right side before drag
            new_is_right_side: Whether node is on right side after drag
        """
        self.node = node
        self.old_position = old_position
        self.new_position = new_position
        self.old_parent = old_parent
        self.new_parent = new_parent
        self.old_is_right_side = old_is_right_side
        self.new_is_right_side = new_is_right_side

    def execute(self) -> None:
        """Execute the drag - apply the new position and parent."""
        self._apply_state(self.new_position, self.new_parent, self.new_is_right_side)

    def undo(self) -> None:
        """Undo the drag - restore the old position and parent."""
        self._apply_state(self.old_position, self.old_parent, self.old_is_right_side)

    def _apply_state(
        self,
        position: tuple[float, float],
        parent: Node | None,
        is_right_side: bool,
    ) -> None:
        """
        Apply a state to the node.

        Args:
            position: Position to apply (x, y)
            parent: Parent to apply (or None)
            is_right_side: Whether node should be on right side
        """
        # Update position
        self.node.position = list(position)

        # Update parent if changed
        if parent != self.node.parent:
            if self.node.parent and self.node in self.node.parent.children:
                # Remove from old parent's children
                self.node.parent.children.remove(self.node)

            self.node.parent = parent

            if parent and self.node not in parent.children:
                # Add to new parent's children
                parent.children.append(self.node)

        # Update is_right_side flag (for presentation layer to use)
        # Note: This is a domain property that the presentation layer observes
        self.node.is_right_side = is_right_side
