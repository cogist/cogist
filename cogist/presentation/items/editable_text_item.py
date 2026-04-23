"""
Editable Text Item - Presentation Layer

A custom QGraphicsTextItem that supports inline editing with dynamic width control.
Provides perfect baseline alignment for both English and Chinese characters.

Features:
- Dynamic width expansion until max width, then auto-wrap
- Perfect baseline alignment (uses same rendering as display text)
- Signal emission for width changes to sync with parent node
- Enter/Escape key handling for finish/cancel editing
"""

from PySide6.QtCore import QEvent, QRectF, Qt, Signal
from PySide6.QtGui import QBrush, QColor, QPainter, QPen, QTextCursor
from PySide6.QtWidgets import QGraphicsTextItem


class EditableTextItem(QGraphicsTextItem):
    """
    Custom editable text item based on QGraphicsTextItem.

    This item dynamically adjusts its width during editing:
    1. Expands horizontally as text is typed
    2. When reaching max_width, enables word wrap
    3. Height adjusts automatically based on content
    """

    # Signals
    text_changed = Signal(str)  # Emitted when text changes
    width_changed = Signal(float)  # Emitted when width changes
    editing_finished = Signal()  # Emitted when editing finishes
    editing_cancelled = Signal()  # Emitted when editing is cancelled
    tab_pressed = Signal()  # Emitted when Tab key is pressed

    def __init__(self, text: str = "", max_width: float = 200, parent=None, mindmap_view=None):
        super().__init__(text, parent)

        self._text_cache = text
        self._max_width = max_width
        self._editing = False
        self._updating = False  # Prevent recursive updates
        self._tab_pressed = False  # Track if Tab key was pressed
        self._mindmap_view = mindmap_view  # Store reference to MindMapView

        # Visual settings
        self._border_color = QColor(Qt.transparent)  # No border by default
        self._border_width = 0

        # Set text interaction - we handle keys manually
        self.setTextInteractionFlags(Qt.NoTextInteraction)

        # Enable mouse and hover events
        self.setAcceptHoverEvents(True)
        self.setAcceptedMouseButtons(Qt.LeftButton)

        # Cache the ideal width before wrapping
        self._current_ideal_width = self._calculate_ideal_width()

        # CRITICAL: Connect to document's textChanged signal for IME support
        # This ensures width updates work with Chinese/Japanese input methods
        self.document().contentsChanged.connect(self._on_document_changed)

    def _calculate_ideal_width(self) -> float:
        """Calculate the ideal width for current text (no wrapping)."""
        # Temporarily disable wrapping to measure
        old_width = self.textWidth()
        self.setTextWidth(-1)  # -1 means no wrap

        # Get ideal width from document
        doc = self.document()
        ideal = doc.idealWidth()

        # Restore previous width
        self.setTextWidth(old_width)

        return ideal

    def _on_document_changed(self):
        """Handle document content changes (including IME input).

        This is called for any text modification, including:
        - Regular keyboard input
        - Chinese/Japanese IME confirmation
        - Paste operations
        """
        if not self._editing or self._updating:
            return

        # Update layout to recalculate width
        self._update_layout()

    def _update_layout(self):
        """Update text layout based on current content and max width."""
        if self._updating:
            return

        self._updating = True

        # Calculate required width (ideal width without wrapping)
        self._current_ideal_width = self._calculate_ideal_width()

        # CRITICAL: max_width=0 means unlimited width (no wrapping)
        # Dynamic wrapping strategy:
        # - If max_width == 0: no wrapping, unlimited width
        # - If ideal_width < max_width: no wrapping, use natural width
        # - If ideal_width >= max_width: enable wrapping at max_width with WrapAnywhere
        if self._max_width > 0 and self._current_ideal_width > self._max_width:
            # Enable wrapping at max width with forced wrapping for long words
            from PySide6.QtGui import QTextOption
            doc = self.document()
            text_option = doc.defaultTextOption()
            text_option.setWrapMode(QTextOption.WrapAnywhere)  # Force wrap at any character
            doc.setDefaultTextOption(text_option)

            self.setTextWidth(self._max_width)
            actual_width = self._max_width
        else:
            # No wrapping (either unlimited or natural width)
            # Reset to default wrap mode (wrap at word boundaries)
            from PySide6.QtGui import QTextOption
            doc = self.document()
            text_option = doc.defaultTextOption()
            text_option.setWrapMode(QTextOption.NoWrap)
            doc.setDefaultTextOption(text_option)

            self.setTextWidth(-1)
            actual_width = self._current_ideal_width

        # Emit width change signal with the actual text width (not including padding)
        self.width_changed.emit(actual_width)

        self._updating = False

    def start_editing(self, select_all: bool = False, initial_width: float = None):
        """
        Start editing mode.

        Args:
            select_all: If True, select all text; otherwise position cursor at end
            initial_width: Initial text width to maintain layout consistency (if provided, uses it; otherwise calculates from content)
        """
        self._editing = True
        self._text_cache = self.toPlainText()

        # Set text alignment to left-top (no forced wrapping initially)
        from PySide6.QtGui import QTextOption
        doc = self.document()
        text_option = QTextOption(Qt.AlignLeft | Qt.AlignTop)
        # Use default wrap mode - will be adjusted dynamically in _update_layout
        doc.setDefaultTextOption(text_option)

        # CRITICAL: Ensure document change signal is connected when editing starts
        # This handles IME input that doesn't trigger keyPressEvent
        import contextlib
        with contextlib.suppress(TypeError, RuntimeError):
            doc.contentsChanged.disconnect(self._on_document_changed)
        doc.contentsChanged.connect(self._on_document_changed)

        # Set initial width if provided (to match display layout)
        # Otherwise, calculate from current content
        if initial_width is not None:
            self.setTextWidth(initial_width)
        else:
            # Calculate initial width based on content
            self._update_layout()

        # Enable text interaction for cursor visibility
        self.setTextInteractionFlags(Qt.TextEditorInteraction)

        # Set cursor position
        cursor = self.textCursor()
        if select_all:
            cursor.select(QTextCursor.Document)
        else:
            cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)

        # Set focus
        self.setFocus()

        # Update visual
        self.update()

    def finish_editing(self):
        """Finish editing mode."""
        if not self._editing:
            return

        self._editing = False
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.clearFocus()

        # Emit signal
        self.editing_finished.emit()

        # Final layout update
        self._update_layout()
        self.update()

    def cancel_editing(self):
        """Cancel editing and restore cached text."""
        if not self._editing:
            return

        # Restore cached text
        self.setPlainText(self._text_cache)

        self._editing = False
        self.setTextInteractionFlags(Qt.NoTextInteraction)
        self.clearFocus()

        # Emit signal
        self.editing_cancelled.emit()

        self.update()

    def get_text(self) -> str:
        """Get current text content."""
        return self.toPlainText()

    def set_max_width(self, width: float):
        """
        Set maximum width for text wrapping.

        Args:
            width: Maximum width in pixels
        """
        self._max_width = width
        if self._editing:
            self._update_layout()

    # Event handlers

    def mousePressEvent(self, event):  # noqa: N802
        """Handle mouse press to start editing."""
        if not self._editing:
            self.start_editing(select_all=False)

        # Call base for cursor positioning
        super().mousePressEvent(event)

    def event(self, event):  # noqa: N802
        """Override event to intercept Tab key before Qt's default handling."""
        if event.type() == QEvent.KeyPress:
            key_value = event.key()

            # Intercept Tab key BEFORE Qt processes it
            if key_value == Qt.Key_Tab and self._editing:
                # Set flag on MindMapView if we have a reference
                if self._mindmap_view:
                    self._mindmap_view._add_child_after_edit = True

                # Emit tab_pressed signal to notify parent (for backward compatibility)
                self.tab_pressed.emit()
                # Finish editing to save the current text
                self.finish_editing()
                # Accept the event to prevent further processing
                event.accept()
                return True

        # Let base class handle all other events
        return super().event(event)

    def keyPressEvent(self, event):  # noqa: N802
        """Handle key press events."""
        key_value = event.key()
        if not self._editing:
            # Let base handle keys when not editing
            super().keyPressEvent(event)
            return

        # Handle special keys BEFORE letting base class process
        if key_value in (Qt.Key_Return, Qt.Key_Enter):
            # Enter to finish editing
            self.finish_editing()
            event.accept()
            return

        elif key_value == Qt.Key_Escape:
            # Escape to cancel
            self.cancel_editing()
            event.accept()
            return

        # Note: Tab is now handled in event() method above

        # For other keys, let base class handle text input
        # _on_document_changed() will handle width updates via contentsChanged signal
        super().keyPressEvent(event)

    def focusOutEvent(self, event):  # noqa: N802
        """Handle focus loss to finish editing."""
        if self._editing:
            self.finish_editing()

        super().focusOutEvent(event)

    def paint(self, painter: QPainter, option, widget):
        """
        Custom paint to optionally show border during editing.
        """
        # Call base for text rendering
        super().paint(painter, option, widget)

        # Draw border if editing and border is enabled
        if self._editing and self._border_width > 0:
            painter.save()
            pen = QPen(self._border_color, self._border_width)
            painter.setPen(pen)
            painter.setBrush(QBrush(Qt.NoBrush))
            painter.drawRoundedRect(self.boundingRect(), 6, 6)
            painter.restore()

    def boundingRect(self) -> QRectF:  # noqa: N802
        """Get bounding rectangle."""
        base_rect = super().boundingRect()

        # Add border margin if editing
        if self._editing and self._border_width > 0:
            margin = self._border_width + 2
            return base_rect.adjusted(-margin, -margin, margin, margin)

        return base_rect
