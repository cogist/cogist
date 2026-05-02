"""Container shape border strategies (shapes with background fill)."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen

from .base import BorderStrategy


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
            # Create the outer boundary path (where the border's outer edge should be)
            half_width = border_width / 2.0
            outer_rect = rect.adjusted(-half_width, -half_width, half_width, half_width)
            outer_radius = radius + half_width
            outer_path = QPainterPath()
            outer_path.addRoundedRect(outer_rect, outer_radius, outer_radius)

            # Step 1: Draw border outline first (just the line, no fill)
            pen = QPen(QColor(border_color), border_width)
            if border_style == "dashed":
                pen.setStyle(Qt.DashLine)
            elif border_style == "dotted":
                pen.setStyle(Qt.DotLine)
            elif border_style == "dash_dot":
                pen.setStyle(Qt.DashDotLine)
            else:
                pen.setStyle(Qt.SolidLine)

            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(outer_path)  # Draw the outer edge line

            # Step 2: Fill the entire inner area (background fills to the inner edge of the border)
            if bg_color:
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(bg_color)))
                painter.fillPath(outer_path, painter.brush())
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
            # Create the outer boundary path (where the border's outer edge should be)
            half_width = border_width / 2.0
            outer_rect = rect.adjusted(-half_width, -half_width, half_width, half_width)
            outer_path = QPainterPath()
            outer_path.addEllipse(outer_rect)

            # Step 1: Draw border outline first (just the line, no fill)
            pen = QPen(QColor(border_color), border_width)
            if border_style == "dashed":
                pen.setStyle(Qt.DashLine)
            elif border_style == "dotted":
                pen.setStyle(Qt.DotLine)
            elif border_style == "dash_dot":
                pen.setStyle(Qt.DashDotLine)
            else:
                pen.setStyle(Qt.SolidLine)

            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(outer_path)  # Draw the outer edge line

            # Step 2: Fill the entire inner area (background fills to the inner edge of the border)
            if bg_color:
                painter.setPen(Qt.NoPen)
                painter.setBrush(QBrush(QColor(bg_color)))
                painter.fillPath(outer_path, painter.brush())
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
