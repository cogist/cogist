"""Rounded orthogonal connector strategy."""

from qtpy.QtCore import QPointF
from qtpy.QtGui import QPainterPath

from .base import ConnectorStrategy


class RoundedOrthogonalConnector(ConnectorStrategy):
    """Rounded orthogonal connector with smooth corner transitions.

    Creates L-shaped or Z-shaped paths with rounded corners instead of sharp 90-degree turns.
    Best for modern, clean diagrams that need the structure of orthogonal lines but with softer aesthetics.
    """

    CORNER_RADIUS = 15.0

    def generate_path(
        self,
        source_point: QPointF,
        target_point: QPointF,
        source_rect,
        target_rect,
    ) -> QPainterPath:
        """Generate rounded orthogonal path with smooth corners.

        Creates an L-shaped path with rounded corners: horizontal then vertical, or vice versa.

        Args:
            source_point: Starting point (edge of source node)
            target_point: Ending point (edge of target node)
            source_rect: Source node rectangle (not used for orthogonal)
            target_rect: Target node rectangle (not used for orthogonal)

        Returns:
            QPainterPath with rounded orthogonal segments
        """
        path = QPainterPath()

        dx = target_point.x() - source_point.x()
        dy = target_point.y() - source_point.y()

        # Midpoint for the corner
        mid_x = source_point.x() + dx * 0.5

        # Define the corner points
        corner1 = QPointF(mid_x, source_point.y())
        corner2 = QPointF(mid_x, target_point.y())

        # Calculate the actual corner radius (limit to avoid overlapping)
        max_radius_x = abs(dx) * 0.4
        max_radius_y = abs(dy) * 0.4
        radius = min(self.CORNER_RADIUS, max_radius_x, max_radius_y)

        if radius <= 0:
            # If radius is too small, fall back to sharp orthogonal
            path.moveTo(source_point)
            path.lineTo(corner1)
            path.lineTo(corner2)
            path.lineTo(target_point)
            return path

        # Build the list of key points
        points = [source_point, corner1, corner2, target_point]

        path.moveTo(points[0])

        # Iterate through intermediate corner points and round them
        for i in range(1, len(points) - 1):
            p1 = points[i - 1]  # Previous point
            p2 = points[i]      # Current corner point
            p3 = points[i + 1]  # Next point

            # Calculate direction vectors from corner to previous and next points
            v1 = p1 - p2  # p2 -> p1
            v2 = p3 - p2  # p2 -> p3

            len1 = (v1.x() ** 2 + v1.y() ** 2) ** 0.5
            len2 = (v2.x() ** 2 + v2.y() ** 2) ** 0.5
            if len1 == 0 or len2 == 0:
                continue
            v1 = QPointF(v1.x() / len1, v1.y() / len1)
            v2 = QPointF(v2.x() / len2, v2.y() / len2)

            # Calculate arc start and end points
            arc_start = p2 + v1 * radius
            arc_end = p2 + v2 * radius

            # Draw straight line to arc start
            path.lineTo(arc_start)

            # Use quadratic Bezier curve with corner as control point
            path.quadTo(p2, arc_end)

        # Draw final segment to end point
        path.lineTo(points[-1])

        return path
