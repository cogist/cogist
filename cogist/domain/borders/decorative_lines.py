"""Decorative line border strategies (single-side lines, no background)."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen

from .base import BorderStrategy


class BottomLineBorder(BorderStrategy):
    """Bottom decorative line (transparent background, line at bottom)."""

    def draw(self, painter: QPainter, rect, style_config: dict) -> None:
        """Draw bottom decorative line.

        Args:
            painter: QPainter instance
            rect: Node bounding rectangle
            style_config: Style configuration dictionary
        """
        bg_color = style_config.get("bg_color")
        border_color = style_config.get("border_color")
        border_width = style_config.get("border_width", 2)

        # Draw background fill (rectangle for decorative lines)
        if bg_color:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(bg_color)))
            painter.drawRect(rect)

        # Don't draw line if width is 0 or color is missing
        if not border_color or border_width <= 0:
            return

        # Draw bottom line
        pen = QPen(QColor(border_color), border_width)
        pen.setCapStyle(Qt.RoundCap)  # Rounded ends look better
        painter.setPen(pen)

        # Calculate line endpoints (full width)
        y = rect.bottom()
        x1 = rect.left()
        x2 = rect.right()

        painter.drawLine(x1, y, x2, y)

    def get_selection_path(self, rect, style_config: dict) -> QPainterPath:
        """Get selection highlight path for bottom line shape.

        Uses a rounded rectangle around the text area for visibility.
        """
        highlight_rect = rect.adjusted(-3, -3, 3, 3)
        path = QPainterPath()
        path.addRoundedRect(highlight_rect, 4, 4)
        return path


class LeftLineBorder(BorderStrategy):
    """Left decorative line (transparent background, line at left)."""

    def draw(self, painter: QPainter, rect, style_config: dict) -> None:
        """Draw left decorative line.

        Args:
            painter: QPainter instance
            rect: Node bounding rectangle
            style_config: Style configuration dictionary
        """
        bg_color = style_config.get("bg_color")
        border_color = style_config.get("border_color")
        border_width = style_config.get("border_width", 2)

        # Draw background fill (rectangle for decorative lines)
        if bg_color:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(bg_color)))
            painter.drawRect(rect)

        # Don't draw line if width is 0 or color is missing
        if not border_color or border_width <= 0:
            return

        # Draw left line
        pen = QPen(QColor(border_color), border_width)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        # Calculate line endpoints (full height)
        x = rect.left()
        y1 = rect.top()
        y2 = rect.bottom()

        painter.drawLine(x, y1, x, y2)

    def get_selection_path(self, rect, style_config: dict) -> QPainterPath:
        """Get selection highlight path for left line shape.

        Uses a rounded rectangle around the text area for visibility.
        """
        highlight_rect = rect.adjusted(-3, -3, 3, 3)
        path = QPainterPath()
        path.addRoundedRect(highlight_rect, 4, 4)
        return path
