"""Abstract base class for node border drawing strategies."""

from abc import ABC, abstractmethod

from PySide6.QtCore import QRectF
from PySide6.QtGui import QPainter, QPainterPath


class BorderStrategy(ABC):
    """Abstract base class for node border/shape drawing strategies.

    Each strategy defines how to draw a node's visual appearance,
    including background fill and border decoration.

    This follows the Strategy pattern, consistent with ConnectorStrategy
    used for edge rendering.
    """

    @abstractmethod
    def draw(
        self,
        painter: QPainter,
        rect: QRectF,
        style_config: dict,
    ) -> None:
        """Draw the node shape and border.

        Args:
            painter: QPainter instance for drawing
            rect: Node's bounding rectangle in item coordinates
            style_config: Dictionary containing style parameters:
                - bg_color: Background color (str or QColor)
                - border_color: Border/line color (str or QColor)
                - border_width: Width of border/line (int)
                - border_radius: Corner radius for rounded shapes (int)
                - padding_w: Horizontal padding (int)
                - padding_h: Vertical padding (int)
        """
        pass

    @abstractmethod
    def get_selection_path(self, rect: QRectF, style_config: dict) -> QPainterPath:
        """Get path for selection highlight.

        Args:
            rect: Node's bounding rectangle
            style_config: Style configuration dictionary

        Returns:
            QPainterPath for drawing selection indicator
        """
        pass
