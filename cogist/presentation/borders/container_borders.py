"""Container shape border strategies (shapes with background fill)."""

from qtpy.QtCore import QPointF, Qt
from qtpy.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen

from .base import BorderStrategy


def _draw_dashed_path(painter: QPainter, path: QPainterPath, color: QColor, width: float, border_style: str) -> None:
    """Draw dashed/dotted/dash-dot path using manual dash algorithm (matching edge_item.py).

    Args:
        painter: QPainter instance
        path: QPainterPath to draw
        color: Line color
        width: Line width
        border_style: "dashed", "dotted", or "dash_dot"
    """
    # Map border_style to Qt enum
    style_map = {
        "dashed": Qt.DashLine,
        "dotted": Qt.DotLine,
        "dash_dot": Qt.DashDotLine,
    }
    line_style = style_map.get(border_style, Qt.DashLine)

    # Define base dash patterns (in pixels) - same as edge_item.py
    # When width > 1, RoundCap extends each segment by width/2 on each end
    # So we need to add width to the gap to maintain the visual spacing
    base_patterns = {
        Qt.DashLine: [(6.0, True), (4.0, False)],  # Dash-Gap
        Qt.DotLine: [(1.0, True), (3.0, False)],   # Dot-Gap
        Qt.DashDotLine: [(6.0, True), (4.0, False), (1.0, True), (4.0, False)],  # Dash-Gap-Dot-Gap
    }

    # Adjust gap based on line width to compensate for RoundCap extension
    # RoundCap adds width/2 to each end, so total extension per segment = width
    cap_extension = width if width > 1 else 0

    pattern = []
    for length, is_visible in base_patterns[line_style]:
        if is_visible:
            pattern.append((length, True))
        else:
            # Increase gap to compensate for RoundCap
            pattern.append((length + cap_extension, False))

    # Convert QPainterPath to list of line segments
    # Sample points along the path based on actual length (same as edge_item.py)
    segments = []
    path_length = path.length()
    if path_length < 0.001:
        return

    # Ensure segments are small enough for smooth rendering
    # Max segment length should be ≤ 1.0 pixel
    max_segment_length = 1.0
    num_segments = max(20, int(path_length / max_segment_length))
    num_segments = min(num_segments, 200)

    # Sample points evenly along the path by length, not by percent
    # This ensures uniform segment lengths even on curves
    prev_point = path.pointAtPercent(0)
    for i in range(1, num_segments + 1):
        # Use length-based sampling for uniform distribution
        target_length = (i / num_segments) * path_length
        t = path.percentAtLength(target_length)
        point = path.pointAtPercent(t)
        segments.append((prev_point, point))
        prev_point = point

    # Manual dash implementation (same algorithm as edge_item.py)
    pattern_position = 0.0
    pattern_index = 0

    for start, end in segments:
        # Calculate segment length
        seg_length = ((end.x() - start.x())**2 + (end.y() - start.y())**2) ** 0.5
        if seg_length < 0.001:
            continue

        # Get current pattern segment
        seg_len, is_visible = pattern[pattern_index]
        remaining_in_pattern = seg_len - pattern_position

        # Process this path segment
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
                # Draw this sub-segment
                # Use RoundCap for smooth rounded ends
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


class RoundedRectBorder(BorderStrategy):
    """Rounded rectangle with background and border."""

    def draw(self, painter: QPainter, rect, style_config: dict) -> None:
        """Draw rounded rectangle border.

        Args:
            painter: QPainter instance
            rect: Node bounding rectangle
            style_config: Style configuration dictionary
        """
        bg_color = style_config.get("bg_color")
        radius = style_config.get("border_radius", 8)
        border_color = style_config.get("border_color")
        border_width = style_config.get("border_width", 0)
        border_style = style_config.get("border_style", "solid")

        if border_width > 0 and border_color:
            # Use compound QPainterPath to create a ring/border-only shape
            # This prevents semi-transparent overlap between border and background

            # CRITICAL: Border extends FULL border_width outward from rect
            # Outer path (extends full border width outward)
            outer_rect = rect.adjusted(-border_width, -border_width, border_width, border_width)
            outer_radius = radius + border_width
            outer_path = QPainterPath()
            outer_path.addRoundedRect(outer_rect, outer_radius, outer_radius)

            # Inner path (original rect, creates the "hole")
            inner_path = QPainterPath()
            inner_path.addRoundedRect(rect, radius, radius)

            # Subtract inner from outer to create a ring shape
            border_ring = outer_path.subtracted(inner_path)

            # Step 1: Draw background first (full rectangle)
            if bg_color:
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(bg_color)))
                painter.drawPath(inner_path)

            # Step 2: Draw border using QPainterPathStroker for dashed/dotted support
            if border_style == "solid":
                # Solid line: use simple pen
                pen = QPen(QColor(border_color), border_width, Qt.SolidLine, Qt.RoundCap)
                painter.setPen(pen)
                painter.setBrush(Qt.NoBrush)
                painter.drawPath(inner_path)
            else:
                # Dashed/dotted/dash-dot: use QPainterPathStroker for proper dash rendering
                # This avoids the segmentation issues with manual drawing
                from qtpy.QtGui import QPainterPathStroker

                stroker = QPainterPathStroker()
                stroker.setWidth(border_width)
                stroker.setCapStyle(Qt.RoundCap)
                stroker.setJoinStyle(Qt.RoundJoin)

                # Set dash pattern (in units of pen width, as per Qt docs)
                if border_style == "dashed":
                    stroker.setDashPattern([4.0, 2.0])  # Dash(4x width) - Gap(2x width)
                elif border_style == "dotted":
                    stroker.setDashPattern([0.5, 2.0])  # Dot(0.5x width) - Gap(2x width)
                elif border_style == "dash_dot":
                    stroker.setDashPattern([4.0, 2.0, 0.5, 2.0])  # Dash-Gap-Dot-Gap

                # Create stroke path and fill it
                border_stroke_path = stroker.createStroke(inner_path)

                # Subtract inner path to avoid overlap with background
                border_ring = border_stroke_path.subtracted(inner_path)

                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(border_color)))
                painter.drawPath(border_ring)
        else:
            # No border, just draw background
            if bg_color:
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(bg_color)))
                painter.drawRoundedRect(rect, radius, radius)

    def get_selection_path(self, rect, style_config: dict) -> QPainterPath:
        """Get selection highlight path for rounded rectangle."""
        radius = style_config.get("border_radius", 8)
        highlight_rect = rect.adjusted(-3, -3, 3, 3)
        path = QPainterPath()
        path.addRoundedRect(highlight_rect, radius + 2, radius + 2)
        return path


class CircleBorder(BorderStrategy):
    """Circle/ellipse with background and border."""

    def draw(self, painter: QPainter, rect, style_config: dict) -> None:
        """Draw circle/ellipse border.

        Args:
            painter: QPainter instance
            rect: Node bounding rectangle
            style_config: Style configuration dictionary
        """
        bg_color = style_config.get("bg_color")
        border_color = style_config.get("border_color")
        border_width = style_config.get("border_width", 0)
        border_style = style_config.get("border_style", "solid")

        if border_width > 0 and border_color:
            # Use compound QPainterPath to create a ring/border-only shape
            # This prevents semi-transparent overlap between border and background

            # CRITICAL: Border extends FULL border_width outward from rect
            # Outer path (extends full border width outward)
            outer_rect = rect.adjusted(-border_width, -border_width, border_width, border_width)
            outer_path = QPainterPath()
            outer_path.addEllipse(outer_rect)

            # Inner path (original rect, creates the "hole")
            inner_path = QPainterPath()
            inner_path.addEllipse(rect)

            # Subtract inner from outer to create a ring shape
            border_ring = outer_path.subtracted(inner_path)

            # Step 1: Draw background first (full ellipse)
            if bg_color:
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(bg_color)))
                painter.drawPath(inner_path)

            # Step 2: Draw border using QPainterPathStroker for dashed/dotted support
            if border_style == "solid":
                # Solid line: use simple pen
                pen = QPen(QColor(border_color), border_width, Qt.SolidLine, Qt.RoundCap)
                painter.setPen(pen)
                painter.setBrush(Qt.NoBrush)
                painter.drawPath(inner_path)
            else:
                # Dashed/dotted/dash-dot: use QPainterPathStroker for proper dash rendering
                # This avoids the segmentation issues with manual drawing
                from qtpy.QtGui import QPainterPathStroker

                stroker = QPainterPathStroker()
                stroker.setWidth(border_width)
                stroker.setCapStyle(Qt.RoundCap)
                stroker.setJoinStyle(Qt.RoundJoin)

                # Set dash pattern (in units of pen width, as per Qt docs)
                if border_style == "dashed":
                    stroker.setDashPattern([4.0, 2.0])  # Dash(4x width) - Gap(2x width)
                elif border_style == "dotted":
                    stroker.setDashPattern([0.5, 2.0])  # Dot(0.5x width) - Gap(2x width)
                elif border_style == "dash_dot":
                    stroker.setDashPattern([4.0, 2.0, 0.5, 2.0])  # Dash-Gap-Dot-Gap

                # Create stroke path and fill it
                border_stroke_path = stroker.createStroke(inner_path)

                # Subtract inner path to avoid overlap with background
                border_ring = border_stroke_path.subtracted(inner_path)

                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(border_color)))
                painter.drawPath(border_ring)
        else:
            # No border, just draw background
            if bg_color:
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(bg_color)))
                painter.drawEllipse(rect)

    def get_selection_path(self, rect, style_config: dict) -> QPainterPath:
        """Get selection highlight path for circle/ellipse."""
        highlight_rect = rect.adjusted(-3, -3, 3, 3)
        path = QPainterPath()
        path.addEllipse(highlight_rect)
        return path
