"""Straight line connector strategy."""

from qtpy.QtCore import QPointF
from qtpy.QtGui import QPainterPath

from .base import ConnectorStrategy


class StraightConnector(ConnectorStrategy):
    """Direct straight line connector.

    Creates a simple straight line between source and target points.
    Best for hierarchical or organizational charts.
    """

    def generate_path(
        self,
        source_point: QPointF,
        target_point: QPointF,
        source_rect,
        target_rect,
    ) -> QPainterPath:
        """Generate straight line path with horizontal segments at both ends.

        The path consists of:
        - First 1/4: Horizontal line from source
        - Middle 2/4: Diagonal line connecting the segments
        - Last 1/4: Horizontal line to target

        Args:
            source_point: Starting point (edge of source node)
            target_point: Ending point (edge of target node)
            source_rect: Source node rectangle (not used for straight line)
            target_rect: Target node rectangle (not used for straight line)

        Returns:
            QPainterPath with segmented line
        """
        path = QPainterPath(source_point)

        # Calculate segment points
        dx = target_point.x() - source_point.x()

        # Each horizontal segment is 1/4 of total horizontal distance
        horizontal_segment = dx / 4.0

        # First point: 1/4 horizontal from source
        point1 = QPointF(source_point.x() + horizontal_segment, source_point.y())

        # Second point: 3/4 horizontal, 1/4 vertical (start of last horizontal segment)
        point2 = QPointF(source_point.x() + 3 * horizontal_segment, target_point.y())

        # Draw the path: horizontal -> diagonal -> horizontal
        path.lineTo(point1)  # First 1/4 horizontal
        path.lineTo(point2)  # Middle 2/4 diagonal
        path.lineTo(target_point)  # Last 1/4 horizontal

        return path
