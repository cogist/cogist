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

        # Draw background fill (original rect)
        if bg_color:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(bg_color)))
            # Disable anti-aliasing for sharp edges
            painter.setRenderHint(QPainter.Antialiasing, False)
            painter.drawRoundedRect(rect, radius, radius)
            # Restore anti-aliasing for other elements
            painter.setRenderHint(QPainter.Antialiasing, True)

        # Draw border completely outside background
        # To match inner edge curvature with background, outer radius must be larger
        if border_width > 0 and border_color:
            pen = QPen(QColor(border_color), border_width)

            # Set border style
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
            # Expand rect by half border width minus tiny overlap to avoid anti-aliasing gaps
            # The 0.5px overlap ensures inner edges blend seamlessly with background
            half_width = border_width / 2.0
            overlap = 0.5  # Tiny overlap to prevent anti-aliasing gaps
            border_rect = rect.adjusted(-(half_width - overlap), -(half_width - overlap),
                                       (half_width - overlap), (half_width - overlap))
            # Increase radius proportionally to maintain inner edge curvature
            outer_radius = radius + half_width - overlap
            # Disable anti-aliasing for sharp edges
            painter.setRenderHint(QPainter.Antialiasing, False)
            painter.drawRoundedRect(border_rect, outer_radius, outer_radius)
            # Restore anti-aliasing for other elements
            painter.setRenderHint(QPainter.Antialiasing, True)

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

        # Draw background fill (original rect)
        if bg_color:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QBrush(QColor(bg_color)))
            # Disable anti-aliasing for sharp edges
            painter.setRenderHint(QPainter.Antialiasing, False)
            painter.drawEllipse(rect)
            # Restore anti-aliasing for other elements
            painter.setRenderHint(QPainter.Antialiasing, True)

        # Draw border completely outside background
        if border_width > 0 and border_color:
            pen = QPen(QColor(border_color), border_width)

            # Set border style
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
            # Expand rect by half border width minus tiny overlap to avoid anti-aliasing gaps
            half_width = border_width / 2.0
            overlap = 0.5  # Tiny overlap to prevent anti-aliasing gaps
            border_rect = rect.adjusted(-(half_width - overlap), -(half_width - overlap),
                                       (half_width - overlap), (half_width - overlap))
            # Disable anti-aliasing for sharp edges
            painter.setRenderHint(QPainter.Antialiasing, False)
            painter.drawEllipse(border_rect)
            # Restore anti-aliasing for other elements
            painter.setRenderHint(QPainter.Antialiasing, True)

    def get_selection_path(self, rect, style_config: dict) -> QPainterPath:
        """Get selection highlight path for circle/ellipse."""
        highlight_rect = rect.adjusted(-3, -3, 3, 3)
        path = QPainterPath()
        path.addEllipse(highlight_rect)
        return path
