"""
Edge Item - Presentation Layer

Connector edge between nodes with strategy pattern support.
"""

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import QGraphicsPathItem

from cogist.domain.connectors import (
    BezierConnector,
    ConnectorStrategy,
    OrthogonalConnector,
    RoundedOrthogonalConnector,
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

    def __init__(self, source_item, target_item, color: str = "#90CAF9", style_config=None):
        super().__init__()
        self.source_item = source_item
        self.target_item = target_item
        self.color = QColor(color)
        self.style_config = style_config  # Store global style config reference

        # Edge style configuration (will be read from style_config in paint)
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

        # Read style from global config if available (real-time, no caching)
        if self.style_config and hasattr(self.source_item, 'depth'):
            source_depth = self.source_item.depth

            # Get connector config for this depth
            if source_depth in self.style_config.connector_config_by_depth:
                connector_config = self.style_config.connector_config_by_depth[source_depth]
            else:
                # Use the deepest configured level for deeper nodes
                max_depth = max(self.style_config.connector_config_by_depth.keys())
                connector_config = self.style_config.connector_config_by_depth[max_depth]

            # Extract style values directly from config
            color = QColor(connector_config["color"])
            line_width = connector_config["line_width"]
            connector_style_str = connector_config["connector_style"]
            connector_shape = connector_config.get("connector_shape", "bezier")

            # Determine enable_gradient based on connector_shape (no need to store it)
            enable_gradient = (connector_shape == "bezier")

            # Map connector style string to Qt enum
            style_map = {
                "solid": Qt.SolidLine,
                "dashed": Qt.DashLine,
                "dotted": Qt.DotLine,
                "dash_dot": Qt.DashDotLine,
            }
            line_style = style_map.get(connector_style_str, Qt.SolidLine)

            # Determine start/end widths based on shape type and enable_gradient
            is_uniform_bezier = connector_shape == "bezier_uniform"
            is_bezier = isinstance(self.connector_strategy, BezierConnector)

            if is_uniform_bezier:
                # Uniform bezier: always use uniform width
                start_width = line_width
                end_width = line_width
            elif is_bezier and enable_gradient:
                # Regular bezier with gradient: apply gradient ratio
                start_width = line_width
                gradient_ratio = connector_config.get("gradient_ratio", 0.5)
                end_width = line_width * max(0.3, min(1.0, gradient_ratio))
            else:
                # Non-bezier or bezier without gradient: use uniform width
                start_width = line_width
                end_width = line_width
        else:
            # Fallback to instance variables (for backward compatibility)
            color = self.color
            start_width = self.start_width
            end_width = self.end_width
            line_style = self.line_style

        # Invalidate gradient path cache and recreate with current widths
        self._gradient_path = None
        self._create_gradient_path(start_width, end_width)

        if self._gradient_path:
            # Check if uniform width (no gradient needed)
            is_uniform = abs(start_width - end_width) < 0.01

            if is_uniform:
                # For uniform width: draw the path directly for sharp corners
                # self.path() is already in item coordinates (set by update_curve)
                pen = QPen(color, start_width, line_style, Qt.FlatCap)
                pen.setJoinStyle(Qt.MiterJoin)

                # Adjust dash pattern for better visibility
                if line_style == Qt.DashLine:
                    pen.setDashPattern([6.0, 4.0])
                elif line_style == Qt.DotLine:
                    pen.setDashPattern([1.0, 3.0])
                elif line_style == Qt.DashDotLine:
                    pen.setDashPattern([6.0, 4.0, 1.0, 4.0])

                painter.setPen(pen)
                painter.drawPath(self.path())
            elif line_style in (Qt.DashLine, Qt.DotLine, Qt.DashDotLine):
                # For dashed/dotted/dash-dot lines with gradient: manual dash implementation
                assert self._gradient_path is not None  # Guaranteed by _create_gradient_path above

                # Define dash patterns as list of (segment_length, is_visible)
                # Each pattern repeats along the path
                # Match the patterns used for uniform width lines (lines 129-134)
                dash_patterns = {
                    Qt.DashLine: [(6.0, True), (4.0, False)],  # Dash-Gap
                    Qt.DotLine: [(1.0, True), (3.0, False)],   # Dot-Gap
                    Qt.DashDotLine: [(6.0, True), (4.0, False), (1.0, True), (4.0, False)],  # Dash-Gap-Dot-Gap
                }
                pattern = dash_patterns.get(line_style, [(6.0, True), (4.0, False)])

                # Calculate total path length for proper dash distribution
                total_length = sum(
                    ((end.x() - start.x())**2 + (end.y() - start.y())**2) ** 0.5
                    for (start, end), _ in self._gradient_path  # type: ignore[union-attr]
                )

                # Manual dash implementation with gradient width
                path_position = 0.0  # Current position along total path
                pattern_position = 0.0  # Current position within current pattern segment
                pattern_index = 0  # Current pattern segment index

                for (start, end), width in self._gradient_path:  # type: ignore[union-attr]
                    # Calculate segment length
                    seg_length = ((end.x() - start.x())**2 + (end.y() - start.y())**2) ** 0.5
                    if seg_length < 0.001:
                        continue

                    # Get current pattern segment
                    seg_len, is_visible = pattern[pattern_index]
                    remaining_in_pattern = seg_len - pattern_position

                    # Process this path segment, potentially splitting across pattern boundaries
                    segment_remaining = seg_length
                    segment_start = start

                    while segment_remaining > 0.001:
                        # How much to draw/skip in this iteration
                        draw_length = min(segment_remaining, remaining_in_pattern)

                        # Calculate end point for this sub-segment
                        t = draw_length / seg_length
                        sub_end = QPointF(
                            segment_start.x() + (end.x() - segment_start.x()) * t,
                            segment_start.y() + (end.y() - segment_start.y()) * t
                        )

                        if is_visible:
                            # Draw this sub-segment with its specific width
                            pen = QPen(color, width, Qt.SolidLine, Qt.RoundCap)
                            painter.setPen(pen)
                            painter.drawLine(segment_start, sub_end)

                        # Update positions
                        segment_remaining -= draw_length
                        pattern_position += draw_length
                        path_position += draw_length
                        segment_start = sub_end

                        # Check if we need to move to next pattern segment
                        if pattern_position >= seg_len - 0.001:
                            pattern_position = 0.0
                            pattern_index = (pattern_index + 1) % len(pattern)
                            seg_len, is_visible = pattern[pattern_index]
                            remaining_in_pattern = seg_len
            else:
                # For solid lines: use gradient width effect
                for (start, end), width in self._gradient_path:
                    pen = QPen(color, width, Qt.SolidLine, Qt.RoundCap)
                    painter.setPen(pen)
                    painter.drawLine(start, end)

    def _create_gradient_path(self, start_width=None, end_width=None):
        """Create cached gradient path.

        Args:
            start_width: Width at start point (read from config if None)
            end_width: Width at end point (read from config if None)
        """
        # If widths not provided, read from global config
        if start_width is None or end_width is None:
            if self.style_config and hasattr(self.source_item, 'depth'):
                source_depth = self.source_item.depth

                if source_depth in self.style_config.connector_config_by_depth:
                    connector_config = self.style_config.connector_config_by_depth[source_depth]
                else:
                    max_depth = max(self.style_config.connector_config_by_depth.keys())
                    connector_config = self.style_config.connector_config_by_depth[max_depth]

                line_width = connector_config["line_width"]
                connector_shape = connector_config.get("connector_shape", "bezier")

                # Determine enable_gradient based on connector_shape (no need to store it)
                enable_gradient = (connector_shape == "bezier")

                is_uniform_bezier = connector_shape == "bezier_uniform"
                is_bezier = isinstance(self.connector_strategy, BezierConnector)

                if start_width is None:
                    start_width = line_width

                if end_width is None:
                    if is_uniform_bezier:
                        end_width = line_width
                    elif is_bezier and enable_gradient:
                        gradient_ratio = connector_config.get("gradient_ratio", 0.5)
                        end_width = line_width * max(0.3, min(1.0, gradient_ratio))
                    else:
                        end_width = line_width
            else:
                # Fallback to instance variables
                if start_width is None:
                    start_width = self.start_width
                if end_width is None:
                    end_width = self.end_width

        path = self.path()
        if path.isEmpty():
            self._gradient_path = []
            return

        # Calculate total path length to determine appropriate segment count
        total_length = path.length()

        # Ensure segments are small enough for dash patterns
        # Max segment length should be smaller than smallest dash pattern unit (1.0 for dots)
        max_segment_length = 1.0  # Small enough for smooth gradient and accurate dashes
        segments = max(20, int(total_length / max_segment_length))  # At least 20 segments
        segments = min(segments, 200)  # Cap at 200 to avoid performance issues

        points = []
        for i in range(segments + 1):
            t = i / segments
            pt = path.pointAtPercent(t)
            points.append(pt)

        self._gradient_path = []
        for i in range(len(points) - 1):
            # Use segment index for linear gradient
            t = i / (len(points) - 1)
            width = start_width - t * (start_width - end_width)
            self._gradient_path.append(((points[i], points[i + 1]), width))

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

        Note: Most style values are now read directly from global config in paint().
        This method only updates the connector strategy when shape changes.

        Args:
            style_config: Dictionary containing edge style parameters
                - connector_shape: str (bezier/straight/orthogonal)
        """
        # Update connector shape (strategy pattern) - this is the only thing that needs updating
        if "connector_shape" in style_config:
            shape_map = {
                "bezier": BezierConnector(),
                "straight": StraightConnector(),
                "orthogonal": OrthogonalConnector(),
                "rounded_orthogonal": RoundedOrthogonalConnector(),
            }
            new_strategy = shape_map.get(style_config["connector_shape"])
            if new_strategy and not isinstance(self.connector_strategy, type(new_strategy)):
                self.connector_strategy = new_strategy
                # Path changed, need to recalculate
                self.update_curve()
