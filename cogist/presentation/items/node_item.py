"""
Node Item - Presentation Layer

QGraphicsItem wrapper for domain Node entity.
Handles all UI rendering and user interaction.
"""

import contextlib

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QBrush, QColor, QFont, QLinearGradient, QPainterPath, QPen
from PySide6.QtWidgets import (
    QGraphicsRectItem,
    QGraphicsTextItem,
)

from cogist.domain.styles.style_config import MAX_TEXT_WIDTH
from cogist.presentation.items.editable_text_item import EditableTextItem


class NodeStyle:
    """
    Unified node style configuration based on depth.

    Centralized style management to ensure consistency across all nodes.
    """

    @staticmethod
    def get_style_for_depth(depth: int, is_root: bool = False) -> dict:
        """
        Get complete style configuration for a node based on its depth.

        Args:
            depth: Node depth in tree (0 for root)
            is_root: Whether this is the root node

        Returns:
            Dictionary containing all style parameters
        """
        if is_root or depth == 0:
            return {
                "font_size": 22,
                "font_weight": QFont.Bold,
                "max_text_width": MAX_TEXT_WIDTH,
                "padding_width": 20,
                "padding_height": 16,
                "border_radius": 10,
            }
        elif depth == 1:
            return {
                "font_size": 18,
                "font_weight": QFont.Bold,
                "max_text_width": MAX_TEXT_WIDTH,
                "padding_width": 20,
                "padding_height": 16,
                "border_radius": 8,
            }
        elif depth == 2:
            return {
                "font_size": 16,
                "font_weight": QFont.Normal,
                "max_text_width": MAX_TEXT_WIDTH,
                "padding_width": 8,
                "padding_height": 6,
                "border_radius": 6,
            }
        else:
            # Depth >= 3: minimal style, no background
            return {
                "font_size": 14,
                "font_weight": QFont.Normal,
                "max_text_width": MAX_TEXT_WIDTH,
                "padding_width": 6,
                "padding_height": 4,
                "border_radius": 4,
                "no_background": True,  # Flag to indicate no background fill
            }


class NodeItem(QGraphicsRectItem):
    """
    Visual representation of a mind map node.

    This is the presentation layer item that wraps a domain Node entity.
    All visual styling and user interaction happens here.
    """

    def __init__(
        self,
        text: str = "",
        width: float = None,  # Must be provided - no default
        height: float = None,  # Must be provided - no default
        color: str = "#2196F3",
        is_root: bool = False,
        depth: int = 0,
        use_domain_size: bool = False,
        style_config=None,  # MindMapStyle instance for unified styling
    ):
        # Initialize with placeholder rect, actual rect set after size calculation
        super().__init__()

        # Visual properties
        self.text_content = text
        self.node_width = width
        self.node_height = height
        self.color = QColor(color)
        self.is_root = is_root
        self.depth = depth
        self.style_config = style_config  # Store style configuration

        # Connected edges (will be updated by layout)
        self.connected_edges = []

        # Child items for following parent movement
        self.child_items = []

        # Track last position for offset calculation
        self._last_pos = QPointF(0, 0)

        # Set flags
        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)  # Enable selection
        self.setAcceptHoverEvents(True)

        # Z-value: nodes above edges
        self.setZValue(1)

        # Inline editing support
        self.edit_widget = None
        self.edit_proxy = None
        self.edit_callback = None  # Store callback for manual finish_editing calls

        # Text item with word wrap and auto-sizing
        self.text_item = QGraphicsTextItem(text, self)
        self.text_item.setDefaultTextColor(Qt.black)  # Black text for better visibility

        # Set text alignment to left-top with forced wrapping
        from PySide6.QtGui import QTextOption
        doc = self.text_item.document()
        text_option = QTextOption(Qt.AlignLeft | Qt.AlignTop)
        text_option.setWrapMode(QTextOption.WrapAnywhere)  # Force wrap at any character
        doc.setDefaultTextOption(text_option)

        # Apply font based on depth using unified style system
        if self.style_config:
            # Use new MindMapStyle system (default priority: Normal)
            from cogist.domain.styles import PriorityLevel

            node_style = self.style_config.resolve_node_style(
                depth, PriorityLevel.LEVEL_1
            )
            font_size = node_style.font_size
            font_weight_str = node_style.font_weight
            style_for_calc = (
                node_style  # Pass full NodeStyleConfig for size calculation
            )
        else:
            # Fallback to old NodeStyle for backward compatibility
            style = NodeStyle.get_style_for_depth(depth, is_root)
            font_size = style["font_size"]
            font_weight_str = style["font_weight"]
            style_for_calc = style  # Pass dict for size calculation

        # Convert font weight string to QFont constant
        font_weight = QFont.Bold if font_weight_str == "Bold" else QFont.Normal
        font = QFont("Arial", font_size, font_weight)
        self.text_item.setFont(font)

        if use_domain_size:
            # Use domain layer's pre-measured size (layout already calculated it)
            # DO NOT recalculate - just use the domain dimensions directly
            self.node_width = width
            self.node_height = height
            self.setRect(-width / 2, -height / 2, width, height)

            # Still need to position text within the node
            # Calculate text size for proper positioning only
            actual_width, actual_height, text_rect = self._calculate_node_size(
                text, style_for_calc
            )
            # Position text at top-left with padding
            padding_width = (
                style_for_calc.padding_width
                if hasattr(style_for_calc, "padding_width")
                else style_for_calc["padding_width"]
            )
            padding_height = (
                style_for_calc.padding_height
                if hasattr(style_for_calc, "padding_height")
                else style_for_calc["padding_height"]
            )
            self.text_item.setPos(
                -width / 2 + padding_width / 2, -height / 2 + padding_height / 2
            )
        else:
            # Measure and auto-size using unified method
            actual_width, actual_height, text_rect = self._calculate_node_size(
                text, style_for_calc
            )
            # Update node dimensions
            self.node_width = actual_width
            self.node_height = actual_height
            self.setRect(
                -actual_width / 2, -actual_height / 2, actual_width, actual_height
            )
            # Position text at top-left with padding
            padding_width = (
                style_for_calc.padding_width
                if hasattr(style_for_calc, "padding_width")
                else style_for_calc["padding_width"]
            )
            padding_height = (
                style_for_calc.padding_height
                if hasattr(style_for_calc, "padding_height")
                else style_for_calc["padding_height"]
            )
            self.text_item.setPos(
                -actual_width / 2 + padding_width / 2, -actual_height / 2 + padding_height / 2
            )

    def add_edge(self, edge):
        """Add a connected edge."""
        if edge not in self.connected_edges:
            self.connected_edges.append(edge)

    def add_child_item(self, child_item):
        """Add a child item to follow on move."""
        if child_item not in self.child_items:
            self.child_items.append(child_item)

    def itemChange(self, change, value):  # noqa: N802
        """Handle position changes - update edges and children."""
        if change == QGraphicsRectItem.ItemPositionHasChanged:
            new_pos = value
            offset = new_pos - self._last_pos

            # Move all children with same offset (they are being dragged along)
            for child_item in self.child_items:
                child_item.setPos(child_item.pos() + offset)

            # Update last position
            self._last_pos = new_pos

            # Update all connected edges (both incoming from parent and outgoing to children)
            for edge in self.connected_edges:
                edge.update_curve()

        return super().itemChange(change, value)

    def paint(self, painter, option, widget=None):  # noqa: ARG002
        """Custom paint for rounded rectangle with gradient."""
        from PySide6.QtGui import QPainter

        # Get border radius from style
        style = NodeStyle.get_style_for_depth(self.depth, self.is_root)
        radius = style["border_radius"]

        # CRITICAL: Use actual rect() from setRect() instead of hardcoded centered position
        # This ensures paint matches the directional expansion logic in on_width_changed
        rect = self.rect()
        path = QPainterPath()
        path.addRoundedRect(
            rect.x(),
            rect.y(),
            rect.width(),
            rect.height(),
            radius,
            radius,
        )

        # Gradient fill
        gradient = QLinearGradient(
            rect.x(),
            rect.y(),
            rect.x(),
            rect.y() + rect.height(),
        )

        if self.is_root:
            gradient.setColorAt(0, self.color.lighter(120))
            gradient.setColorAt(1, self.color)
        else:
            gradient.setColorAt(0, self.color.lighter(110))
            gradient.setColorAt(1, self.color)

        # Draw selection highlight if selected
        if self.isSelected():
            # Draw selection highlight (brighter border)
            highlight_path = QPainterPath()
            highlight_path.addRoundedRect(
                rect.x() - 3,
                rect.y() - 3,
                rect.width() + 6,
                rect.height() + 6,
                radius + 2,
                radius + 2,
            )
            painter.setPen(QPen(QColor("#FFD700"), 3))  # Gold border
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(highlight_path)

        painter.setRenderHint(QPainter.Antialiasing, True)

        # Check if this node should have no background (depth >= 3)
        if style.get("no_background", False):
            # No background fill, no border - just text
            painter.setPen(Qt.NoPen)
            painter.setBrush(Qt.NoBrush)
        else:
            # Gradient fill for nodes with background
            gradient = QLinearGradient(
                rect.x(),
                rect.y(),
                rect.x(),
                rect.y() + rect.height(),
            )

            if self.is_root:
                gradient.setColorAt(0, self.color.lighter(120))
                gradient.setColorAt(1, self.color)
            else:
                gradient.setColorAt(0, self.color.lighter(110))
                gradient.setColorAt(1, self.color)

            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)  # Remove border

        painter.drawPath(path)

    def get_text(self) -> str:
        """Get node text."""
        return self.text_content

    def _calculate_node_size(self, text: str, style) -> tuple[float, float, object]:
        """
        Unified method to calculate node size based on text content and style.

        This method ensures consistent size calculation across all scenarios:
        - Initial node creation
        - Text editing
        - Dynamic resizing

        Args:
            text: The text content
            style: Style dictionary from NodeStyle.get_style_for_depth() or NodeStyleConfig object

        Returns:
            Tuple of (actual_width, actual_height, text_rect)
        """
        # Support both dict and NodeStyleConfig
        if hasattr(style, "max_text_width"):
            # It's a NodeStyleConfig object
            max_text_width = style.max_text_width
            padding_width = style.padding_width
            padding_height = style.padding_height
        else:
            # It's a dict (backward compatibility)
            max_text_width = style["max_text_width"]
            padding_width = style["padding_width"]
            padding_height = style["padding_height"]

        # Ensure wrap mode is set to WrapAnywhere for forced wrapping
        from PySide6.QtGui import QTextOption
        doc = self.text_item.document()
        text_option = doc.defaultTextOption()
        text_option.setWrapMode(QTextOption.WrapAnywhere)
        doc.setDefaultTextOption(text_option)

        # First, measure text width without wrapping
        self.text_item.setTextWidth(-1)  # -1 means no wrap
        self.text_item.setPlainText(text)
        text_rect_no_wrap = self.text_item.boundingRect()
        text_width_no_wrap = text_rect_no_wrap.width()

        # If text exceeds max width, enable word wrap
        if text_width_no_wrap > max_text_width:
            self.text_item.setTextWidth(max_text_width)
            text_rect = self.text_item.boundingRect()
        else:
            # Use natural width (no wrapping needed)
            text_rect = text_rect_no_wrap

        # Calculate actual size with padding from style
        actual_width = min(
            text_rect.width() + padding_width,
            max_text_width + padding_width,
        )
        actual_height = text_rect.height() + padding_height

        return actual_width, actual_height, text_rect

    def _update_node_geometry(self, text: str):
        """
        Unified method to update node geometry (size and text position).

        This method recalculates node size and repositions text.

        Args:
            text: New text content
        """
        # Get style for current depth
        style = NodeStyle.get_style_for_depth(self.depth, self.is_root)

        # Calculate new size
        actual_width, actual_height, text_rect = self._calculate_node_size(text, style)

        # Update node dimensions
        self.node_width = actual_width
        self.node_height = actual_height
        self.setRect(-actual_width / 2, -actual_height / 2, actual_width, actual_height)

        # Center text vertically
        self.text_item.setPos(
            -text_rect.width() / 2, -actual_height / 2 + style["padding_height"] / 2
        )

    def set_text(self, text: str):
        """Set node text and re-measure dimensions with word wrap."""
        self.text_content = text

        # Use unified geometry update method
        self._update_node_geometry(text)

    def start_editing(self, on_edit_callback=None, cursor_position: int = -1, mindmap_view=None):
        """Start inline editing with EditableTextItem.

        Args:
            on_edit_callback: Callback when editing finishes
            cursor_position: Cursor position in text (-1 for select all)
            mindmap_view: Reference to MindMapView for Tab key handling
        """
        if self.edit_widget is not None:
            return  # Already editing

        # Create editable text item with proper Tab key handling
        self.edit_widget = EditableTextItem(
            text=self.text_content,
            max_width=MAX_TEXT_WIDTH,  # Use global constant for max text width
            mindmap_view=mindmap_view,  # Pass MindMapView reference
        )

        # Match the text item's font exactly
        font = self.text_item.font()
        self.edit_widget.setFont(font)
        self.edit_widget.setDefaultTextColor(Qt.black)

        # Add to scene as child item (not via proxy widget)
        self.edit_widget.setParentItem(self)

        # Position to match text item exactly (top-left with padding)
        # Get style to calculate padding
        style = NodeStyle.get_style_for_depth(self.depth, self.is_root)
        padding_width = style["padding_width"]
        padding_height = style["padding_height"]
        self.edit_widget.setPos(
            -self.node_width / 2 + padding_width / 2,
            -self.node_height / 2 + padding_height / 2
        )

        # Hide text item during editing
        self.text_item.setVisible(False)

        # Store callback for manual finish_editing calls
        self.edit_callback = on_edit_callback

        # Connect signals
        def on_width_changed(new_width):
            """Handle width changes during editing - update node background size.

            CRITICAL: For non-root nodes, maintain fixed edge position relative to parent:
            - Right branch (x > 0): Expand/shrink only on the right side (left edge fixed)
            - Left branch (x < 0): Expand/shrink only on the left side (right edge fixed)
            - Root node (depth == 0): Keep centered expansion (both sides)
            """
            if self.edit_widget is None:
                return

            # Get style to calculate padding
            style = NodeStyle.get_style_for_depth(self.depth, self.is_root)
            padding_width = style["padding_width"]
            padding_height = style["padding_height"]

            # Calculate new node dimensions
            new_node_width = new_width + padding_width

            # Get height from document
            doc = self.edit_widget.document()
            doc_size = doc.size()
            new_node_height = doc_size.height() + padding_height

            # Determine expansion direction based on node position
            current_x = self.pos().x()
            is_right_branch = current_x >= 0  # Right side of parent (or root)

            # CRITICAL: Capture current rect dimensions BEFORE any updates
            old_rect = self.rect()
            old_left = old_rect.left()
            old_right = old_rect.right()

            # Update node dimensions
            self.node_width = new_node_width
            self.node_height = new_node_height

            if self.depth == 0 or self.is_root:
                # Root node: centered expansion (both sides)
                self.setRect(
                    -new_node_width / 2,
                    -new_node_height / 2,
                    new_node_width,
                    new_node_height
                )
            else:
                # Non-root nodes: directional expansion to maintain parent edge
                if is_right_branch:
                    # Right branch: LEFT edge stays fixed in scene coordinates
                    # Old left edge (scene) = pos.x + old_left
                    # New left edge (local) should result in same scene position
                    # new_left = old_left (keep same local left)
                    new_rect_left = old_left
                    new_rect_top = -new_node_height / 2
                    self.setRect(
                        new_rect_left,
                        new_rect_top,
                        new_node_width,
                        new_node_height
                    )
                else:
                    # Left branch: RIGHT edge stays fixed in scene coordinates
                    # Old right edge (scene) = pos.x + old_right
                    # New right edge (local) should result in same scene position
                    # new_right = old_right, so new_left = old_right - new_width
                    new_rect_right = old_right
                    new_rect_left = new_rect_right - new_node_width
                    new_rect_top = -new_node_height / 2
                    self.setRect(
                        new_rect_left,
                        new_rect_top,
                        new_node_width,
                        new_node_height
                    )

            # Update edit widget position (relative to new rect with padding)
            # Get the new rect's left and top
            rect = self.rect()
            self.edit_widget.setPos(
                rect.left() + padding_width / 2,
                rect.top() + padding_height / 2
            )

            # CRITICAL: Force full repaint after rect change
            # This ensures the background updates immediately during editing
            self.update()

            # Update all connected edges
            for edge in self.connected_edges:
                edge.update_curve()

        def on_text_changed(new_text):
            """Handle text changes during editing."""
            pass  # Width change handler will take care of everything

        def on_tab_pressed():
            """Handle Tab key press - set flag to add child after editing."""
            # This is now handled directly in EditableTextItem.event()
            # Keeping this for backward compatibility
            pass

        def on_editing_finished():
            """Handle editing finished."""
            self.finish_editing(on_edit_callback)

        self.edit_widget.width_changed.connect(on_width_changed)
        self.edit_widget.text_changed.connect(on_text_changed)
        self.edit_widget.tab_pressed.connect(on_tab_pressed)
        self.edit_widget.editing_finished.connect(on_editing_finished)

        # Start editing mode
        select_all = (cursor_position < 0)
        self.edit_widget.start_editing(select_all=select_all)

    def finish_editing(self, on_edit_callback=None):
        """Finish inline editing."""
        if self.edit_widget is None:
            return

        # Get new text before cleaning up
        new_text = self.edit_widget.get_text().strip()

        # Don't allow empty text
        if not new_text:
            new_text = self.text_content

        # Disconnect signals to prevent re-entry
        with contextlib.suppress(TypeError, RuntimeError):
            self.edit_widget.text_changed.disconnect()
            self.edit_widget.tab_pressed.disconnect()
            self.edit_widget.editing_finished.disconnect()

        # Clear focus from edit widget
        self.edit_widget.clearFocus()

        # Remove edit widget from scene
        scene = self.scene()
        if scene and self.edit_widget:
            scene.removeItem(self.edit_widget)

        # Clear references
        self.edit_widget = None

        # Show text item again
        self.text_item.setVisible(True)

        # Update text if changed
        if new_text != self.text_content:
            # CRITICAL: Update text and geometry FIRST, before calling callback
            # This ensures UI dimensions are fully updated before layout refresh
            self.set_text(new_text)

            # Call the callback to update domain and layout
            # Use provided callback or fall back to stored edit_callback
            callback = on_edit_callback or self.edit_callback
            if callback:
                callback(new_text)

    def cancel_editing(self):
        """Cancel editing and discard changes."""
        if self.edit_widget is None:
            return

        # Disconnect signals to prevent re-entry
        with contextlib.suppress(TypeError, RuntimeError):
            self.edit_widget.text_changed.disconnect()
            self.edit_widget.tab_pressed.disconnect()
            self.edit_widget.editing_finished.disconnect()

        # Clear focus from edit widget
        self.edit_widget.clearFocus()

        # Remove edit widget from scene
        scene = self.scene()
        if scene and self.edit_widget:
            scene.removeItem(self.edit_widget)

        # Clear references
        self.edit_widget = None

        # Show text item again (text remains unchanged)
        self.text_item.setVisible(True)
