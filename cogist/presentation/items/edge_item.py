"""
Edge Item - Presentation Layer

Connector edge between nodes with strategy pattern support.
"""

import colorsys
import contextlib

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import QGraphicsPathItem

from cogist.presentation.connectors import (
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

    def __init__(self, source_item, target_item, color: str = "#FF90CAF9", style_config=None):
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

    def paint(self, painter, option, widget=None):
        """Custom paint with gradient line width."""
        from PySide6.QtGui import QPainter

        painter.setRenderHint(QPainter.Antialiasing)

        # Read style from global config if available (real-time, no caching)
        if self.style_config and hasattr(self.source_item, 'depth'):
            from cogist.domain.styles.extended_styles import NodeRole

            source_depth = self.source_item.depth
            target_depth = self.target_item.depth

            # Get connector config from role-based style
            role_map = {
                0: NodeRole.ROOT,
                1: NodeRole.PRIMARY,
                2: NodeRole.SECONDARY,
            }
            # Use source depth for connector style (edge inherits source node's connector config)
            connector_role = role_map.get(source_depth, NodeRole.TERTIARY)
            # Use source depth for brightness/opacity adjustments (edge belongs to source node's layer)
            adjustment_role = connector_role

            # Default values
            color_str = "#FF666666"
            line_width = 2.0
            connector_style_str = "solid"
            connector_shape = "bezier"
            enable_gradient = True

            # NEW: Get connector style from MindMapStyle.role_styles (flat structure)
            if (hasattr(self.style_config, 'role_styles') and
                connector_role in self.style_config.role_styles):
                role_style = self.style_config.role_styles[connector_role]

                # Get connector color using index system
                branch_colors = self.style_config.branch_colors
                color_str = self._get_color_from_index(
                    role_style.connector_color_index,
                    branch_colors,
                    role_style.connector_brightness,
                    role_style.connector_opacity,
                    True  # connector is always enabled
                ) or "#FF666666"

                line_width = role_style.line_width
                connector_style_str = role_style.connector_style
                connector_shape = role_style.connector_shape
                enable_gradient = (connector_shape == "bezier")

            # Rainbow branch handling
            # Apply rainbow color to:
            # 1. Root -> Level 1 edges (target is Level 1)
            # 2. Level 1 -> Level 2+ edges (source is Level 1)
            # 3. Level 2+ -> Level 2+ edges (inherit from Level 1 ancestor)
            if self.style_config.use_rainbow_branches and len(self.style_config.branch_colors) >= 8:
                branch_idx = None

                # Case 1: Target is a Level 1 node (Root -> Level 1 edge)
                if (hasattr(self.target_item, 'domain_node') and self.target_item.domain_node and
                        self.target_item.domain_node.parent and target_depth == 1):
                    with contextlib.suppress(ValueError, AttributeError):
                        branch_idx = self.target_item.domain_node.parent.children.index(self.target_item.domain_node)

                # Case 2: Source is a Level 1 node (Level 1 -> Level 2+ edge)
                elif (hasattr(self.source_item, 'domain_node') and self.source_item.domain_node and
                      self.source_item.domain_node.parent and source_depth == 1):
                    with contextlib.suppress(ValueError, AttributeError):
                        branch_idx = self.source_item.domain_node.parent.children.index(self.source_item.domain_node)

                # Case 3: Level 2+ -> Level 2+ edges (inherit from Level 1 ancestor)
                elif target_depth >= 2 and hasattr(self.target_item, '_find_level_1_ancestor'):
                    level_1_ancestor = self.target_item._find_level_1_ancestor()
                    if level_1_ancestor and level_1_ancestor.parent:
                        with contextlib.suppress(ValueError, AttributeError):
                            branch_idx = level_1_ancestor.parent.children.index(level_1_ancestor)

                # Apply rainbow color if branch index found
                if branch_idx is not None and branch_idx < len(self.style_config.branch_colors):
                    # Get base rainbow color from branch_colors array
                    rainbow_base = self.style_config.branch_colors[branch_idx % 8]  # Only use indices 0-7

                    # Apply brightness and opacity adjustments for Level 2+
                    if hasattr(self.style_config, 'role_styles') and adjustment_role in self.style_config.role_styles:
                        role_style = self.style_config.role_styles[adjustment_role]

                        # Apply brightness adjustment
                        if role_style.connector_brightness != 1.0:
                            rainbow_base = self._adjust_color_brightness(rainbow_base, role_style.connector_brightness)

                        # Apply opacity adjustment
                        if role_style.connector_opacity < 255:
                            rainbow_base = self._apply_opacity(rainbow_base, role_style.connector_opacity)

                    color_str = rainbow_base

            # Extract style values directly from config
            color = QColor(color_str)

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
                # Regular bezier with gradient: use default ratio
                start_width = line_width
                end_width = line_width * 0.5  # Default 50% gradient
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

            if line_style == Qt.SolidLine:
                # For solid lines: use optimized drawing
                if is_uniform:
                    # Uniform width: draw path directly for best performance
                    # Use RoundCap to match decorative line rendering
                    pen = QPen(color, start_width, Qt.SolidLine, Qt.RoundCap)
                    pen.setJoinStyle(Qt.MiterJoin)
                    painter.setPen(pen)
                    painter.drawPath(self.path())
                else:
                    # Gradient width: draw segment by segment
                    for (start, end), width in self._gradient_path:  # type: ignore[union-attr]
                        pen = QPen(color, width, Qt.SolidLine, Qt.RoundCap)
                        painter.setPen(pen)
                        painter.drawLine(start, end)
            else:
                # For dashed/dotted/dash-dot lines: use manual dash implementation
                # This ensures consistent dash patterns across all connector shapes
                self._draw_dashed_line(painter, color, line_style)

    def _adjust_color_brightness(self, color_hex: str, brightness_factor: float) -> str:
        """Adjust color brightness using HLS color space.

        Args:
            color_hex: Color in hex format (#AARRGGBB or #RRGGBB)
            brightness_factor: Brightness multiplier (0.0-2.0, 1.0 = no change)

        Returns:
            Adjusted color in #AARRGGBB format
        """
        color_hex = color_hex.lstrip("#")

        # Extract alpha and RGB components
        if len(color_hex) == 8:
            alpha = int(color_hex[0:2], 16)
            r = int(color_hex[2:4], 16) / 255.0
            g = int(color_hex[4:6], 16) / 255.0
            b = int(color_hex[6:8], 16) / 255.0
        elif len(color_hex) == 6:
            alpha = 255
            r = int(color_hex[0:2], 16) / 255.0
            g = int(color_hex[2:4], 16) / 255.0
            b = int(color_hex[4:6], 16) / 255.0
        else:
            return color_hex

        # Convert to HLS
        h, lightness, s = colorsys.rgb_to_hls(r, g, b)

        # Apply brightness adjustment
        new_lightness = lightness * brightness_factor
        new_lightness = max(0.0, min(1.0, new_lightness))  # Clamp to [0, 1]

        # Convert back to RGB
        new_r, new_g, new_b = colorsys.hls_to_rgb(h, new_lightness, s)

        # Convert to hex
        r_int = int(new_r * 255)
        g_int = int(new_g * 255)
        b_int = int(new_b * 255)

        return f"#{alpha:02X}{r_int:02X}{g_int:02X}{b_int:02X}"

    def _apply_opacity(self, color_hex: str, opacity: int) -> str:
        """Apply opacity to a color by modifying the alpha channel.

        Args:
            color_hex: Color in hex format (#AARRGGBB or #RRGGBB)
            opacity: Opacity value (0-255), 255 = fully opaque

        Returns:
            Color with modified alpha channel in #AARRGGBB format
        """
        color_hex = color_hex.lstrip("#")

        # Extract RGB components
        if len(color_hex) == 8:
            rgb_hex = color_hex[2:]
        elif len(color_hex) == 6:
            rgb_hex = color_hex
        else:
            return color_hex

        # Apply new opacity
        return f"#{opacity:02X}{rgb_hex}"

    def _get_color_from_index(self, color_index: int, branch_colors: list,
                              brightness: float, opacity: int, enabled: bool) -> str | None:
        """Get color from branch_colors index with adjustments.

        Args:
            color_index: Index into branch_colors array
            branch_colors: List of colors
            brightness: Brightness factor (0.5-1.5)
            opacity: Opacity value (0-255)
            enabled: Whether the element is enabled

        Returns:
            Color string in #AARRGGBB format, or None if disabled
        """
        if not enabled:
            return None

        if not branch_colors or color_index >= len(branch_colors):
            return None

        base_color = branch_colors[color_index]

        # Apply brightness adjustment
        if brightness != 1.0:
            base_color = self._adjust_color_brightness(base_color, brightness)

        # Apply opacity adjustment
        if opacity < 255:
            base_color = self._apply_opacity(base_color, opacity)

        return base_color

    def _draw_dashed_line(self, painter, color, line_style):
        """Draw dashed/dotted/dash-dot lines with precise pattern control.

        This method uses a manual dash algorithm that works for all connector shapes
        (bezier, straight, orthogonal) and supports gradient widths.

        Args:
            painter: QPainter instance
            color: Line color
            line_style: Qt.PenStyle (DashLine, DotLine, or DashDotLine)
        """
        assert self._gradient_path is not None

        # Define dash patterns as list of (segment_length, is_visible)
        # Match the patterns used for uniform width lines
        dash_patterns = {
            Qt.DashLine: [(6.0, True), (4.0, False)],  # Dash-Gap
            Qt.DotLine: [(1.0, True), (3.0, False)],   # Dot-Gap
            Qt.DashDotLine: [(6.0, True), (4.0, False), (1.0, True), (4.0, False)],  # Dash-Gap-Dot-Gap
        }
        pattern = dash_patterns.get(line_style, [(6.0, True), (4.0, False)])

        # Manual dash implementation with gradient width support
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

                # Calculate end point for this sub-segment using linear interpolation
                t = draw_length / seg_length
                sub_end = QPointF(
                    segment_start.x() + (end.x() - segment_start.x()) * t,
                    segment_start.y() + (end.y() - segment_start.y()) * t
                )

                if is_visible:
                    # Draw this sub-segment with its specific width (gradient preserved!)
                    pen = QPen(color, width, Qt.SolidLine, Qt.RoundCap)
                    painter.setPen(pen)
                    painter.drawLine(segment_start, sub_end)

                # Update positions
                segment_remaining -= draw_length
                pattern_position += draw_length
                segment_start = sub_end

                # Check if we need to move to next pattern segment
                if pattern_position >= seg_len - 0.001:
                    pattern_position = 0.0
                    pattern_index = (pattern_index + 1) % len(pattern)
                    seg_len, is_visible = pattern[pattern_index]
                    remaining_in_pattern = seg_len

    def _create_gradient_path(self, start_width=None, end_width=None):
        """Create cached gradient path.

        Args:
            start_width: Width at start point (read from config if None)
            end_width: Width at end point (read from config if None)
        """
        # If widths not provided, read from global config
        if start_width is None or end_width is None:
            if self.style_config and hasattr(self.source_item, 'depth'):
                from cogist.domain.styles.extended_styles import NodeRole

                source_depth = self.source_item.depth
                role_map = {0: NodeRole.ROOT, 1: NodeRole.PRIMARY, 2: NodeRole.SECONDARY}
                role = role_map.get(source_depth, NodeRole.TERTIARY)

                # Default values
                line_width = 2.0
                connector_shape = "bezier"
                enable_gradient = True

                if (self.style_config.resolved_template and
                    role in self.style_config.resolved_template.role_styles):
                    role_style = self.style_config.resolved_template.role_styles[role]
                    line_width = role_style.line_width
                    connector_shape = role_style.connector_shape
                    enable_gradient = (connector_shape == "bezier")

                is_uniform_bezier = connector_shape == "bezier_uniform"
                is_bezier = isinstance(self.connector_strategy, BezierConnector)

                if start_width is None:
                    start_width = line_width

                if end_width is None:
                    if is_uniform_bezier:
                        end_width = line_width
                    elif is_bezier and enable_gradient:
                        # Fixed gradient ratio for bezier connectors
                        end_width = line_width * 0.5
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

        # Get border shape types and widths for source and target nodes
        source_shape = self._get_node_border_shape(self.source_item)
        target_shape = self._get_node_border_shape(self.target_item)
        source_border_width = self._get_node_border_width(self.source_item)
        target_border_width = self._get_node_border_width(self.target_item)

        # Get connector width from style config if available
        connector_width = 2.0  # Default value
        if self.style_config and hasattr(self.source_item, 'depth'):
            from cogist.domain.styles.extended_styles import NodeRole

            source_depth = self.source_item.depth
            role_map = {0: NodeRole.ROOT, 1: NodeRole.PRIMARY, 2: NodeRole.SECONDARY}
            role = role_map.get(source_depth, NodeRole.TERTIARY)

            if (self.style_config.resolved_template and
                role in self.style_config.resolved_template.role_styles):
                role_style = self.style_config.resolved_template.role_styles[role]
                connector_width = role_style.line_width

        # For mind map: always use left/right edge based on horizontal direction
        # Parent (source) should connect from right edge (if child is on right)
        # or left edge (if child is on left)
        if dx >= 0:
            # Child is on right: connect from source's right edge
            # Adjust connection point based on border shape
            source_local_right = self._get_edge_point_for_shape(
                source_rect, "right", source_shape, source_border_width, connector_width
            )
            source_point = self.source_item.mapToScene(source_local_right)

            # Connect to target's left edge
            target_local_left = self._get_edge_point_for_shape(
                target_rect, "left", target_shape, target_border_width, connector_width
            )
            target_point = self.target_item.mapToScene(target_local_left)
        else:
            # Child is on left: connect from source's left edge
            source_local_left = self._get_edge_point_for_shape(
                source_rect, "left", source_shape, source_border_width, connector_width
            )
            source_point = self.source_item.mapToScene(source_local_left)

            # Connect to target's right edge
            target_local_right = self._get_edge_point_for_shape(
                target_rect, "right", target_shape, target_border_width, connector_width
            )
            target_point = self.target_item.mapToScene(target_local_right)

        # Use strategy to generate path
        path = self.connector_strategy.generate_path(
            source_point, target_point, source_rect, target_rect
        )
        self.setPath(path)

        self._gradient_path = None

        # CRITICAL: Force full repaint to clear old drawing
        self.update()

    def _get_node_border_shape(self, node_item) -> str:
        """Get the border shape type of a node.

        Args:
            node_item: NodeItem instance

        Returns:
            Border shape type string (e.g., 'rounded_rect', 'bottom_line')
        """
        try:
            return node_item.template_style.shape.basic_shape
        except AttributeError:
            # Fallback to default if template_style is not available
            return "rounded_rect"

    def _get_node_border_width(self, node_item) -> float:
        """Get the border width of a node.

        Args:
            node_item: NodeItem instance

        Returns:
            Border width in pixels
        """
        try:
            return node_item.template_style.border.border_width
        except AttributeError:
            return 2.0  # Default border width

    def _get_edge_point_for_shape(
        self, rect, edge: str, shape_type: str, border_width: float = 2.0, connector_width: float = 2.0
    ) -> QPointF:
        """Get connection point on node edge based on border shape.

        Args:
            rect: Node rectangle in local coordinates
            edge: Which edge to connect from ('left' or 'right')
            shape_type: Border shape type (e.g., 'bottom_line', 'left_line')
            border_width: Border width (unused: node height is now forced to even numbers)
            connector_width: Connector line width (unused: node height is now forced to even numbers)

        Returns:
            QPointF in local coordinates for the connection point
        """
        # Decorative line shapes: connect to the decorative line position
        if shape_type == "bottom_line":
            # CRITICAL: Use exact rect.bottom() to match decorative line drawing coordinate.
            # Node height is now forced to be even (see node_item.py), so rect.bottom()
            # is always an integer, ensuring crisp anti-aliased rendering for both lines.
            y = rect.bottom()

            if edge == "left":
                return QPointF(rect.left(), y)
            else:
                return QPointF(rect.right(), y)
        elif shape_type == "left_line":
            # Left line is drawn exactly at rect.left()
            if edge == "left":
                return QPointF(rect.left(), rect.center().y())
            else:  # edge == 'right', shouldn't happen for left_line but handle gracefully
                return QPointF(rect.right(), rect.center().y())
        else:
            # Default: connect to edge center (for rounded_rect, circle, etc.)
            if edge == "left":
                return QPointF(rect.left(), rect.center().y())
            else:  # edge == 'right'
                return QPointF(rect.right(), rect.center().y())

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
            from cogist.presentation.connectors import SharpFirstRoundedConnector

            shape_map = {
                "bezier": BezierConnector(),
                "straight": StraightConnector(),
                "orthogonal": OrthogonalConnector(),
                "rounded_orthogonal": RoundedOrthogonalConnector(),
                "sharp_first_rounded": SharpFirstRoundedConnector(),
            }
            new_strategy = shape_map.get(style_config["connector_shape"])
            if new_strategy and not isinstance(self.connector_strategy, type(new_strategy)):
                self.connector_strategy = new_strategy
                # Path changed, need to recalculate
                self.update_curve()
