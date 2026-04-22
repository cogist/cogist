"""Preview generators for connector types.

Provides functions to generate visual previews for different connector shapes.
"""

from PySide6.QtCore import QPointF, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QPixmap


def generate_bezier_preview(size: QSize, selected: bool = False) -> QPixmap:
    """Generate preview for Bezier (S-curve) connector with gradient width.

    Args:
        size: Preview size

    Returns:
        QPixmap with Bezier curve preview (wavy S-curve, thick left to thin right)
    """
    pixmap = QPixmap(size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Draw wavy S-curve bezier with gradient width
    margin_x = size.width() * 0.05
    start_x = margin_x
    start_y = size.height() * 0.5
    end_x = size.width() - margin_x
    end_y = size.height() * 0.5

    # Calculate control points for wavy S-curve
    dx = end_x - start_x
    control_offset_x = abs(dx) * 0.4
    control_offset_y = size.height() * 0.3  # More pronounced curve

    if dx >= 0:
        control1 = QPointF(start_x + control_offset_x, start_y - control_offset_y)
        control2 = QPointF(end_x - control_offset_x, end_y + control_offset_y)
    else:
        control1 = QPointF(start_x - control_offset_x, start_y)
        control2 = QPointF(end_x + control_offset_x, end_y)

    # Build complete path
    path = QPainterPath()
    path.moveTo(start_x, start_y)
    path.cubicTo(control1, control2, QPointF(end_x, end_y))

    # Draw with gradient width effect (thick left to thin right)
    color = QColor("#FFFFFF") if selected else QColor("#000000")
    start_width = 4.0
    end_width = 1.0
    segments = 100

    for i in range(segments):
        t1 = i / segments
        t2 = (i + 1) / segments
        t_mid = (t1 + t2) / 2

        # Interpolate width
        width = start_width * (1 - t_mid) + end_width * t_mid

        pen = QPen(color, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)

        # Calculate points on bezier curve
        t1_2 = 1 - t1
        t2_2 = 1 - t2

        pt1_x = (
            t1_2**3 * start_x
            + 3 * t1_2**2 * t1 * control1.x()
            + 3 * t1_2 * t1**2 * control2.x()
            + t1**3 * end_x
        )
        pt1_y = (
            t1_2**3 * start_y
            + 3 * t1_2**2 * t1 * control1.y()
            + 3 * t1_2 * t1**2 * control2.y()
            + t1**3 * end_y
        )

        pt2_x = (
            t2_2**3 * start_x
            + 3 * t2_2**2 * t2 * control1.x()
            + 3 * t2_2 * t2**2 * control2.x()
            + t2**3 * end_x
        )
        pt2_y = (
            t2_2**3 * start_y
            + 3 * t2_2**2 * t2 * control1.y()
            + 3 * t2_2 * t2**2 * control2.y()
            + t2**3 * end_y
        )

        painter.drawLine(QPointF(pt1_x, pt1_y), QPointF(pt2_x, pt2_y))

    painter.end()
    return pixmap


def generate_sharp_first_rounded_preview(
    size: QSize, selected: bool = False
) -> QPixmap:
    """Generate preview for Sharp-First Rounded connector.

    Shows a path with:
    - First corner: Sharp 90-degree angle
    - Second corner: Rounded corner

    Args:
        size: Preview size

    Returns:
        QPixmap with sharp-first rounded orthogonal preview
    """
    pixmap = QPixmap(size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Draw sharp-first rounded path - centered in pixmap
    margin_x = size.width() * 0.05
    margin_y = size.height() * 0.2
    start_x = margin_x
    start_y = margin_y
    end_x = size.width() - margin_x
    end_y = size.height() - margin_y
    mid_x = (start_x + end_x) / 2

    # Calculate corner radius
    dx = end_x - start_x
    dy = end_y - start_y
    max_radius_x = abs(dx) * 0.35
    max_radius_y = abs(dy) * 0.35
    radius = min(15.0, max_radius_x, max_radius_y)

    # Define corner points
    corner1 = QPointF(mid_x, start_y)  # Sharp corner
    corner2 = QPointF(mid_x, end_y)  # Rounded corner

    path = QPainterPath()
    path.moveTo(start_x, start_y)

    # Draw to sharp corner (horizontal then vertical)
    path.lineTo(corner1)
    path.lineTo(corner2)

    # Draw rounded corner at corner2
    if radius > 0:
        # Calculate direction vectors
        v1 = corner1 - corner2  # Incoming (vertical)
        v2 = QPointF(end_x - corner2.x(), 0)  # Outgoing (horizontal)

        len1 = (v1.x() ** 2 + v1.y() ** 2) ** 0.5
        len2 = (v2.x() ** 2 + v2.y() ** 2) ** 0.5

        if len1 > 0 and len2 > 0:
            v1 = QPointF(v1.x() / len1, v1.y() / len1)
            v2 = QPointF(v2.x() / len2, v2.y() / len2)

            # Calculate arc start and end points
            arc_start = corner2 + v1 * radius
            arc_end = corner2 + v2 * radius

            # Draw to arc start
            path.lineTo(arc_start)

            # Use quadratic Bezier for rounded corner
            path.quadTo(corner2, arc_end)

            # Draw final segment
            path.lineTo(end_x, end_y)
        else:
            path.lineTo(end_x, end_y)
    else:
        path.lineTo(end_x, end_y)

    # Draw the path
    color = "#FFFFFF" if selected else "#000000"
    pen = QPen(QColor(color), 2.0, Qt.SolidLine, Qt.RoundCap)
    painter.setPen(pen)
    painter.drawPath(path)

    painter.end()
    return pixmap


def generate_bezier_uniform_preview(size: QSize, selected: bool = False) -> QPixmap:
    """Generate preview for Bezier connector with uniform width (2px).

    Args:
        size: Preview size

    Returns:
        QPixmap with uniform width Bezier curve preview (wavy S-curve, 2px width)
    """
    pixmap = QPixmap(size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Draw wavy S-curve bezier with uniform width
    margin_x = size.width() * 0.05
    start_x = margin_x
    start_y = size.height() * 0.5
    end_x = size.width() - margin_x
    end_y = size.height() * 0.5

    # Calculate control points for wavy S-curve (same curvature as gradient version)
    dx = end_x - start_x
    control_offset_x = abs(dx) * 0.4
    control_offset_y = size.height() * 0.3

    if dx >= 0:
        control1 = QPointF(start_x + control_offset_x, start_y - control_offset_y)
        control2 = QPointF(end_x - control_offset_x, end_y + control_offset_y)
    else:
        control1 = QPointF(start_x - control_offset_x, start_y)
        control2 = QPointF(end_x + control_offset_x, end_y)

    # Build complete path
    path = QPainterPath()
    path.moveTo(start_x, start_y)
    path.cubicTo(control1, control2, QPointF(end_x, end_y))

    # Draw with uniform width (2px)
    color = "#FFFFFF" if selected else "#000000"
    pen = QPen(QColor(color), 2.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    painter.setPen(pen)
    painter.drawPath(path)

    painter.end()
    return pixmap


def generate_straight_preview(size: QSize, selected: bool = False) -> QPixmap:
    """Generate preview for Straight connector with horizontal segments.

    The preview shows:
    - First 1/4: Horizontal line from start
    - Middle 2/4: Diagonal connecting line
    - Last 1/4: Horizontal line to end

    Args:
        size: Preview size

    Returns:
        QPixmap with segmented line preview
    """
    pixmap = QPixmap(size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Draw segmented line - centered in pixmap
    margin_x = size.width() * 0.05  # 5% margin for better centering
    margin_y = size.height() * 0.2  # 20% margin top/bottom
    start_x = margin_x
    start_y = margin_y
    end_x = size.width() - margin_x
    end_y = size.height() - margin_y

    # Calculate segment points
    dx = end_x - start_x
    horizontal_segment = dx / 4.0

    # First point: 1/4 horizontal from start
    point1_x = start_x + horizontal_segment
    point1_y = start_y

    # Second point: 3/4 horizontal, 1/4 vertical (start of last horizontal segment)
    point2_x = start_x + 3 * horizontal_segment
    point2_y = end_y

    # Draw the segmented path
    path = QPainterPath()
    path.moveTo(start_x, start_y)
    path.lineTo(point1_x, point1_y)  # First 1/4 horizontal
    path.lineTo(point2_x, point2_y)  # Middle 2/4 diagonal
    path.lineTo(end_x, end_y)  # Last 1/4 horizontal

    # Draw the line
    color = "#FFFFFF" if selected else "#000000"  # White if selected, black otherwise
    pen = QPen(QColor(color), 2.0, Qt.SolidLine, Qt.RoundCap)
    painter.setPen(pen)
    painter.drawPath(path)

    painter.end()
    return pixmap


def generate_orthogonal_preview(size: QSize, selected: bool = False) -> QPixmap:
    """Generate preview for Orthogonal (right-angle) connector.

    Args:
        size: Preview size

    Returns:
        QPixmap with orthogonal line preview
    """
    pixmap = QPixmap(size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Draw orthogonal path (right-angle) - centered in pixmap
    margin_x = size.width() * 0.05  # 5% margin for better centering
    margin_y = size.height() * 0.2  # 20% margin top/bottom
    start_x = margin_x
    start_y = margin_y
    end_x = size.width() - margin_x
    end_y = size.height() - margin_y
    mid_x = (start_x + end_x) / 2

    path = QPainterPath()
    path.moveTo(start_x, start_y)
    path.lineTo(mid_x, start_y)  # Horizontal segment
    path.lineTo(mid_x, end_y)  # Vertical segment
    path.lineTo(end_x, end_y)  # Final horizontal segment

    # Draw the path
    color = "#FFFFFF" if selected else "#000000"  # White if selected, black otherwise
    pen = QPen(QColor(color), 2.0, Qt.SolidLine, Qt.RoundCap)
    painter.setPen(pen)
    painter.drawPath(path)

    painter.end()
    return pixmap


def generate_rounded_orthogonal_preview(size: QSize, selected: bool = False) -> QPixmap:
    """Generate preview for Rounded Orthogonal connector.

    Args:
        size: Preview size

    Returns:
        QPixmap with rounded orthogonal line preview
    """
    pixmap = QPixmap(size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Draw rounded orthogonal path - centered in pixmap
    margin_x = size.width() * 0.05  # 5% margin for better centering
    margin_y = size.height() * 0.2  # 20% margin top/bottom
    start_x = margin_x
    start_y = margin_y
    end_x = size.width() - margin_x
    end_y = size.height() - margin_y
    mid_x = (start_x + end_x) / 2

    # Calculate corner length (limit to avoid overlapping)
    dx = end_x - start_x
    dy = end_y - start_y
    # Dynamically calculate corner length based on available space
    # Each corner needs corner_length on both sides, so max is min segment / 2
    max_corner_x = abs(dx) * 0.35
    max_corner_y = abs(dy) * 0.35
    corner_length = min(15.0, max_corner_x, max_corner_y)

    # Build the list of key points
    points = [
        QPointF(start_x, start_y),
        QPointF(mid_x, start_y),
        QPointF(mid_x, end_y),
        QPointF(end_x, end_y),
    ]

    path = QPainterPath()
    path.moveTo(points[0])

    # Iterate through intermediate corner points and round them
    for i in range(1, len(points) - 1):
        p1 = points[i - 1]  # Previous point
        p2 = points[i]  # Current corner point
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
        arc_start = p2 + v1 * corner_length
        arc_end = p2 + v2 * corner_length

        # Draw straight line to arc start
        path.lineTo(arc_start)

        # Use quadratic Bezier curve with corner as control point
        path.quadTo(p2, arc_end)

    # Draw final segment to end point
    path.lineTo(points[-1])

    # Draw the path
    color = "#FFFFFF" if selected else "#000000"  # White if selected, black otherwise
    pen = QPen(QColor(color), 2.0, Qt.SolidLine, Qt.RoundCap)
    painter.setPen(pen)
    painter.drawPath(path)

    painter.end()
    return pixmap
