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
    """Generate preview for Straight connector.

    Args:
        size: Preview size

    Returns:
        QPixmap with straight line preview
    """
    pixmap = QPixmap(size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Draw straight diagonal line - centered in pixmap
    margin_x = size.width() * 0.05  # 5% margin for better centering
    margin_y = size.height() * 0.2  # 20% margin top/bottom
    start_x = margin_x
    start_y = margin_y
    end_x = size.width() - margin_x
    end_y = size.height() - margin_y

    path = QPainterPath()
    path.moveTo(start_x, start_y)
    path.lineTo(end_x, end_y)

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

    # Calculate corner radius (limit to avoid overlapping)
    dx = end_x - start_x
    dy = end_y - start_y
    corner_length = 15.0

    path = QPainterPath()
    path.moveTo(start_x, start_y)

    # Draw orthogonal path with rounded corners using quadratic Bezier curves
    # Corner points: (mid_x, start_y) and (mid_x, end_y)
    corner1 = QPointF(mid_x, start_y)
    corner2 = QPointF(mid_x, end_y)

    # First segment: from start to corner1
    # Calculate distance from corner1 to start and end_y
    dist_start_to_corner1 = abs(mid_x - start_x)
    dist_corner1_to_corner2_y = abs(end_y - start_y)

    if (
        dist_start_to_corner1 > corner_length
        and dist_corner1_to_corner2_y > corner_length
    ):
        # Draw to corner1 with rounded corner
        curve_start1 = corner1 + QPointF(-corner_length if dx > 0 else corner_length, 0)
        path.lineTo(curve_start1)
        # Quadratic curve through corner1
        curve_end1 = corner1 + QPointF(0, corner_length if dy > 0 else -corner_length)
        path.quadTo(corner1, curve_end1)
    else:
        path.lineTo(corner1)

    # Second segment: from corner1 to corner2
    # Draw to corner2 with rounded corner
    if dist_corner1_to_corner2_y > 2 * corner_length:
        curve_start2 = corner2 + QPointF(0, -corner_length if dy > 0 else corner_length)
        path.lineTo(curve_start2)
        # Quadratic curve through corner2
        curve_end2 = corner2 + QPointF(corner_length if dx > 0 else -corner_length, 0)
        path.quadTo(corner2, curve_end2)
    else:
        path.lineTo(corner2)
        curve_end2 = QPointF(end_x, end_y)

    # Final segment to end point
    path.lineTo(end_x, end_y)

    # Draw the path
    color = "#FFFFFF" if selected else "#000000"  # White if selected, black otherwise
    pen = QPen(QColor(color), 2.0, Qt.SolidLine, Qt.RoundCap)
    painter.setPen(pen)
    painter.drawPath(path)

    painter.end()
    return pixmap
