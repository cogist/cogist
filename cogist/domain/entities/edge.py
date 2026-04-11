"""
Edge Entity - Domain Layer

Core business entity representing a connection between nodes.
Pure Python class, no UI dependencies.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Edge:
    """
    Edge entity in the domain model.

    Represents a connection between two nodes in a mind map.

    Attributes:
        id: Unique identifier (UUID)
        source_node_id: ID of the source node (parent)
        target_node_id: ID of the target node (child)
        color: Edge color in HEX format
        line_width: Line width in pixels
        _ui_item: Runtime reference to UI representation
    """

    id: str
    source_node_id: str
    target_node_id: str
    color: str = "#90CAF9"
    line_width: float = 2.0

    # Runtime attributes (not part of equality)
    _ui_item: Any = field(default=None, repr=False, init=False)

    def set_ui_item(self, item: Any) -> None:
        """Set the UI representation item."""
        self._ui_item = item

    def get_ui_item(self) -> Any | None:
        """Get the UI representation item."""
        return self._ui_item
