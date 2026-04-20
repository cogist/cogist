"""MindMap Repository Interface - Domain Layer

Defines the abstract interface for mind map persistence.
Follows the Repository pattern from DDD.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class MindMapRepositoryInterface(ABC):
    """Abstract interface for mind map repository

    This interface defines the contract for mind map persistence operations.
    Concrete implementations can use different storage backends (JSON files,
    SQLite, PostgreSQL, etc.).

    Design principles:
    1. Dependency Inversion: Application layer depends on this interface,
       not concrete implementations
    2. Single Responsibility: Only handles persistence operations
    3. Testability: Easy to mock for unit tests
    """

    @abstractmethod
    def save(self, root_node: Any, file_path: str | Path, style_config: Any = None) -> Path:
        """Save a mind map to storage

        Args:
            root_node: Root node of the mind map tree
            file_path: Path to save the file to
            style_config: Optional MindMapStyle configuration

        Returns:
            Path to the saved file

        Raises:
            OSError: If saving fails
            ValueError: If root_node is invalid
        """
        pass

    @abstractmethod
    def load(self, file_path: str | Path) -> tuple[Any, Any | None]:
        """Load a mind map from storage

        Args:
            file_path: Path to load the file from

        Returns:
            Tuple of (root_node, style_config). style_config may be None.

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
            OSError: If loading fails
        """
        pass

    @abstractmethod
    def exists(self, file_path: str | Path) -> bool:
        """Check if a mind map file exists

        Args:
            file_path: Path to check

        Returns:
            True if file exists, False otherwise
        """
        pass

    @abstractmethod
    def delete(self, file_path: str | Path) -> None:
        """Delete a mind map file

        Args:
            file_path: Path to delete

        Raises:
            FileNotFoundError: If file doesn't exist
            OSError: If deletion fails
        """
        pass

    @property
    @abstractmethod
    def current_file(self) -> Path | None:
        """Get the currently active file path

        Returns:
            Path to current file, or None if no file is active
        """
        pass

    @property
    @abstractmethod
    def last_saved(self) -> Any | None:
        """Get the timestamp of last successful save

        Returns:
            datetime of last save, or None if never saved
        """
        pass
