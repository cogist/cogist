"""
MindMap Repository - Infrastructure Layer

Handles persistence of mind maps to/from files.
Supports .mwe format (JSON-based).
"""

from datetime import datetime
from pathlib import Path
from typing import Any


class MindMapRepository:
    """
    Repository for mind map persistence.

    Handles saving and loading mind maps in .mwe format,
    which is a JSON file.
    """

    FILE_EXTENSION = ".mwe"
    DEFAULT_ENCODING = "utf-8"

    def __init__(self):
        """Initialize the repository."""
        self.current_file: Path | None = None
        self.last_saved: datetime | None = None

    def save(self, root_node: Any, file_path: str) -> Path:
        """
        Save a mind map to a file.

        Args:
            root_node: Root node of the mind map tree
            file_path: Path to save the file to

        Returns:
            Path to the saved file

        Raises:
            OSError: If saving fails
        """
        path = Path(file_path)

        # Ensure correct extension
        if path.suffix != self.FILE_EXTENSION:
            path = path.with_suffix(self.FILE_EXTENSION)

        try:
            # Convert node to dictionary
            from cogist.infrastructure.io.json_serializer import JSONSerializer

            mind_map_data = {"root": JSONSerializer.node_to_dict(root_node)}

            # Serialize to JSON
            json_string = JSONSerializer.serialize(mind_map_data)

            # Write to file (optionally could use ZIP compression)
            # For now, save as plain JSON for simplicity and debuggability
            # Future: use ZIP compression for large files
            path.write_text(json_string, encoding=self.DEFAULT_ENCODING)

            # Update metadata
            self.current_file = path
            self.last_saved = datetime.now()

            return path

        except Exception as e:
            raise OSError(f"Failed to save mind map to {path}: {e}") from e

    def load(self, file_path: str) -> Any:
        """
        Load a mind map from a file.

        Args:
            file_path: Path to load the file from

        Returns:
            Root node of the loaded mind map

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is invalid
            OSError: If loading fails
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Mind map file not found: {path}")

        try:
            # Read JSON string
            json_string = path.read_text(encoding=self.DEFAULT_ENCODING)

            # Deserialize
            from cogist.infrastructure.io.json_serializer import JSONSerializer

            mind_map_data = JSONSerializer.deserialize(json_string)

            # Convert dictionary to node tree
            root_node = JSONSerializer.dict_to_node(mind_map_data["root"])

            # Update metadata
            self.current_file = path
            self.last_saved = None  # Will be set when saved

            return root_node

        except (FileNotFoundError, ValueError):
            raise
        except Exception as e:
            raise OSError(f"Failed to load mind map from {path}: {e}") from e

    def exists(self, file_path: str) -> bool:
        """
        Check if a mind map file exists.

        Args:
            file_path: Path to check

        Returns:
            True if file exists, False otherwise
        """
        return Path(file_path).exists()

    def get_current_file(self) -> Path | None:
        """
        Get the currently loaded/saved file path.

        Returns:
            Path to current file, or None if no file is loaded
        """
        return self.current_file

    def clear_current(self) -> None:
        """Clear the current file reference."""
        self.current_file = None
        self.last_saved = None
