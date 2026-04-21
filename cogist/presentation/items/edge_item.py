"""
Edge Item - Presentation Layer

Bezier curve connection between nodes.
"""

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsPathItem


class EdgeItem(QGraphicsPathItem):
    """
    Bezier curve edge connecting two nodes.

    Features:
    - Gradient line width (thick at source, thin at target)
    - Smooth S-curve
    - Auto-update on node move
    """

    def __init__(self, source_item, target_item, color: str = "#90CAF9"):
        super().__init__()
        self.source_item = source_item
        self.target_item = target_item
        self.color = QColor(color)

        # Edge style configuration
        self.start_width = 6.0
        self.end_width = 2.0
        self.line_style = Qt.SolidLine

        # Z-value: edges below nodes (set to -1 to ensure they're below)
        self.setZValue(-1)

        # Cache for gradient path
        self._gradient_path = None

        # Custom drawing
        self.update_curve()

    def paint(self, painter, option, widget=None):  # noqa: ARG002
        """Custom paint with gradient line width."""
        from PySide6.QtGui import QPainter

        painter.setRenderHint(QPainter.Antialiasing)

        if self._gradient_path is None:
            self._create_gradient_path()

        # DEBUG: Print current style
        print(f"DEBUG EdgeItem.paint: color={self.color.name()}, line_style={self.line_style}, start_width={self.start_width}, end_width={self.end_width}")

        if self._gradient_path:
            for (start, end), width in self._gradient_path:
                pen = QPen(self.color, width, self.line_style, Qt.RoundCap)
                painter.setPen(pen)
                painter.drawLine(start, end)

    def _create_gradient_path(self):
        """Create cached gradient path."""
        path = self.path()
        if path.isEmpty():
            self._gradient_path = []
            return

        segments = 20  # Same as original demo
        points = []

        for i in range(segments + 1):
            t = i / segments
            pt = path.pointAtPercent(t)
            points.append(pt)

        self._gradient_path = []
        for i in range(len(points) - 1):
            # Use segment index for linear gradient
            t = i / (len(points) - 1)
            line_width = self.start_width - t * (self.start_width - self.end_width)
            self._gradient_path.append(((points[i], points[i + 1]), line_width))

    def update_curve(self):
        """Update bezier curve to connect nodes.

        CRITICAL: Use mapToScene() to convert node rect edges to scene coordinates.
        This ensures edge endpoints match the actual visual boundaries of nodes,
        regardless of whether they use centered or directional expansion.
        """
        # CRITICAL: Use mapToScene() to get actual edge positions in scene coordinates
        # This handles both centered and directional expansion correctly
        source_rect = self.source_item.rect()
        target_rect = self.target_item.rect()

        dx = self.target_item.scenePos().x() - self.source_item.scenePos().x()

        # For mind map: always use left/right edge based on horizontal direction
        # Parent (source) should connect from right edge (if child is on right)
        # or left edge (if child is on left)
        if dx >= 0:
            # Child is on right: connect from source's right edge
            # Map the right edge of source rect to scene coordinates
            source_local_right = QPointF(source_rect.right(), source_rect.center().y())
            source_point = self.source_item.mapToScene(source_local_right)

            # Connect to target's left edge
            # Map the left edge of target rect to scene coordinates
            target_local_left = QPointF(target_rect.left(), target_rect.center().y())
            target_point = self.target_item.mapToScene(target_local_left)
        else:
            # Child is on left: connect from source's left edge
            # Map the left edge of source rect to scene coordinates
            source_local_left = QPointF(source_rect.left(), source_rect.center().y())
            source_point = self.source_item.mapToScene(source_local_left)

            # Connect to target's right edge
            # Map the right edge of target rect to scene coordinates
            target_local_right = QPointF(target_rect.right(), target_rect.center().y())
            target_point = self.target_item.mapToScene(target_local_right)

        path = QPainterPath(source_point)
        control_offset = abs(target_point.x() - source_point.x()) * 0.5

        # Control points: horizontal S-curve
        # Direction depends on whether child is on left or right
        if dx >= 0:
            # Child on right: control1 goes right from source, control2 goes left from target
            control1 = QPointF(source_point.x() + control_offset, source_point.y())
            control2 = QPointF(target_point.x() - control_offset, target_point.y())
        else:
            # Child on left: control1 goes left from source, control2 goes right from target
            control1 = QPointF(source_point.x() - control_offset, source_point.y())
            control2 = QPointF(target_point.x() + control_offset, target_point.y())

        path.cubicTo(control1, control2, target_point)
        self.setPath(path)

        self._gradient_path = None

        # CRITICAL: Force full repaint to clear old drawing
        self.update()

    def _find_edge_point(
        self, center: QPointF, direction_x: float, direction_y: float, item
    ) -> QPointF:
        """Find best edge point on node boundary based on direction."""
        import math

        half_w = item.node_width / 2
        half_h = item.node_height / 2

        length = (direction_x**2 + direction_y**2) ** 0.5
        if length == 0:
            return center

        angle = math.atan2(-direction_y, direction_x)
        deg = math.degrees(angle)

        if deg < 0:
            deg += 360

        if deg < 45 or deg >= 315:
            return QPointF(center.x() + half_w, center.y())
        elif 45 <= deg < 135:
            return QPointF(center.x(), center.y() - half_h)
        elif 135 <= deg < 225:
            return QPointF(center.x() - half_w, center.y())
        else:
            return QPointF(center.x(), center.y() + half_h)

    def update_style(self, style_config: dict):
        """Update edge style from configuration.

        Args:
            style_config: Dictionary containing edge style parameters
                - connector_color: str (hex color)
                - line_width: float (uniform width for both ends)
                - start_width: float (width at source node, optional)
                - end_width: float (width at target node, optional)
                - connector_style: str (solid/dashed/dotted)
                - connector_type: str (bezier/straight/orthogonal) - not yet implemented
        """
        print(f"DEBUG EdgeItem.update_style called with: {style_config}")
        
        # Update color
        if "connector_color" in style_config:
            self.color = QColor(style_config["connector_color"])
            print(f"DEBUG: Set color to {self.color.name()}")

        # Update widths - support both uniform line_width and separate start/end widths
        if "line_width" in style_config:
            # Uniform width for both ends
            width = float(style_config["line_width"])
            self.start_width = width
            self.end_width = width
            print(f"DEBUG: Set start_width={self.start_width}, end_width={self.end_width}")
        else:
            # Separate widths for gradient effect
            if "start_width" in style_config:
                self.start_width = float(style_config["start_width"])
            if "end_width" in style_config:
                self.end_width = float(style_config["end_width"])

        # Update line style
        style_map = {
            "solid": Qt.SolidLine,
            "dashed": Qt.DashLine,
            "dotted": Qt.DotLine,
        }
        if "connector_style" in style_config:
            self.line_style = style_map.get(style_config["connector_style"], Qt.SolidLine)
            print(f"DEBUG: Set line_style to {self.line_style}")

        # Note: connector_type (bezier/straight/orthogonal) requires path recalculation
        # This would need to be handled by updating the curve generation logic
        # For now, we only support styling changes, not path type changes

        # Invalidate cache and trigger repaint
        self._gradient_path = None
        self.update()
        print(f"DEBUG: Called update(), current state: color={self.color.name()}, line_style={self.line_style}, start_width={self.start_width}, end_width={self.end_width}")
