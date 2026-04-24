"""Qt Node Provider - Presentation Layer adapter for DragHandler.

Adapts Qt's NodeItem to the INodeProvider interface used by Application Layer.
"""

from typing import TYPE_CHECKING

from cogist.application.services.drag_handler import INodeProvider

if TYPE_CHECKING:
    from cogist.presentation.items.node_item import NodeItem


class QtNodeProvider(INodeProvider):
    """Adapter that provides node information from Qt NodeItems.

    This class bridges the Presentation Layer (Qt) and Application Layer
    by implementing the INodeProvider interface.
    """

    def __init__(self, node_items: dict[str, "NodeItem"]):
        """Initialize the adapter.

        Args:
            node_items: Dictionary mapping node IDs to NodeItem instances
        """
        self.node_items = node_items

    def get_node_position(self, node_id: str) -> tuple[float, float]:
        """Get the position of a node.

        Args:
            node_id: The ID of the node

        Returns:
            Tuple of (x, y) coordinates
        """
        item = self.node_items.get(node_id)
        if not item:
            return (0.0, 0.0)

        pos = item.scenePos()
        return (pos.x(), pos.y())

    def get_node_bounds(self, node_id: str) -> tuple[float, float, float, float]:
        """Get the bounding box of a node.

        Args:
            node_id: The ID of the node

        Returns:
            Tuple of (x, y, width, height) where x,y are local coordinates (usually 0,0)
        """
        item = self.node_items.get(node_id)
        if not item:
            return (0.0, 0.0, 0.0, 0.0)

        rect = item.boundingRect()
        return (rect.x(), rect.y(), rect.width(), rect.height())

    def get_all_node_ids(self) -> list[str]:
        """Get all node IDs in the scene.

        Returns:
            List of all node IDs
        """
        return list(self.node_items.keys())
