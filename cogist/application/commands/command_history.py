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

        Supports coalescing for ChangeStyleCommand:
        - If the new command is a ChangeStyleCommand and can be coalesced with the last command,
          they will be merged into a single command (only keeping the last value for numeric fields).

        Args:
            command: Command to push
        """
        # Check if we should coalesce with the last command
        if (
            self.undo_stack
            and hasattr(command, 'should_coalesce_with')
            and hasattr(command, 'merge_with')
        ):
            last_command = self.undo_stack[-1]
            if command.should_coalesce_with(last_command):
                # Merge the new command into the last command
                last_command.merge_with(command)
                # Don't add the new command to the stack
                return

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

    def peek_last_undo_command(self):
        """Peek at the last command in undo stack without popping it.

        Returns:
            The last command or None if stack is empty
        """
        if self.undo_stack:
            return self.undo_stack[-1]
        return None

    def peek_last_redo_command(self):
        """Peek at the last command in redo stack without popping it.

        Returns:
            The last command or None if stack is empty
        """
        if self.redo_stack:
            return self.redo_stack[-1]
        return None

    def clear(self) -> None:
        """Clear both undo and redo stacks."""
        self.undo_stack.clear()
        self.redo_stack.clear()

    def __len__(self) -> int:
        """Return the number of commands in the undo stack."""
        return len(self.undo_stack)

    def __bool__(self) -> bool:
        """Return True if this CommandHistory object exists (regardless of stack size)."""
        return True

    def get_command_count(self) -> int:
        """Return the total number of commands in undo stack."""
        return len(self.undo_stack)
