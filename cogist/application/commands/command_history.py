"""
Command History - Application Layer

Manages the history of executed commands for undo/redo functionality.
"""

from cogist.application.commands.command import Command


class CommandHistory:
    """
    Manages command history for undo/redo operations.

    Maintains two stacks:
    - undo_stack: Commands that can be undone
    - redo_stack: Commands that can be redone
    """

    def __init__(self, max_size: int = 100):
        """
        Initialize the command history.

        Args:
            max_size: Maximum number of commands to keep in history
        """
        self.undo_stack: list[Command] = []
        self.redo_stack: list[Command] = []
        self.max_size = max_size

    def push(self, command: Command) -> None:
        """
        Push a command onto the undo stack.

        Args:
            command: Command to push
        """
        self.undo_stack.append(command)

        # Clear redo stack when new command is executed
        self.redo_stack.clear()

        # Limit stack size
        if len(self.undo_stack) > self.max_size:
            self.undo_stack.pop(0)

    def undo(self) -> bool:
        """
        Undo the last command.

        Returns:
            True if undo was successful, False if nothing to undo
        """
        if not self.can_undo():
            return False

        command = self.undo_stack.pop()
        command.undo()
        self.redo_stack.append(command)
        return True

    def redo(self) -> bool:
        """
        Redo the last undone command.

        Returns:
            True if redo was successful, False if nothing to redo
        """
        if not self.can_redo():
            return False

        command = self.redo_stack.pop()
        command.execute()
        self.undo_stack.append(command)
        return True

    def can_undo(self) -> bool:
        """Check if there's a command to undo."""
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        """Check if there's a command to redo."""
        return len(self.redo_stack) > 0

    def clear(self) -> None:
        """Clear both undo and redo stacks."""
        self.undo_stack.clear()
        self.redo_stack.clear()

    def __len__(self) -> int:
        """Return the number of commands in the undo stack."""
        return len(self.undo_stack)

    def get_command_count(self) -> int:
        """Return the total number of commands in undo stack."""
        return len(self.undo_stack)
