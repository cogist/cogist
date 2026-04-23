"""Sharp-first rounded orthogonal connector strategy."""

from PySide6.QtCore import QPointF
from PySide6.QtGui import QPainterPath

from .base import ConnectorStrategy


class SharpFirstRoundedConnector(ConnectorStrategy):
    """Sharp-first rounded orthogonal connector.

    Creates a path with:
    - First corner (near source): Sharp 90-degree angle
    - Second corner (near target): Rounded corner

    This provides a clean, structured look near the parent node while
    maintaining smooth aesthetics near the child node.
    """

    CORNER_RADIUS = 15.0

    def generate_path(
        self,
        source_point: QPointF,
        target_point: QPointF,
        source_rect,  # noqa: ARG002 - kept for interface consistency
        target_rect,  # noqa: ARG002 - kept for interface consistency
    ) -> QPainterPath:
        """Generate path with sharp first corner and rounded second corner.

        Creates a Z-shaped path:
        - Horizontal from source
        - Sharp 90° turn at first corner
        - Vertical segment
        - Rounded turn at second corner
        - Horizontal to target

        Args:
            source_point: Starting point (edge of source node)
            target_point: Ending point (edge of target node)
            source_rect: Source node rectangle (not used)
            target_rect: Target node rectangle (not used)

        Returns:
            QPainterPath with sharp-first rounded orthogonal segments
        """
        path = QPainterPath()

        dx = target_point.x() - source_point.x()
        dy = target_point.y() - source_point.y()

        # Midpoint for the corner
        mid_x = source_point.x() + dx * 0.5

        # Define the corner points
        corner1 = QPointF(mid_x, source_point.y())  # First corner (sharp)
        corner2 = QPointF(mid_x, target_point.y())  # Second corner (rounded)

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

        # Start path from source
        path.moveTo(points[0])

        # First corner (corner1): Keep it SHARP - draw directly to it
        path.lineTo(corner1)

        # Second corner (corner2): Round it
        p1 = points[1]  # Previous point (corner1)
        p2 = points[2]  # Current corner point (corner2) - to round
        p3 = points[3]  # Next point (target)

        # Calculate direction vectors from corner to previous and next points
        v1 = p1 - p2  # p2 -> p1
        v2 = p3 - p2  # p2 -> p3

        len1 = (v1.x() ** 2 + v1.y() ** 2) ** 0.5
        len2 = (v2.x() ** 2 + v2.y() ** 2) ** 0.5

        if len1 > 0 and len2 > 0:
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
