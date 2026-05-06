"""Bezier S-curve connector strategy."""

from qtpy.QtCore import QPointF
from qtpy.QtGui import QPainterPath

from .base import ConnectorStrategy


class BezierConnector(ConnectorStrategy):
    """S-curve bezier connector (default mind map style).

    Creates a smooth S-shaped curve with horizontal control points.
    The curve direction adapts based on whether the target is left or right of source.
    """

    def generate_path(
        self,
        source_point: QPointF,
        target_point: QPointF,
        source_rect,
        target_rect,
    ) -> QPainterPath:
        """Generate bezier S-curve path.

        Args:
            source_point: Starting point (edge of source node)
            target_point: Ending point (edge of target node)
            source_rect: Source node rectangle (not used for bezier)
            target_rect: Target node rectangle (not used for bezier)

        Returns:
            QPainterPath with cubic bezier curve
        """
        path = QPainterPath(source_point)

        # Calculate control offset based on horizontal distance
        dx = target_point.x() - source_point.x()
        control_offset = abs(dx) * 0.5

        # Control points: horizontal S-curve
        if dx >= 0:
            # Target on right: control1 goes right from source, control2 goes left from target
            control1 = QPointF(source_point.x() + control_offset, source_point.y())
            control2 = QPointF(target_point.x() - control_offset, target_point.y())
        else:
            # Target on left: control1 goes left from source, control2 goes right from target
            control1 = QPointF(source_point.x() - control_offset, source_point.y())
            control2 = QPointF(target_point.x() + control_offset, target_point.y())

        path.cubicTo(control1, control2, target_point)
        return path
