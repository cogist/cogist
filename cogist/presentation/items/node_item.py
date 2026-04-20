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

        # Set text alignment to left-top with forced wrapping
        from PySide6.QtGui import QTextOption
        doc = self.text_item.document()
        text_option = QTextOption(Qt.AlignLeft | Qt.AlignTop)
        text_option.setWrapMode(QTextOption.WrapAnywhere)  # Force wrap at any character
        doc.setDefaultTextOption(text_option)

        # Apply font based on role using new style system
        if self.style_config and self.style_config.resolved_template:
            # Use new role-based style system
            from cogist.domain.styles import NodeRole

            # Map depth to role
            role = self._depth_to_role(depth)

            # Get template style for this role
            template_style = self.style_config.resolved_template.role_styles.get(role)
            if not template_style:
                # Fallback to TERTIARY if role not found
                template_style = self.style_config.resolved_template.role_styles.get(
                    NodeRole.TERTIARY
                )

            if template_style:
                # Extract font properties from template (without colors)
                font_size = template_style.font_size
                font_weight_str = template_style.font_weight
                font_family = template_style.font_family

                # Get colors from color scheme
                color_scheme = self.style_config.resolved_color_scheme
                if color_scheme:
                    bg_color = color_scheme.node_colors.get(role, "#FFFFFF")
                    text_color = (color_scheme.text_colors.get(role) 
                                  if color_scheme.text_colors 
                                  else None) or self._auto_contrast(bg_color)
                    border_color = (color_scheme.border_colors.get(role) 
                                    if color_scheme.border_colors 
                                    else None)
                else:
                    bg_color = "#FFFFFF"
                    text_color = "#000000"
                    border_color = None

                # Store for rendering
                self.template_style = template_style
                self.bg_color = bg_color
                self.text_color = text_color
                self.border_color = border_color

                style_for_calc = template_style
            else:
                # Fallback to defaults
                font_size = 14
                font_weight_str = "Normal"
                font_family = "Arial"
                bg_color = "#FFFFFF"
                text_color = "#000000"
                border_color = None
                style_for_calc = None
        else:
            # Fallback to old NodeStyle for backward compatibility
            style = NodeStyle.get_style_for_depth(depth, is_root)
            font_size = style["font_size"]
            font_weight_str = style["font_weight"]
            font_family = "Arial"
            text_color = "#000000"
            style_for_calc = style  # Pass dict for size calculation
            self.node_style = None  # No node_style when using legacy style

        # Convert font weight string to QFont.Weight enum
        weight_map = {
            "Thin": QFont.Weight.Thin,              # 0
            "Hairline": QFont.Weight.Thin,          # 0
            "Extra Light": QFont.Weight.ExtraLight, # 12
            "ExtraLight": QFont.Weight.ExtraLight,  # 12
            "Ultra Light": QFont.Weight.ExtraLight, # 12
            "UltraLight": QFont.Weight.ExtraLight,  # 12
            "Light": QFont.Weight.Light,            # 25
            "Regular": QFont.Weight.Normal,         # 50
            "Normal": QFont.Weight.Normal,          # 50
            "Medium": QFont.Weight.Medium,          # 57
            "Semi Bold": QFont.Weight.DemiBold,     # 63
            "SemiBold": QFont.Weight.DemiBold,      # 63
            "Demi Bold": QFont.Weight.DemiBold,     # 63
            "DemiBold": QFont.Weight.DemiBold,      # 63
            "Bold": QFont.Weight.Bold,              # 70
            "Extra Bold": QFont.Weight.ExtraBold,   # 80
            "ExtraBold": QFont.Weight.ExtraBold,    # 80
            "Ultra Bold": QFont.Weight.Black,       # 87
            "UltraBold": QFont.Weight.Black,        # 87
            "Black": QFont.Weight.Black,            # 87
            "Heavy": QFont.Weight.Black,            # 87
        }
        font_weight = weight_map.get(font_weight_str, QFont.Weight.Normal)

        # Create font with family and size
        font = QFont(font_family, font_size)
        font.setWeight(font_weight)  # Use setWeight for better compatibility

        # Note: Font decorations (italic/underline/strikeout) are not yet in RoleBasedStyle
        # They can be added to the template structure in the future

        self.text_item.setFont(font)

        # Apply text color
        if isinstance(text_color, str):
            self.text_item.setDefaultTextColor(QColor(text_color))
        else:
            self.text_item.setDefaultTextColor(text_color)

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
            if style_for_calc and hasattr(style_for_calc, 'padding_w'):
                padding_left = style_for_calc.padding_w
                padding_top = style_for_calc.padding_h
            else:
                padding_left = 12
                padding_top = 8
            self.text_item.setPos(
                -width / 2 + padding_left, -height / 2 + padding_top
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
            if style_for_calc and hasattr(style_for_calc, 'padding_w'):
                padding_left = style_for_calc.padding_w
                padding_top = style_for_calc.padding_h
            else:
                padding_left = 12
                padding_top = 8
            self.text_item.setPos(
                -actual_width / 2 + padding_left, -actual_height / 2 + padding_top
            )

    def add_edge(self, edge):
        """Add a connected edge."""
        if edge not in self.connected_edges:
            self.connected_edges.append(edge)

    def add_child_item(self, child_item):
        """Add a child item to follow on move."""
        if child_item not in self.child_items:
            self.child_items.append(child_item)

    def _depth_to_role(self, depth: int):
        """Map node depth to NodeRole.

        Args:
            depth: Node depth (0 = root, 1 = first level, etc.)

        Returns:
            NodeRole for the given depth
        """
        from cogist.domain.styles import NodeRole

        role_map = {0: NodeRole.ROOT, 1: NodeRole.PRIMARY, 2: NodeRole.SECONDARY}
        return role_map.get(depth, NodeRole.TERTIARY)

    def _auto_contrast(self, bg_color: str) -> str:
        """Automatically choose text color based on background brightness.

        Args:
            bg_color: Background color in hex format (#RRGGBB)

        Returns:
            '#FFFFFF' for dark backgrounds, '#000000' for light backgrounds
        """
        # Parse hex color
        bg_color = bg_color.lstrip('#')
        if len(bg_color) != 6:
            return '#000000'

        try:
            r = int(bg_color[0:2], 16)
            g = int(bg_color[2:4], 16)
            b = int(bg_color[4:6], 16)
        except ValueError:
            return '#000000'

        # Calculate luminance
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0

        # Return white for dark backgrounds, black for light
        return '#FFFFFF' if luminance < 0.5 else '#000000'

    def update_style(self, style_config):
        """Update node style from new style_config and trigger repaint.

        Args:
            style_config: New MindMapStyle instance
        """
        self.style_config = style_config

        # Recalculate style based on new config using role-based system
        if self.style_config and self.style_config.resolved_template:
            from cogist.domain.styles import NodeRole

            # Map depth to role
            role = self._depth_to_role(self.depth)

            # Get template style
            template_style = self.style_config.resolved_template.role_styles.get(role)
            if not template_style:
                template_style = self.style_config.resolved_template.role_styles.get(
                    NodeRole.TERTIARY
                )

            if template_style:
                # Get colors from color scheme
                color_scheme = self.style_config.resolved_color_scheme
                if color_scheme:
                    bg_color = color_scheme.node_colors.get(role, "#FFFFFF")
                    text_color = color_scheme.text_colors.get(role) or self._auto_contrast(bg_color)
                    border_color = color_scheme.border_colors.get(role) if color_scheme.border_colors else None
                else:
                    bg_color = "#FFFFFF"
                    text_color = "#000000"
                    border_color = None

                # Store for rendering
                self.template_style = template_style
                self.bg_color = bg_color
                self.text_color = text_color
                self.border_color = border_color

                # Update font
                font_size = template_style.font_size
                font_weight_str = template_style.font_weight
                font_family = template_style.font_family

                # Convert font weight string to QFont.Weight enum
                weight_map = {
                    "Thin": QFont.Weight.Thin,
                    "Hairline": QFont.Weight.Thin,
                    "Extra Light": QFont.Weight.ExtraLight,
                    "ExtraLight": QFont.Weight.ExtraLight,
                    "Ultra Light": QFont.Weight.ExtraLight,
                    "UltraLight": QFont.Weight.ExtraLight,
                    "Light": QFont.Weight.Light,
                    "Regular": QFont.Weight.Normal,
                    "Normal": QFont.Weight.Normal,
                    "Medium": QFont.Weight.Medium,
                    "Semi Bold": QFont.Weight.DemiBold,
                    "SemiBold": QFont.Weight.DemiBold,
                    "Demi Bold": QFont.Weight.DemiBold,
                    "DemiBold": QFont.Weight.DemiBold,
                    "Bold": QFont.Weight.Bold,
                    "Extra Bold": QFont.Weight.ExtraBold,
                    "ExtraBold": QFont.Weight.ExtraBold,
                    "Ultra Bold": QFont.Weight.Black,
                    "UltraBold": QFont.Weight.Black,
                    "Black": QFont.Weight.Black,
                    "Heavy": QFont.Weight.Black,
                }
                font_weight = weight_map.get(font_weight_str, QFont.Weight.Normal)

                font = QFont(font_family, font_size)
                font.setWeight(font_weight)

                # Apply font decorations
                is_italic_style = "italic" in font_weight_str.lower() if font_weight_str else False

                if template_style.font_style == "Italic" and not is_italic_style:
                    font.setItalic(True)

                self.text_item.setFont(font)

                # Update text color
                if isinstance(text_color, str):
                    self.text_item.setDefaultTextColor(QColor(text_color))
                else:
                    self.text_item.setDefaultTextColor(text_color)
            else:
                # Fallback to default font
                font = QFont("Arial", 14)
                self.text_item.setFont(font)
                self.text_item.setDefaultTextColor(QColor("#000000"))
        else:
            # Fallback when no resolved template
            font = QFont("Arial", 14)
            self.text_item.setFont(font)
            self.text_item.setDefaultTextColor(QColor("#000000"))

        # Trigger repaint
        self.update()

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
        """Custom paint for node with shape support using style_config."""
        from PySide6.QtGui import QPainter

        # Use template_style if available (new architecture), otherwise fallback to legacy
        if hasattr(self, 'template_style') and self.template_style:
            # Use new role-based style system
            shape_type = self.template_style.shape.basic_shape if self.template_style.shape else "rounded_rect"
            radius = self.template_style.shape.border_radius if self.template_style.shape else 8
            bg_color = self.bg_color  # Color comes from color scheme
            border_color = self.border_color  # Border color from color scheme or None
            border_width = self.template_style.border.border_width if self.template_style.border else 2
            border_style = self.template_style.border.border_style if self.template_style.border else "solid"
        else:
            # Fallback to old NodeStyle
            style = NodeStyle.get_style_for_depth(self.depth, self.is_root)
            shape_type = "rounded_rect"
            radius = style["border_radius"]
            bg_color = self.color
            border_color = None
            border_width = 0
            border_style = "solid"

        rect = self.rect()

        # Create path based on shape
        path = QPainterPath()
        if shape_type == "circle":
            # Draw circle/ellipse
            path.addEllipse(rect)
        elif shape_type == "rect":
            # Draw rectangle (no radius)
            path.addRect(rect)
        else:  # rounded_rect (default)
            # Draw rounded rectangle
            path.addRoundedRect(
                rect.x(),
                rect.y(),
                rect.width(),
                rect.height(),
                radius,
                radius,
            )

        # Draw selection highlight if selected
        if self.isSelected():
            highlight_path = QPainterPath()
            if shape_type == "circle":
                # Ellipse highlight with offset
                highlight_rect = rect.adjusted(-3, -3, 3, 3)
                highlight_path.addEllipse(highlight_rect)
            elif shape_type == "rect":
                # Rectangle highlight with offset
                highlight_rect = rect.adjusted(-3, -3, 3, 3)
                highlight_path.addRect(highlight_rect)
            else:  # rounded_rect
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

        # Check if this node should have no background (depth >= 3 or explicit flag)
        # For now, always draw background in new architecture
        has_background = True

        if not has_background:
            # No background fill, no border - just text
            painter.setPen(Qt.NoPen)
            painter.setBrush(Qt.NoBrush)
        else:
            # Apply background color
            bg_qcolor = QColor(bg_color) if isinstance(bg_color, str) else bg_color

            # Create gradient or solid color
            # For now, just use solid color (gradient can be added later)
            painter.setBrush(QBrush(bg_qcolor))

            # Apply border if specified
            if border_width > 0 and border_color:
                if isinstance(border_color, str):
                    border_qcolor = QColor(border_color)
                else:
                    border_qcolor = border_color

                pen = QPen(border_qcolor, border_width)

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
            else:
                painter.setPen(Qt.NoPen)

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
        # Support RoleBasedStyle, NodeStyleConfig, and dict
        if hasattr(style, 'padding_w'):
            # It's a RoleBasedStyle object (new architecture)
            max_text_width = getattr(style, 'max_text_width', 250.0)  # Default to 250
            padding_width = style.padding_w * 2  # padding_w is single-side, need both sides
            padding_height = style.padding_h * 2  # padding_h is single-side, need top+bottom
        elif hasattr(style, "max_text_width"):
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
        # Use template_style if available (new architecture), otherwise fallback to legacy
        if hasattr(self, 'template_style') and self.template_style:
            # Use new role-based style system
            style_for_calc = self.template_style
            padding_left = style_for_calc.padding_w
            padding_top = style_for_calc.padding_h
        else:
            # Fallback to old NodeStyle for backward compatibility
            style_for_calc = NodeStyle.get_style_for_depth(self.depth, self.is_root)
            padding_left = style_for_calc["padding_width"]
            padding_top = style_for_calc["padding_height"]

        # Calculate new size
        actual_width, actual_height, text_rect = self._calculate_node_size(text, style_for_calc)

        # Update node dimensions
        self.node_width = actual_width
        self.node_height = actual_height
        self.setRect(-actual_width / 2, -actual_height / 2, actual_width, actual_height)

        # Position text at top-left with padding
        self.text_item.setPos(
            -actual_width / 2 + padding_left, -actual_height / 2 + padding_top
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
        if hasattr(self, 'template_style') and self.template_style:
            padding_left = self.template_style.padding_w
            padding_top = self.template_style.padding_h
        else:
            style = NodeStyle.get_style_for_depth(self.depth, self.is_root)
            padding_left = style["padding_width"]
            padding_top = style["padding_height"]
        self.edit_widget.setPos(
            -self.node_width / 2 + padding_left,
            -self.node_height / 2 + padding_top
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
            if hasattr(self, 'template_style') and self.template_style:
                padding_width = self.template_style.padding_w * 2  # Both sides
                padding_height = self.template_style.padding_h * 2
            else:
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
