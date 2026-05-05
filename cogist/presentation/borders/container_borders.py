"""Container shape border strategies (shapes with background fill)."""

from qtpy.QtCore import Qt
from qtpy.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen

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

            # Step 2: Draw border ring on top (only the ring area, no overlap)
            pen = QPen(QColor(border_color), 0)  # Pen width 0 - we're filling a path, not stroking
            if border_style == "dashed":
                pen.setStyle(Qt.DashLine)
            elif border_style == "dotted":
                pen.setStyle(Qt.DotLine)
            elif border_style == "dash_dot":
                pen.setStyle(Qt.DashDotLine)
            else:
                pen.setStyle(Qt.SolidLine)

            painter.setPen(pen)
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

            # Step 2: Draw border ring on top (only the ring area, no overlap)
            pen = QPen(QColor(border_color), 0)  # Pen width 0 - we're filling a path, not stroking
            if border_style == "dashed":
                pen.setStyle(Qt.DashLine)
            elif border_style == "dotted":
                pen.setStyle(Qt.DotLine)
            elif border_style == "dash_dot":
                pen.setStyle(Qt.DashDotLine)
            else:
                pen.setStyle(Qt.SolidLine)

            painter.setPen(pen)
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
