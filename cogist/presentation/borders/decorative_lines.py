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

        # Set border style
        border_style = style_config.get("border_style", "solid")
        if border_style == "dashed":
            pen.setStyle(Qt.DashLine)
        elif border_style == "dotted":
            pen.setStyle(Qt.DotLine)
        elif border_style == "dash_dot":
            pen.setStyle(Qt.DashDotLine)
        else:
            pen.setStyle(Qt.SolidLine)

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
    """Left decorative line border style (adapts to node side for directional rendering)."""

    def draw(self, painter: QPainter, rect, style_config: dict) -> None:
        """Draw vertical decorative line on the side facing parent.

        Args:
            painter: QPainter instance
            rect: Node bounding rectangle
            style_config: Style configuration dictionary with 'is_right_side' flag
        """
        bg_color = style_config.get("bg_color")
        border_color = style_config.get("border_color")
        border_width = style_config.get("border_width", 2)
        is_right_side = style_config.get("is_right_side", True)  # Default: right side

        # Draw background fill (rectangle for decorative lines)
        if bg_color:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(bg_color)))
            painter.drawRect(rect)

        # Don't draw line if width is 0 or color is missing
        if not border_color or border_width <= 0:
            return

        # Draw vertical line on the appropriate edge
        pen = QPen(QColor(border_color), border_width)
        pen.setCapStyle(Qt.RoundCap)

        # Set border style
        border_style = style_config.get("border_style", "solid")
        if border_style == "dashed":
            pen.setStyle(Qt.DashLine)
        elif border_style == "dotted":
            pen.setStyle(Qt.DotLine)
        elif border_style == "dash_dot":
            pen.setStyle(Qt.DashDotLine)
        else:
            pen.setStyle(Qt.SolidLine)

        painter.setPen(pen)

        # Calculate line endpoints (full height)
        y1 = rect.top()
        y2 = rect.bottom()

        # Adaptive direction: draw on the side facing the parent
        x = rect.left() if is_right_side else rect.right()

        painter.drawLine(x, y1, x, y2)

    def get_selection_path(self, rect, style_config: dict) -> QPainterPath:
        """Get selection highlight path for left line shape.

        Uses a rounded rectangle around the text area for visibility.
        """
        highlight_rect = rect.adjusted(-3, -3, 3, 3)
        path = QPainterPath()
        path.addRoundedRect(highlight_rect, 4, 4)
        return path
