"""
MindMap Service - Application Layer

Provides high-level API for mind map operations.
Coordinates between NodeService and Repository.
"""

from pathlib import Path

from cogist.application.commands.command_history import CommandHistory
from cogist.application.services.node_service import NodeService
from cogist.domain.entities.node import Node
from cogist.domain.layout import DefaultLayout, LayoutConfig, DEFAULT_LAYOUT_CONFIG
from cogist.domain.repositories import MindMapRepositoryInterface
from cogist.infrastructure.repositories.mindmap_repository import MindMapRepository


class MindMapService:
    """
    Service for mind map operations.

    Provides high-level methods for creating, editing, saving,
    and loading mind maps.
    """

    def __init__(
        self,
        repository: MindMapRepositoryInterface | None = None,
        layout_config: LayoutConfig | None = None,
    ):
        """Initialize the mind map service.
        
        Args:
            repository: Repository implementation (uses MindMapRepository if not provided)
            layout_config: Optional layout configuration (uses default if not provided)
        """
        self.command_history = CommandHistory()
        self.node_service = NodeService(self.command_history)
        # Dependency injection: accept interface, provide default implementation
        self.repository = repository or MindMapRepository()
        self.layout_engine = DefaultLayout(layout_config or DEFAULT_LAYOUT_CONFIG)

        self.root_node: Node | None = None
        self.current_file: Path | None = None
        self._is_modified: bool = False  # Track if mind map has unsaved changes
        self._command_count_at_save: int = 0  # Track command count at last save

    def create_new_mindmap(self, root_text: str = "Central Topic") -> Node:
        """
        Create a new mind map with a root node.

        Args:
            root_text: Text for the root node

        Returns:
            The root node of the new mind map
        """
        import uuid

        self.root_node = Node(
            id=str(uuid.uuid4()), text=root_text, is_root=True, position=(0.0, 0.0)
        )

        self.current_file = None
        self._is_modified = False  # New file is not modified
        return self.root_node

    def load_mindmap(self, file_path: str) -> Node:
        """
        Load a mind map from file.

        Args:
            file_path: Path to the .mwe file

        Returns:
            The root node of the loaded mind map
        """
        self.root_node = self.repository.load(file_path)
        self.current_file = self.repository.get_current_file()
        self._is_modified = False  # Loaded file is not modified
        assert self.root_node is not None
        return self.root_node

    def save_mindmap(self, file_path: str | None = None) -> Path:
        """
        Save the current mind map to file.

        Args:
            file_path: Optional path to save to. If None, uses current file.

        Returns:
            Path to the saved file

        Raises:
            ValueError: If no mind map is loaded
            IOError: If saving fails
        """
        if self.root_node is None:
            raise ValueError("No mind map loaded")

        # Use current file if no path specified
        if file_path is None:
            if self.current_file is None:
                raise ValueError("No file path specified and no current file")
            file_path = str(self.current_file)

        saved_path = self.repository.save(self.root_node, file_path)
        self.current_file = saved_path
        self._is_modified = False  # Saved file is not modified
        self._command_count_at_save = (
            self.command_history.get_command_count()
        )  # Record save point
        return saved_path

    def add_child_node(
        self,
        parent_node: Node,
        text: str = "New Node",
    ) -> Node | None:
        """
        Add a child node to the specified parent.

        Args:
            parent_node: Parent node to add child to
            text: Text content for the new node

        Returns:
            The newly created node
        """
        result = self.node_service.add_child_node(parent_node, text)
        if result:  # Only mark as modified if node was actually added
            self.mark_modified()
        return result

    def delete_node(self, node: Node) -> None:
        """
        Delete a node and all its children.

        Args:
            node: Node to delete
        """
        self.node_service.delete_node(node)
        self.mark_modified()

    def edit_node_text(self, node: Node, new_text: str) -> None:
        """
        Edit the text content of a node.

        Args:
            node: Node to edit
            new_text: New text content
        """
        self.node_service.edit_node_text(node, new_text)
        self.mark_modified()

    def undo(self) -> bool:
        """
        Undo the last operation.

        Returns:
            True if undo was successful, False if nothing to undo
        """
        result = self.node_service.undo()
        if (
            result
            and self.command_history.get_command_count() < self._command_count_at_save
        ):
            self._is_modified = False
        return result

    def redo(self) -> bool:
        """
        Redo the last undone operation.

        Returns:
            True if redo was successful, False if nothing to redo
        """
        result = self.node_service.redo()
        if (
            result
            and self.command_history.get_command_count() > self._command_count_at_save
        ):
            self._is_modified = True
        return result

    def can_undo(self) -> bool:
        """Check if there's an operation to undo."""
        return self.node_service.can_undo()

    def can_redo(self) -> bool:
        """Check if there's an operation to redo."""
        return self.node_service.can_redo()

    def relayout(
        self, canvas_width: float = 1200.0, canvas_height: float = 800.0, context: dict | None = None
    ) -> None:
        """
        Recalculate the layout of the mind map.

        Args:
            canvas_width: Width of the canvas
            canvas_height: Height of the canvas
            context: Optional context information (e.g., focused_node_id)
        """
        if self.root_node is None:
            return

        self.layout_engine.layout(self.root_node, canvas_width, canvas_height, context)
    
    def set_layout_config(self, config: LayoutConfig) -> None:
        """Update the layout configuration and relayout.
        
        Args:
            config: New layout configuration
        """
        self.layout_engine = DefaultLayout(config)

    def get_root_node(self) -> Node | None:
        """Get the root node of the current mind map."""
        return self.root_node

    def get_current_file(self) -> Path | None:
        """Get the current file path."""
        return self.current_file

    def mark_modified(self) -> None:
        """Mark the mind map as modified (has unsaved changes)."""
        self._is_modified = True

    def is_modified(self) -> bool:
        """Check if the mind map has unsaved changes."""
        return self._is_modified
