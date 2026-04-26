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
    3. Ensuring sceneRect is always >= viewport size (scrollbars always work)
    4. Temporary overrides for export operations

    Design principles:
    - Avoids超大 sceneRect that breaks scrollbars (Qt INT range limitation)
    - Maintains padding around content for visual comfort
    - Supports precise control for export/printing scenarios
    - sceneRect >= viewport ensures alignment offsets don't interfere
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
        self._view: QGraphicsView | None = None

    def set_view(self, view: QGraphicsView) -> None:
        """Set the view reference for viewport size checks.

        Args:
            view: The QGraphicsView containing this scene
        """
        self._view = view

    def _get_viewport_size(self) -> tuple[float, float] | None:
        """Get current viewport size if available.

        Returns:
            Tuple of (width, height) or None if view is not set
        """
        if self._view is None:
            return None
        viewport = self._view.viewport()
        if viewport is None:
            return None
        return float(viewport.width()), float(viewport.height())

    def initialize_from_viewport(self) -> None:
        """Set initial scene rect based on viewport size.

        This ensures no scrollbars appear in the initial empty state
        and that scrollbars always work (sceneRect >= viewport).
        """
        vp_size = self._get_viewport_size()
        if vp_size is None:
            return
        width, height = vp_size
        # Center the initial rect at origin
        self.scene.setSceneRect(-width / 2, -height / 2, width, height)

    def update_from_content(self, margin: float | None = None) -> None:
        """Update scene rect based on actual content bounds + margin.

        This should be called after layout calculations to ensure
        sceneRect tightly fits the content with appropriate padding.

        CRITICAL: Ensures sceneRect is always >= viewport size,
        so scrollbars remain active and alignment offsets don't interfere.

        Args:
            margin: Override default margin (uses default_margin if None)
        """
        effective_margin = margin if margin is not None else self.default_margin

        content_rect = self.scene.itemsBoundingRect()

        if content_rect.isEmpty():
            return

        # Expand content rect by margin on all sides
        expanded_rect = content_rect.adjusted(
            -effective_margin,
            -effective_margin,
            effective_margin,
            effective_margin,
        )

        # CRITICAL: Ensure sceneRect is at least as large as the viewport.
        # This guarantees scrollbars are always active.
        vp_size = self._get_viewport_size()
        if vp_size is not None:
            vw, vh = vp_size
            if expanded_rect.width() < vw:
                extra = vw - expanded_rect.width()
                expanded_rect.adjust(-extra / 2, 0, extra / 2, 0)
            if expanded_rect.height() < vh:
                extra = vh - expanded_rect.height()
                expanded_rect.adjust(0, -extra / 2, 0, extra / 2)

        self.scene.setSceneRect(expanded_rect)

    def ensure_minimum_size(self) -> None:
        """Expand sceneRect to at least match the current viewport size.

        Call this when the viewport grows (e.g., panel closes, window resizes)
        to ensure sceneRect >= viewport so scrollbars remain active.
        """
        vp_size = self._get_viewport_size()
        if vp_size is None:
            return
        vw, vh = vp_size

        current_rect = self.scene.sceneRect()
        if current_rect.width() >= vw and current_rect.height() >= vh:
            return

        # Expand to fit viewport while keeping center position
        new_rect = QRectF(current_rect)
        if new_rect.width() < vw:
            extra = vw - new_rect.width()
            new_rect.adjust(-extra / 2, 0, extra / 2, 0)
        if new_rect.height() < vh:
            extra = vh - new_rect.height()
            new_rect.adjust(0, -extra / 2, 0, extra / 2)

        self.scene.setSceneRect(new_rect)

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
