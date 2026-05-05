"""Preview generators for node shapes.

Provides functions to generate visual previews for different node shapes,
used in the VisualSelector widget for shape selection.
"""

from qtpy.QtCore import QSize, Qt
from qtpy.QtGui import QColor, QPainter, QPen, QPixmap


def generate_rounded_rect_preview(size: QSize, selected: bool = False) -> QPixmap:
    """Generate preview for rounded rectangle shape.

    Args:
        size: Preview size
        selected: Whether this option is currently selected

    Returns:
        QPixmap with rounded rectangle preview
    """
    pixmap = QPixmap(size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Draw rounded rect with border
    # Use relative margins to adapt to different sizes
    margin_x = size.width() * 0.08  # 8% horizontal margin
    margin_y = size.height() * 0.1  # 10% vertical margin
    rect = pixmap.rect().adjusted(margin_x, margin_y, -margin_x, -margin_y)

    color = QColor("#FFFFFF") if selected else QColor("#000000")
    pen = QPen(color, 2)
    painter.setPen(pen)
    painter.setBrush(Qt.NoBrush)
    painter.drawRoundedRect(rect, 6, 6)

    painter.end()
    return pixmap


def generate_circle_preview(size: QSize, selected: bool = False) -> QPixmap:
    """Generate preview for circle shape.

    Args:
        size: Preview size
        selected: Whether this option is currently selected

    Returns:
        QPixmap with circle preview
    """
    pixmap = QPixmap(size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Draw circle
    # Use relative margins to adapt to different sizes
    margin_x = size.width() * 0.08  # 8% horizontal margin
    margin_y = size.height() * 0.1  # 10% vertical margin
    rect = pixmap.rect().adjusted(margin_x, margin_y, -margin_x, -margin_y)

    color = QColor("#FFFFFF") if selected else QColor("#000000")
    pen = QPen(color, 2)
    painter.setPen(pen)
    painter.setBrush(Qt.NoBrush)
    painter.drawEllipse(rect)

    painter.end()
    return pixmap


def generate_bottom_line_preview(size: QSize, selected: bool = False) -> QPixmap:
    """Generate preview for bottom decorative line shape.

    Shows solid bottom border with dashed borders on other three sides.

    Args:
        size: Preview size
        selected: Whether this option is currently selected

    Returns:
        QPixmap with bottom line preview
    """
    pixmap = QPixmap(size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Use relative margins to adapt to different sizes
    margin_x = size.width() * 0.08  # 8% horizontal margin
    margin_y = size.height() * 0.1  # 10% vertical margin
    rect = pixmap.rect().adjusted(margin_x, margin_y, -margin_x, -margin_y)

    color = QColor("#FFFFFF") if selected else QColor("#000000")

    # Draw dotted borders for top, left, right
    dotted_pen = QPen(color, 1.0, Qt.DotLine)
    painter.setPen(dotted_pen)
    painter.setBrush(Qt.NoBrush)

    # Top border (dashed)
    painter.drawLine(rect.left(), rect.top(), rect.right(), rect.top())
    # Left border (dashed)
    painter.drawLine(rect.left(), rect.top(), rect.left(), rect.bottom())
    # Right border (dashed)
    painter.drawLine(rect.right(), rect.top(), rect.right(), rect.bottom())

    # Bottom border (solid)
    solid_pen = QPen(color, 2, Qt.SolidLine, Qt.RoundCap)
    painter.setPen(solid_pen)
    painter.drawLine(rect.left(), rect.bottom(), rect.right(), rect.bottom())

    painter.end()
    return pixmap


def generate_left_line_preview(size: QSize, selected: bool = False) -> QPixmap:
    """Generate preview for left decorative line shape.

    Shows solid left border with dashed borders on other three sides.

    Args:
        size: Preview size
        selected: Whether this option is currently selected

    Returns:
        QPixmap with left line preview
    """
    pixmap = QPixmap(size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # Use relative margins to adapt to different sizes
    margin_x = size.width() * 0.08  # 8% horizontal margin
    margin_y = size.height() * 0.1  # 10% vertical margin
    rect = pixmap.rect().adjusted(margin_x, margin_y, -margin_x, -margin_y)

    color = QColor("#FFFFFF") if selected else QColor("#000000")

    # Draw dotted borders for top, bottom, right
    dotted_pen = QPen(color, 1.0, Qt.DotLine)
    painter.setPen(dotted_pen)
    painter.setBrush(Qt.NoBrush)

    # Top border (dashed)
    painter.drawLine(rect.left(), rect.top(), rect.right(), rect.top())
    # Bottom border (dashed)
    painter.drawLine(rect.left(), rect.bottom(), rect.right(), rect.bottom())
    # Right border (dashed)
    painter.drawLine(rect.right(), rect.top(), rect.right(), rect.bottom())

    # Left border (solid)
    solid_pen = QPen(color, 2, Qt.SolidLine, Qt.RoundCap)
    painter.setPen(solid_pen)
    painter.drawLine(rect.left(), rect.top(), rect.left(), rect.bottom())

    painter.end()
    return pixmap
