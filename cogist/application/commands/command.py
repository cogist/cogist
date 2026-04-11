"""
Command Pattern - Application Layer

Commands encapsulate operations that can be undone/redone.
All commands implement the Command interface with execute() and undo() methods.
"""

from abc import ABC, abstractmethod


class Command(ABC):
    """
    Abstract base class for all commands.

    Commands must implement:
    - execute(): Perform the operation
    - undo(): Reverse the operation
    """

    @abstractmethod
    def execute(self) -> None:
        """Execute the command."""
        pass

    @abstractmethod
    def undo(self) -> None:
        """Undo the command."""
        pass
