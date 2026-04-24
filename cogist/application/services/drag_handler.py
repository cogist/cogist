"""Drag Handler - Application Layer

Coordinates drag operations between Presentation and Domain layers.
"""

from typing import Protocol

from cogist.domain.entities import Node
from cogist.domain.value_objects.position import Position


class INodeProvider(Protocol):
    """Interface for providing node information to DragHandler.
    
    Implemented by Presentation Layer to abstract UI dependencies.
    """
    
    def get_node_position(self, node_id: str) -> tuple[float, float]:
        """Get the position of a node."""
        ...
    
    def get_node_bounds(self, node_id: str) -> tuple[float, float, float, float]:
        """Get the bounding box of a node (x, y, width, height)."""
        ...
    
    def get_all_node_ids(self) -> list[str]:
        """Get all node IDs in the scene."""
        ...


class DragHandler:
    """Handles drag detection logic.
    
    Coordinates between UI events and domain logic to detect
    potential parent nodes during drag operations.
    """
    
    def __init__(self, root_node: Node, node_provider: INodeProvider):
        """Initialize DragHandler.
        
        Args:
            root_node: The root node of the mind map tree
            node_provider: Interface to access node information
        """
        self.root_node = root_node
        self.node_provider = node_provider
    
    def detect_potential_parent(
        self, 
        dragged_node_id: str, 
        mouse_pos: Position
    ) -> Node | None:
        """Detect the best potential parent based on anchor point distance.
        
        Uses current position to determine which side the node is on.
        Distance is calculated from dragged node center to candidate's anchor point.
        
        Args:
            dragged_node_id: ID of the node being dragged
            mouse_pos: Current mouse position
            
        Returns:
            The best candidate parent node, or None if no valid candidate
        """
        # TODO: Implement the actual detection logic
        # For now, return None to make tests compile
        return None
