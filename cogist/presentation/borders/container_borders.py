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

            # Step 2: Draw border by filling the ring shape (not stroking)
            # This completely avoids semi-transparent overlap issues
            if border_style == "solid":
                # Solid border: fill the ring path directly
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(border_color)))
                painter.drawPath(border_ring)
            else:
                # Dashed/dotted/dash-dot: Use QPainterPathStroker for proper dash rendering
                # CRITICAL: Stroke inner_path (not outer_path) to avoid gap with background
                # Then subtract inner_path to prevent overlap (same principle as solid)
                from qtpy.QtGui import QPainterPathStroker

                stroker = QPainterPathStroker()
                stroker.setWidth(border_width)
                stroker.setCapStyle(Qt.RoundCap)
                stroker.setJoinStyle(Qt.RoundJoin)

                # Create dashed stroke path
                # CRITICAL: Create a path that extends border_width/2 outward
                # When stroker adds border_width/2 on both sides, inner edge = inner_path position
                half_expanded_rect = rect.adjusted(-border_width/2, -border_width/2, border_width/2, border_width/2)
                half_expanded_radius = radius + border_width/2
                stroke_base_path = QPainterPath()
                stroke_base_path.addRoundedRect(half_expanded_rect, half_expanded_radius, half_expanded_radius)

                # Dash patterns - Calculate perimeter and adjust for uniform distribution
                # This prevents dash segments from clustering at corners
                path_length = stroke_base_path.length()

                # Base pattern in pixels
                if border_style == "dashed":
                    base_pattern = [6.0, 4.0 + 1.0 * border_width]  # dash, gap (with RoundCap compensation)
                elif border_style == "dotted":
                    base_pattern = [1.0, 3.0 + 1.0 * border_width]  # dot, gap
                else:  # dash_dot
                    base_pattern = [6.0, 4.0 + 1.0 * border_width, 1.0, 4.0 + 1.0 * border_width]  # dash, gap, dot, gap

                # Calculate pattern length and adjust to fit path evenly
                pattern_length = sum(base_pattern)
                num_patterns = path_length / pattern_length
                num_rounded = max(1, round(num_patterns))

                # Adjust gap to make pattern fit evenly (keep dash/dot length fixed)
                # This ensures uniform distribution around the entire path
                if len(base_pattern) == 2:  # dashed or dotted
                    dash_len = base_pattern[0] / border_width
                    # Adjust gap so that n * (dash + gap) = path_length
                    adjusted_gap = (path_length / num_rounded - base_pattern[0]) / border_width
                    stroker.setDashPattern([dash_len, adjusted_gap])
                else:  # dash_dot (len == 4)
                    dash_len = base_pattern[0] / border_width
                    dot_len = base_pattern[2] / border_width
                    # Adjust both gaps proportionally
                    total_fixed = base_pattern[0] + base_pattern[2]
                    total_gap_needed = path_length / num_rounded - total_fixed
                    gap_ratio = base_pattern[1] / (base_pattern[1] + base_pattern[3])
                    adjusted_gap1 = (total_gap_needed * gap_ratio) / border_width
                    adjusted_gap2 = (total_gap_needed * (1.0 - gap_ratio)) / border_width
                    stroker.setDashPattern([dash_len, adjusted_gap1, dot_len, adjusted_gap2])

                # CRITICAL: Calculate dash offset to center pattern and avoid clustering at corners
                # Offset by half pattern length to distribute evenly around the path
                # For closed paths, this prevents dash segments from overlapping at start/end point
                dash_offset = (path_length / num_rounded) / 2.0
                stroker.setDashOffset(dash_offset / border_width)  # Convert to width multiples

                dashed_stroke_path = stroker.createStroke(stroke_base_path)

                # Subtract inner_path to get only the outer portion (no overlap with background)
                dashed_border_ring = dashed_stroke_path.subtracted(inner_path)

                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(border_color)))
                painter.drawPath(dashed_border_ring)
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

            # Step 2: Draw border by filling the ring shape (not stroking)
            # This completely avoids semi-transparent overlap issues
            if border_style == "solid":
                # Solid border: fill the ring path directly
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(border_color)))
                painter.drawPath(border_ring)
            else:
                # Dashed/dotted/dash-dot: Use QPainterPathStroker for proper dash rendering
                # CRITICAL: Stroke inner_path (not outer_path) to avoid gap with background
                # Then subtract inner_path to prevent overlap (same principle as solid)
                from qtpy.QtGui import QPainterPathStroker

                stroker = QPainterPathStroker()
                stroker.setWidth(border_width)
                stroker.setCapStyle(Qt.RoundCap)
                stroker.setJoinStyle(Qt.RoundJoin)

                # Create dashed stroke path for ellipse
                # CRITICAL: Create a path that extends border_width/2 outward
                # When stroker adds border_width/2 on both sides, inner edge = inner_path position
                half_expanded_rect = rect.adjusted(-border_width/2, -border_width/2, border_width/2, border_width/2)
                stroke_base_path = QPainterPath()
                stroke_base_path.addEllipse(half_expanded_rect)

                # Dash patterns - Calculate perimeter and adjust for uniform distribution
                # This prevents dash segments from clustering at corners
                path_length = stroke_base_path.length()

                # Base pattern in pixels
                if border_style == "dashed":
                    base_pattern = [6.0, 4.0 + 1.0 * border_width]  # dash, gap (with RoundCap compensation)
                elif border_style == "dotted":
                    base_pattern = [1.0, 3.0 + 1.0 * border_width]  # dot, gap
                else:  # dash_dot
                    base_pattern = [6.0, 4.0 + 1.0 * border_width, 1.0, 4.0 + 1.0 * border_width]  # dash, gap, dot, gap

                # Calculate pattern length and adjust to fit path evenly
                pattern_length = sum(base_pattern)
                num_patterns = path_length / pattern_length
                num_rounded = max(1, round(num_patterns))

                # Adjust gap to make pattern fit evenly (keep dash/dot length fixed)
                # This ensures uniform distribution around the entire path
                if len(base_pattern) == 2:  # dashed or dotted
                    dash_len = base_pattern[0] / border_width
                    # Adjust gap so that n * (dash + gap) = path_length
                    adjusted_gap = (path_length / num_rounded - base_pattern[0]) / border_width
                    stroker.setDashPattern([dash_len, adjusted_gap])
                else:  # dash_dot (len == 4)
                    dash_len = base_pattern[0] / border_width
                    dot_len = base_pattern[2] / border_width
                    # Adjust both gaps proportionally
                    total_fixed = base_pattern[0] + base_pattern[2]
                    total_gap_needed = path_length / num_rounded - total_fixed
                    gap_ratio = base_pattern[1] / (base_pattern[1] + base_pattern[3])
                    adjusted_gap1 = (total_gap_needed * gap_ratio) / border_width
                    adjusted_gap2 = (total_gap_needed * (1.0 - gap_ratio)) / border_width
                    stroker.setDashPattern([dash_len, adjusted_gap1, dot_len, adjusted_gap2])

                # CRITICAL: Calculate dash offset to center pattern and avoid clustering at corners
                # Offset by half pattern length to distribute evenly around the path
                # For closed paths, this prevents dash segments from overlapping at start/end point
                dash_offset = (path_length / num_rounded) / 2.0
                stroker.setDashOffset(dash_offset / border_width)  # Convert to width multiples

                dashed_stroke_path = stroker.createStroke(stroke_base_path)

                # Subtract inner_path to get only the outer portion (no overlap with background)
                dashed_border_ring = dashed_stroke_path.subtracted(inner_path)

                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(border_color)))
                painter.drawPath(dashed_border_ring)
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
