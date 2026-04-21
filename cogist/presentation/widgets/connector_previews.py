"""Preview generators for connector types.

Provides functions to generate visual previews for different connector shapes.
"""

from PySide6.QtCore import QPointF, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QPixmap


def generate_bezier_preview(size: QSize, selected: bool = False) -> QPixmap:
    """Generate preview for Bezier (S-curve) connector.

    Args:
        size: Preview size

    Returns:
        QPixmap with Bezier curve preview
    """
    pixmap = QPixmap(size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Draw S-curve bezier - centered in pixmap
    path = QPainterPath()
    margin_x = size.width() * 0.05  # 5% margin on each side for better centering
    start_x = margin_x
    start_y = size.height() * 0.5
    end_x = size.width() - margin_x
    end_y = size.height() * 0.5

    path.moveTo(start_x, start_y)

    # Calculate control points for S-curve
    dx = end_x - start_x
    control_offset = abs(dx) * 0.4

    if dx >= 0:
        control1 = QPointF(start_x + control_offset, start_y)
        control2 = QPointF(end_x - control_offset, end_y)
    else:
        control1 = QPointF(start_x - control_offset, start_y)
        control2 = QPointF(end_x + control_offset, end_y)

    path.cubicTo(control1, control2, QPointF(end_x, end_y))

    # Draw the curve
    color = "#FFFFFF" if selected else "#000000"  # White if selected, black otherwise
    pen = QPen(QColor(color), 2.0, Qt.SolidLine, Qt.RoundCap)
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
