"""
MindMap Service - Application Layer

Provides high-level API for mind map operations.
Coordinates between NodeService and Repository.
"""

from pathlib import Path

from cogist.application.commands.command_history import CommandHistory
from cogist.application.services.node_service import NodeService
from cogist.domain.entities.node import Node
from cogist.domain.layout import (
    DEFAULT_LAYOUT_CONFIG,
    DefaultLayoutConfig,
    layout_registry,
)
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
        layout_config: DefaultLayoutConfig | None = None,
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

        # Layout management with registry
        self.layout_registry = layout_registry
        self.current_layout_name = "default"
        self.layout_config = layout_config or DEFAULT_LAYOUT_CONFIG
        self.layout_engine = self._create_layout_engine()

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
            file_path: Path to the .cgs file

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

        # Get style config from mindmap view if available
        style_config = None
        if hasattr(self, '_mindmap_view') and self._mindmap_view:
            style_config = getattr(self._mindmap_view, 'style_config', None)

        saved_path = self.repository.save(self.root_node, file_path, style_config)
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
        self,
        canvas_width: float = 1200.0,
        canvas_height: float = 800.0,
        context: dict | None = None,
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

    def _create_layout_engine(self):
        """Create layout engine instance using registry

        Returns:
            Layout algorithm instance
        """
        return self.layout_registry.get_layout(
            self.current_layout_name,
            self.layout_config
        )

    def set_layout_algorithm(self, algorithm_name: str) -> None:
        """Switch to a different layout algorithm

        Args:
            algorithm_name: Name of the layout algorithm (e.g., "default", "tree")

        Raises:
            ValueError: If layout algorithm is not registered
        """
        if not self.layout_registry.has_layout(algorithm_name):
            available = ", ".join(self.layout_registry.get_available_layouts())
            raise ValueError(
                f"Unknown layout algorithm: '{algorithm_name}'. "
                f"Available layouts: {available}"
            )

        self.current_layout_name = algorithm_name
        self.layout_engine = self._create_layout_engine()
        # Note: Caller should trigger relayout if needed

    def set_layout_config(self, config: DefaultLayoutConfig) -> None:
        """Update the layout configuration and recreate layout engine.

        Args:
            config: New layout configuration
        """
        self.layout_config = config
        self.layout_engine = self._create_layout_engine()

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

    def add_child_node_by_id(
        self,
        parent_id: str,
        text: str = "New Node",
    ) -> tuple[Node | None, Node | None]:
        """
        Add a child node to the specified parent by ID.

        Args:
            parent_id: ID of the parent node
            text: Text content for the new node

        Returns:
            Tuple of (parent_node, new_node) or (None, None) if failed
        """
        if self.root_node is None:
            return None, None

        # Find parent node
        parent_node = self._find_node_by_id(self.root_node, parent_id)
        if parent_node is None:
            return None, None

        # Use NodeService to add child
        new_node = self.node_service.add_child_node(parent_node, text)
        if new_node:
            self.mark_modified()
            return parent_node, new_node

        return None, None

    def add_sibling_node(
        self,
        node_id: str,
        text: str = "New Node",
    ) -> tuple[Node | None, Node | None]:
        """
        Add a sibling node to the specified node.

        Args:
            node_id: ID of the reference node
            text: Text content for the new node

        Returns:
            Tuple of (parent_node, new_node) or (None, None) if failed
        """
        if self.root_node is None or self.root_node.id == node_id:
            return None, None  # Can't add sibling to root

        # Find parent and current node
        parent_node, current_node = self._find_parent_and_node(
            self.root_node, node_id
        )

        if parent_node is None or current_node is None:
            return None, None

        # Use NodeService to add child (sibling is just another child of same parent)
        new_node = self.node_service.add_child_node(parent_node, text)
        if new_node:
            self.mark_modified()
            return parent_node, new_node

        return None, None

    def delete_node_by_id(self, node_id: str) -> bool:
        """
        Delete a node by ID.

        Args:
            node_id: ID of the node to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        if self.root_node is None or self.root_node.id == node_id:
            return False  # Can't delete root

        # Find parent and node to delete
        parent_node, node_to_delete = self._find_parent_and_node(
            self.root_node, node_id
        )

        if node_to_delete is None:
            return False

        # Use NodeService to delete
        self.node_service.delete_node(node_to_delete)
        self.mark_modified()
        return True

    def edit_node_text_by_id(self, node_id: str, new_text: str) -> bool:
        """
        Edit node text by ID.

        Args:
            node_id: ID of the node to edit
            new_text: New text content

        Returns:
            True if edited successfully, False otherwise
        """
        if self.root_node is None:
            return False

        # Find the node
        node = self._find_node_by_id(self.root_node, node_id)
        if node is None:
            return False

        # Use NodeService to edit
        self.node_service.edit_node_text(node, new_text)
        self.mark_modified()
        return True

    def _find_node_by_id(self, root: Node, node_id: str) -> Node | None:
        """
        Find a node by ID using breadth-first search.

        Args:
            root: Root node to start search from
            node_id: ID to search for

        Returns:
            Node if found, None otherwise
        """
        if root.id == node_id:
            return root

        queue = list(root.children)
        while queue:
            node = queue.pop(0)
            if node.id == node_id:
                return node
            queue.extend(node.children)

        return None

    def _find_parent_and_node(
        self, root: Node, node_id: str
    ) -> tuple[Node | None, Node | None]:
        """
        Find both parent and node by node ID.

        Args:
            root: Root node to start search from
            node_id: ID of the node to find

        Returns:
            Tuple of (parent_node, target_node) or (None, None) if not found
        """
        if root.id == node_id:
            return None, root  # Root has no parent

        # BFS to find node and track parent
        queue = [(root, None)]  # (node, parent)
        while queue:
            current_node, parent = queue.pop(0)
            for child in current_node.children:
                if child.id == node_id:
                    return current_node, child
                queue.append((child, current_node))

        return None, None
