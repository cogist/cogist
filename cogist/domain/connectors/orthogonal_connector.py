"""Orthogonal (right-angle) connector strategy."""

from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainterPath

from .base import ConnectorStrategy


class OrthogonalConnector(ConnectorStrategy):
    """Right-angle orthogonal connector.

    Creates L-shaped or Z-shaped paths with 90-degree turns.
    Best for flowcharts and technical diagrams.
    """

    def generate_path(
        self,
        source_point: QPointF,
        target_point: QPointF,
        source_rect,
        target_rect,
    ) -> QPainterPath:
        """Generate orthogonal path with right-angle turns.

        Creates an L-shaped path: horizontal then vertical, or vice versa.

        Args:
            source_point: Starting point (edge of source node)
            target_point: Ending point (edge of target node)
            source_rect: Source node rectangle (not used for orthogonal)
            target_rect: Target node rectangle (not used for orthogonal)

        Returns:
            QPainterPath with orthogonal segments
        """
        path = QPainterPath(source_point)

        dx = target_point.x() - source_point.x()

        # Create L-shaped path: go horizontal first, then vertical
        # Midpoint for the corner
        mid_x = source_point.x() + dx * 0.5

        path.lineTo(mid_x, source_point.y())  # Horizontal segment
        path.lineTo(mid_x, target_point.y())  # Vertical segment
        path.lineTo(target_point.x(), target_point.y())  # Final horizontal segment

        return path
