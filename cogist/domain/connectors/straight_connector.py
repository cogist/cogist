"""Straight line connector strategy."""

from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainterPath

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
        source_rect,  # noqa: ARG002 - kept for interface consistency
        target_rect,  # noqa: ARG002 - kept for interface consistency
    ) -> QPainterPath:
        """Generate straight line path.

        Args:
            source_point: Starting point (edge of source node)
            target_point: Ending point (edge of target node)
            source_rect: Source node rectangle (not used for straight line)
            target_rect: Target node rectangle (not used for straight line)

        Returns:
            QPainterPath with straight line
        """
        path = QPainterPath(source_point)
        path.lineTo(target_point)
        return path
