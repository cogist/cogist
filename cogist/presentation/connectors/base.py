"""Abstract base class for connector strategies."""

from abc import ABC, abstractmethod

from qtpy.QtCore import QPointF
from qtpy.QtGui import QPainterPath


class ConnectorStrategy(ABC):
    """Abstract base class for connector path generation strategies.

    All connector types must implement this interface to generate
    paths between source and target nodes.
    """

    @abstractmethod
    def generate_path(
        self,
        source_point: QPointF,
        target_point: QPointF,
        source_rect,
        target_rect,
    ) -> QPainterPath:
        """Generate connection path between two points.

        Args:
            source_point: Starting point in scene coordinates
            target_point: Ending point in scene coordinates
            source_rect: Source node's rectangle (for edge calculation)
            target_rect: Target node's rectangle (for edge calculation)

        Returns:
            QPainterPath representing the connector shape
        """
        pass
