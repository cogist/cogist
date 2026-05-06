"""Node Entity - Domain Layer

Core business entity representing a mind map node.
Pure Python class, no UI dependencies.
"""

from dataclasses import dataclass, field
from typing import Any, Optional

from cogist.domain.styles import PriorityLevel


@dataclass
class Node:
    """
    Node entity in the domain model.

    Note: Node order is preserved by the order of children list.
    No separate sort_weight field is needed.

    Attributes:
        id: Unique identifier (UUID)
        text: Node content text
        width: Node width in pixels (auto-calculated based on text)
        height: Node height in pixels (auto-calculated based on text)
        position: (x, y) position tuple
        parent: Parent node reference
        children: List of child nodes (order determines visual order)
        color: Node color
        is_root: Whether this is the root node
        depth: Depth in the tree (0 for root)
    """

    id: str
    text: str
    # width: float = 140.0  # Must be calculated based on text content
    # height: float = 50.0  # Must be calculated based on text content
    width: float = 0.0  # Temporary: must be set after measurement
    height: float = 0.0  # Temporary: must be set after measurement
    position: tuple = (0.0, 0.0)
    parent: Optional["Node"] = None
    children: list["Node"] = field(default_factory=list)
    color: str = "#2196F3"
    is_root: bool = False
    depth: int = 0
    priority_level: PriorityLevel = PriorityLevel.LEVEL_1  # Default: Normal
    custom_style: dict | None = None  # Reserved for future node-level override
    is_locked_position: bool = False  # Lock for rebalancing (prevents moving to other side)
    rainbow_branch_index: int | None = None  # Fixed color index for rainbow mode (0-7)

    # Runtime attributes (not part of equality)
    _ui_item: Any = field(default=None, repr=False, init=False)

    def add_child(self, child: "Node") -> None:
        """Add a child node to this node."""
        child.parent = self
        child.depth = self.depth + 1
        self.children.append(child)

    def remove_child(self, child: "Node") -> None:
        """Remove a child node from this node."""
        if child in self.children:
            child.parent = None
            self.children.remove(child)

    def get_depth(self) -> int:
        """Get the depth of this node in the tree."""
        if self.parent is None:
            return 0
        return 1 + self.parent.get_depth()

    def get_all_descendants(self) -> list["Node"]:
        """Get all descendant nodes (children, grandchildren, etc.)."""
        descendants = []
        for child in self.children:
            descendants.append(child)
            descendants.extend(child.get_all_descendants())
        return descendants

    def set_ui_item(self, item: Any) -> None:
        """Set the UI representation item."""
        self._ui_item = item

    def get_ui_item(self) -> Any | None:
        """Get the UI representation item."""
        return self._ui_item
