"""
Edge Item - Presentation Layer

Connector edge between nodes with strategy pattern support.
"""

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainterPath, QPen
from PySide6.QtWidgets import QGraphicsPathItem

from cogist.domain.connectors import (
    BezierConnector,
    ConnectorStrategy,
    OrthogonalConnector,
    StraightConnector,
)


class EdgeItem(QGraphicsPathItem):
    """
    Connector edge between nodes with strategy pattern.

    Features:
    - Multiple connector types (bezier, straight, orthogonal)
    - Gradient line width for bezier curves
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

        # Connector strategy (default to bezier)
        self.connector_strategy: ConnectorStrategy = BezierConnector()

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

        if self._gradient_path:
            if self.line_style in (Qt.DashLine, Qt.DotLine, Qt.DashDotLine):
                # For dashed/dotted/dash-dot lines: draw as continuous path
                full_path = QPainterPath()
                for (start, end), _width in self._gradient_path:
                    if full_path.isEmpty():
                        full_path.moveTo(start)
                    full_path.lineTo(end)

                pen = QPen(self.color, self.end_width, self.line_style, Qt.RoundCap)
                # Adjust dash pattern for better visibility
                if self.line_style == Qt.DashLine:
                    pen.setDashPattern([6.0, 4.0])  # Dash length, gap
                elif self.line_style == Qt.DotLine:
                    pen.setDashPattern([1.0, 3.0])  # Dot size, gap
                elif self.line_style == Qt.DashDotLine:
                    pen.setDashPattern([6.0, 4.0, 1.0, 4.0])  # Dash, gap, dot, gap

                painter.setPen(pen)
                painter.drawPath(full_path)
            else:
                # For solid lines: use gradient width effect
                for (start, end), width in self._gradient_path:
                    pen = QPen(self.color, width, Qt.SolidLine, Qt.RoundCap)
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
        """Update connector path using strategy pattern.

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

        # Use strategy to generate path
        path = self.connector_strategy.generate_path(
            source_point, target_point, source_rect, target_rect
        )
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
                - connector_style: str (solid/dashed/dotted/dash_dot)
                - connector_shape: str (bezier/straight/orthogonal)
                - enable_gradient: bool (only for bezier, default True)
                - gradient_ratio: float (end_width/start_width ratio, 0.3-1.0)
        """
        # Update color
        if "connector_color" in style_config:
            self.color = QColor(style_config["connector_color"])

        # Update connector shape (strategy pattern)
        if "connector_shape" in style_config:
            shape_map = {
                "bezier": BezierConnector(),
                "straight": StraightConnector(),
                "orthogonal": OrthogonalConnector(),
            }
            new_strategy = shape_map.get(style_config["connector_shape"])
            if new_strategy and not isinstance(self.connector_strategy, type(new_strategy)):
                self.connector_strategy = new_strategy
                # Path changed, need to recalculate
                self.update_curve()

        # Update widths - support both uniform line_width and separate start/end widths
        base_width = None
        if "line_width" in style_config:
            base_width = float(style_config["line_width"])

        # Check connector shape type
        shape = style_config.get("connector_shape", "bezier")
        is_uniform_bezier = shape == "bezier_uniform"
        is_bezier = isinstance(self.connector_strategy, BezierConnector)

        if is_uniform_bezier:
            # For bezier_uniform: use uniform width (2px default or line_width)
            uniform_width = base_width if base_width is not None else 2.0
            self.start_width = uniform_width
            self.end_width = uniform_width
        elif is_bezier:
            # For regular bezier: use gradient width
            if "start_width" in style_config:
                self.start_width = float(style_config["start_width"])
            elif base_width is not None:
                self.start_width = base_width

            if "end_width" in style_config:
                self.end_width = float(style_config["end_width"])
            elif base_width is not None:
                # Apply gradient ratio if specified
                gradient_ratio = style_config.get("gradient_ratio", 0.5)
                self.end_width = base_width * max(0.3, min(1.0, gradient_ratio))
        else:
            # For non-bezier: use uniform width
            if base_width is not None:
                self.start_width = base_width
                self.end_width = base_width
            else:
                # Fallback to individual settings
                if "start_width" in style_config:
                    self.start_width = float(style_config["start_width"])
                if "end_width" in style_config:
                    self.end_width = float(style_config["end_width"])

        # Update line style
        style_map = {
            "solid": Qt.SolidLine,
            "dashed": Qt.DashLine,
            "dotted": Qt.DotLine,
            "dash_dot": Qt.DashDotLine,
        }
        if "connector_style" in style_config:
            self.line_style = style_map.get(style_config["connector_style"], Qt.SolidLine)

        # Invalidate cache and trigger repaint (if path didn't change)
        if "connector_shape" not in style_config:
            self._gradient_path = None
            self.update()
