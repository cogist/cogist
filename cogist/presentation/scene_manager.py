"""Scene management utilities for dynamic canvas sizing.

This module provides scene rect management to support infinite canvas behavior
while maintaining proper scrollbar functionality and export precision.

Architecture:
- Presentation Layer concern: Manages Qt Graphics View scene boundaries
- Dynamic sizing: Updates sceneRect based on content + margin after layout
- Export support: Allows temporary precise sceneRect for SVG/PNG/PDF export
"""

from qtpy.QtCore import QRectF
from qtpy.QtWidgets import QGraphicsScene, QGraphicsView


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

        # Calculate sceneRect: content bounds + margin, with minimum viewport size
        expanded_rect = content_rect.adjusted(
            -effective_margin,
            -effective_margin,
            effective_margin,
            effective_margin,
        )

        # CRITICAL: Update sceneRect while preserving viewport position
        # to avoid triggering Qt's automatic viewport adjustment.
        view = self.scene.views()[0] if self.scene.views() else None
        viewport_center_view = None
        viewport_center_scene = None

        if view:
            # Save current viewport center in scene coordinates
            viewport_center_view = view.viewport().rect().center()
            viewport_center_scene = view.mapToScene(viewport_center_view)

        vp_size = self._get_viewport_size()
        if vp_size is not None:
            vw, vh = vp_size

            # Calculate the union of current rect and expanded content rect
            # This ensures we only expand, never shrink
            current_rect = self.scene.sceneRect()
            final_rect = current_rect.united(expanded_rect)

            # Ensure minimum size matches viewport
            if final_rect.width() < vw:
                extra = vw - final_rect.width()
                final_rect.adjust(-extra / 2, 0, extra / 2, 0)
            if final_rect.height() < vh:
                extra = vh - final_rect.height()
                final_rect.adjust(0, -extra / 2, 0, extra / 2)

            expanded_rect = final_rect

        self.scene.setSceneRect(expanded_rect)

        # Restore viewport position after sceneRect change
        if view and viewport_center_view and viewport_center_scene:
            # Calculate the offset needed to restore viewport center
            new_viewport_center_scene = view.mapToScene(viewport_center_view)
            offset_x = viewport_center_scene.x() - new_viewport_center_scene.x()
            offset_y = viewport_center_scene.y() - new_viewport_center_scene.y()

            # Scroll to restore original viewport position
            h_bar = view.horizontalScrollBar()
            v_bar = view.verticalScrollBar()
            h_bar.setValue(h_bar.value() + int(offset_x))
            v_bar.setValue(v_bar.value() + int(offset_y))

    def ensure_minimum_size(self) -> None:
        """Expand sceneRect to at least match the current viewport size.

        Call this when the viewport grows (e.g., panel closes, window resizes)
        to ensure sceneRect >= viewport so scrollbars remain active.

        CRITICAL: Also recenters sceneRect to keep scroll range symmetric,
        so compensation works in both directions.
        """
        vp_size = self._get_viewport_size()
        if vp_size is None:
            return
        vw, vh = vp_size

        current_rect = self.scene.sceneRect()

        # CRITICAL: Always make sceneRect LARGER than viewport to ensure
        # scrollbars are always active. Add extra margin for scroll range.
        extra_margin = 500.0  # Extra space for scrolling
        target_width = max(current_rect.width(), vw + extra_margin)
        target_height = max(current_rect.height(), vh + extra_margin)

        # Center around content
        content_center = current_rect.center()
        new_rect = QRectF(
            content_center.x() - target_width / 2,
            content_center.y() - target_height / 2,
            target_width,
            target_height,
        )

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
