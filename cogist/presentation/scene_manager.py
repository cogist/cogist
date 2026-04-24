"""Scene management utilities for dynamic canvas sizing.

This module provides scene rect management to support infinite canvas behavior
while maintaining proper scrollbar functionality and export precision.

Architecture:
- Presentation Layer concern: Manages Qt Graphics View scene boundaries
- Dynamic sizing: Updates sceneRect based on content + margin after layout
- Export support: Allows temporary precise sceneRect for SVG/PNG/PDF export
"""

from PySide6.QtCore import QRectF
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView


class SceneRectManager:
    """Manages dynamic scene rectangle for infinite canvas behavior.

    This class handles:
    1. Initial scene rect setup (based on viewport size)
    2. Dynamic updates after layout changes (content + margin)
    3. Temporary overrides for export operations

    Design principles:
    - Avoids超大 sceneRect that breaks scrollbars (Qt INT range limitation)
    - Maintains padding around content for visual comfort
    - Supports precise control for export/printing scenarios
    """

    def __init__(self, scene: QGraphicsScene, default_margin: float = 100.0):
        """Initialize scene rect manager.

        Args:
            scene: The QGraphicsScene to manage
            default_margin: Padding around content in scene coordinates
        """
        self.scene = scene
        self.default_margin = default_margin
        self._original_rect: QRectF | None = None

    def initialize_from_viewport(self, view: QGraphicsView) -> None:
        """Set initial scene rect based on viewport size.

        This ensures no scrollbars appear in the initial empty state.

        Args:
            view: The QGraphicsView containing the scene
        """
        viewport_size = view.viewport().size()
        width = float(viewport_size.width())
        height = float(viewport_size.height())

        # Center the initial rect at origin
        self.scene.setSceneRect(-width / 2, -height / 2, width, height)

    def update_from_content(self, margin: float | None = None) -> None:
        """Update scene rect based on actual content bounds + margin.

        This should be called after layout calculations to ensure
        sceneRect tightly fits the content with appropriate padding.

        Args:
            margin: Override default margin (uses default_margin if None)
        """
        effective_margin = margin if margin is not None else self.default_margin

        content_rect = self.scene.itemsBoundingRect()

        if content_rect.isEmpty():
            # No content yet, keep current rect or set a reasonable default
            return

        # Expand content rect by margin on all sides
        expanded_rect = content_rect.adjusted(
            -effective_margin,
            -effective_margin,
            effective_margin,
            effective_margin
        )

        self.scene.setSceneRect(expanded_rect)

    def override_for_export(self, export_rect: QRectF) -> QRectF:
        """Temporarily override scene rect for export operations.

        Use this when you need precise control over export dimensions
        (e.g., fitting to A4 paper size for PDF export).

        Args:
            export_rect: The exact rect to use for export

        Returns:
            The original scene rect (call restore_original() to revert)
        """
        self._original_rect = self.scene.sceneRect()
        self.scene.setSceneRect(export_rect)
        return self._original_rect

    def restore_original(self) -> None:
        """Restore the original scene rect after export override."""
        if self._original_rect is not None:
            self.scene.setSceneRect(self._original_rect)
            self._original_rect = None

    def get_content_bounds(self) -> QRectF:
        """Get the current content bounding rectangle.

        Returns:
            The bounding rect of all items in the scene
        """
        return self.scene.itemsBoundingRect()
