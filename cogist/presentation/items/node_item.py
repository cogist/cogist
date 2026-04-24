"""
Node Item - Presentation Layer

QGraphicsItem wrapper for domain Node entity.
Handles all UI rendering and user interaction.
"""

import contextlib

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QFont, QPen
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
                "padding_width": 16,  # Match RoleBasedStyle PRIMARY
                "padding_height": 12,
                "border_radius": 8,
            }
        elif depth == 2:
            return {
                "font_size": 16,
                "font_weight": QFont.Normal,
                "max_text_width": MAX_TEXT_WIDTH,
                "padding_width": 12,  # Match RoleBasedStyle SECONDARY
                "padding_height": 10,
                "border_radius": 6,
            }
        else:
            # Depth >= 3: minimal style, no background
            return {
                "font_size": 14,
                "font_weight": QFont.Normal,
                "max_text_width": MAX_TEXT_WIDTH,
                "padding_width": 10,  # Match RoleBasedStyle TERTIARY
                "padding_height": 8,
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
        self.is_right_side = True  # Default: right side of root (will be set by main.py)

        # Connected edges (will be updated by layout)
        self.connected_edges = []

        # Child items for following parent movement
        self.child_items = []

        # Track last position for offset calculation
        self._last_pos = QPointF(0, 0)

        # Set flags
        # Disable ItemIsMovable - we handle drag manually for smart subtree dragging
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)
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
        doc.setDocumentMargin(0)  # Remove default document margin
        text_option = QTextOption(Qt.AlignLeft | Qt.AlignTop)
        text_option.setWrapMode(QTextOption.WrapAnywhere)  # Force wrap at any character
        doc.setDefaultTextOption(text_option)

        # Apply font based on role using new style system
        # style_config is always set (from create_default_template or update_style)
        assert self.style_config is not None, "style_config must be set"


        # Map depth to role
        role = self._depth_to_role(depth)

        # CRITICAL: Get template style for this role - must exist in template
        # No fallback allowed - all roles must be defined in the template
        template_style = self.style_config.resolved_template.role_styles[role]

        # Extract font properties from template (without colors)
        font_size = template_style.font_size
        font_weight_str = template_style.font_weight
        font_family = template_style.font_family

        # Get colors from color scheme
        color_scheme = self.style_config.resolved_color_scheme
        if color_scheme:
            # node_colors is required and contains all roles
            bg_color = color_scheme.node_colors[role]

            # text_colors is optional - auto contrast if not provided
            if color_scheme.text_colors and role in color_scheme.text_colors:
                text_color = color_scheme.text_colors[role]
            else:
                text_color = self._auto_contrast(bg_color)

            # border_colors is optional - None if not provided
            if color_scheme.border_colors and role in color_scheme.border_colors:
                border_color = color_scheme.border_colors[role]
            else:
                border_color = None
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

        # Convert font weight string to QFont.Weight enum
        weight_map = {
            "Thin": QFont.Weight.Thin,  # 0
            "Hairline": QFont.Weight.Thin,  # 0
            "Extra Light": QFont.Weight.ExtraLight,  # 12
            "ExtraLight": QFont.Weight.ExtraLight,  # 12
            "Ultra Light": QFont.Weight.ExtraLight,  # 12
            "UltraLight": QFont.Weight.ExtraLight,  # 12
            "Light": QFont.Weight.Light,  # 25
            "Regular": QFont.Weight.Normal,  # 50
            "Normal": QFont.Weight.Normal,  # 50
            "Medium": QFont.Weight.Medium,  # 57
            "Semi Bold": QFont.Weight.DemiBold,  # 63
            "SemiBold": QFont.Weight.DemiBold,  # 63
            "Demi Bold": QFont.Weight.DemiBold,  # 63
            "DemiBold": QFont.Weight.DemiBold,  # 63
            "Bold": QFont.Weight.Bold,  # 70
            "Extra Bold": QFont.Weight.ExtraBold,  # 80
            "ExtraBold": QFont.Weight.ExtraBold,  # 80
            "Ultra Bold": QFont.Weight.Black,  # 87
            "UltraBold": QFont.Weight.Black,  # 87
            "Black": QFont.Weight.Black,  # 87
            "Heavy": QFont.Weight.Black,  # 87
        }
        font_weight = weight_map.get(font_weight_str, QFont.Weight.Normal)

        # Create font with family and size
        font = QFont(font_family, font_size)
        font.setWeight(font_weight)  # Use setWeight for better compatibility

        # Apply font decorations from template_style
        if (
            hasattr(template_style, "font_style")
            and template_style.font_style == "Italic"
        ):
            font.setItalic(True)
        if hasattr(template_style, "font_underline") and template_style.font_underline:
            font.setUnderline(True)
        if hasattr(template_style, "font_strikeout") and template_style.font_strikeout:
            font.setStrikeOut(True)

        self.text_item.setFont(font)

        # Apply text color
        if isinstance(text_color, str):
            self.text_item.setDefaultTextColor(QColor(text_color))
        else:
            self.text_item.setDefaultTextColor(text_color)

        # Apply font shadow effect if enabled
        self._apply_font_shadow()

        if use_domain_size:
            # Use domain layer's pre-measured size as INITIAL size
            # But still recalculate based on current style to ensure padding is correct
            actual_width, actual_height, text_rect = self._calculate_node_size(
                text, style_for_calc
            )

            # Use calculated size (text-based auto-sizing)
            self.node_width = actual_width
            self.node_height = actual_height
            self.setRect(
                -self.node_width / 2,
                -self.node_height / 2,
                self.node_width,
                self.node_height,
            )

            # Position text with padding and vertical centering
            # CRITICAL: Always use template_style if available, never use hardcoded defaults
            if hasattr(self, "template_style") and self.template_style:
                padding_left = self.template_style.padding_w
                padding_top = self.template_style.padding_h
            elif style_for_calc and hasattr(style_for_calc, "padding_w"):
                padding_left = style_for_calc.padding_w
                padding_top = style_for_calc.padding_h
            else:
                # Fallback to NodeStyle.get_style_for_depth() for consistency
                fallback_style = NodeStyle.get_style_for_depth(self.depth, self.is_root)
                padding_left = fallback_style["padding_width"]
                padding_top = fallback_style["padding_height"]

            # Calculate text position: left padding + vertical centering
            text_x = -self.node_width / 2 + padding_left
            text_y = (
                -self.node_height / 2
                + padding_top
                + (self.node_height - text_rect.height() - padding_top * 2) / 2
            )
            self.text_item.setPos(text_x, text_y)
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
            # Position text with padding and vertical centering
            # CRITICAL: Always use template_style if available, never use hardcoded defaults
            if hasattr(self, "template_style") and self.template_style:
                padding_left = self.template_style.padding_w
                padding_top = self.template_style.padding_h
            elif style_for_calc and hasattr(style_for_calc, "padding_w"):
                padding_left = style_for_calc.padding_w
                padding_top = style_for_calc.padding_h
            else:
                # Fallback to NodeStyle.get_style_for_depth() for consistency
                fallback_style = NodeStyle.get_style_for_depth(self.depth, self.is_root)
                padding_left = fallback_style["padding_width"]
                padding_top = fallback_style["padding_height"]

            # Calculate text position: left padding + vertical centering
            text_x = -actual_width / 2 + padding_left
            text_y = (
                -actual_height / 2
                + padding_top
                + (actual_height - text_rect.height() - padding_top * 2) / 2
            )
            self.text_item.setPos(text_x, text_y)

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
        bg_color = bg_color.lstrip("#")
        if len(bg_color) != 6:
            return "#000000"

        try:
            r = int(bg_color[0:2], 16)
            g = int(bg_color[2:4], 16)
            b = int(bg_color[4:6], 16)
        except ValueError:
            return "#000000"

        # Calculate luminance
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0

        # Return white for dark backgrounds, black for light
        return "#FFFFFF" if luminance < 0.5 else "#000000"

    def _apply_font_shadow(self):
        """Apply font shadow effect to text_item based on template_style.

        This method is called in __init__ and update_style to ensure shadow
        effect is always in sync with the current style configuration.
        """
        from PySide6.QtWidgets import QGraphicsDropShadowEffect

        if not hasattr(self.template_style, "shadow_enabled"):
            return

        if self.template_style.shadow_enabled:
            # Get existing effect or create new one
            shadow_effect = self.text_item.graphicsEffect()

            if not isinstance(shadow_effect, QGraphicsDropShadowEffect):
                shadow_effect = QGraphicsDropShadowEffect()
                self.text_item.setGraphicsEffect(shadow_effect)

            # Update shadow parameters
            shadow_effect.setOffset(
                self.template_style.shadow_offset_x, self.template_style.shadow_offset_y
            )
            shadow_effect.setBlurRadius(self.template_style.shadow_blur)

            # Update shadow color
            shadow_color_str = self.template_style.shadow_color or "#000000"
            if isinstance(shadow_color_str, str):
                shadow_qcolor = QColor(shadow_color_str)
            else:
                shadow_qcolor = shadow_color_str

            # Set semi-transparent (50% opacity)
            shadow_qcolor.setAlpha(128)
            shadow_effect.setColor(shadow_qcolor)
        else:
            # Remove shadow effect if disabled
            self.text_item.setGraphicsEffect(None)

    def update_style(self, style_config):
        """Update node style from new style_config and trigger repaint.

        Args:
            style_config: New MindMapStyle instance
        """
        self.style_config = style_config

        # Recalculate style based on new config using role-based system
        if self.style_config and self.style_config.resolved_template:

            # Map depth to role
            role = self._depth_to_role(self.depth)

            # CRITICAL: Get template style for this role - must exist in template
            # No fallback allowed - all roles must be defined in the template
            template_style = self.style_config.resolved_template.role_styles[role]

            if template_style:
                # Get colors from color scheme
                color_scheme = self.style_config.resolved_color_scheme
                if color_scheme:
                    # node_colors is required and contains all roles
                    bg_color = color_scheme.node_colors[role]

                    # text_colors is optional - auto contrast if not provided
                    if color_scheme.text_colors and role in color_scheme.text_colors:
                        text_color = color_scheme.text_colors[role]
                    else:
                        text_color = self._auto_contrast(bg_color)

                    # border_colors is optional - None if not provided
                    if color_scheme.border_colors and role in color_scheme.border_colors:
                        border_color = color_scheme.border_colors[role]
                    else:
                        border_color = None
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
                is_italic_style = (
                    "italic" in font_weight_str.lower() if font_weight_str else False
                )

                if template_style.font_style == "Italic" and not is_italic_style:
                    font.setItalic(True)

                self.text_item.setFont(font)

                # Update text color
                if isinstance(text_color, str):
                    self.text_item.setDefaultTextColor(QColor(text_color))
                else:
                    self.text_item.setDefaultTextColor(text_color)

                # Apply font shadow effect
                self._apply_font_shadow()
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

        # CRITICAL: Recalculate node geometry when style changes (padding, font size, etc.)
        # This ensures node size is updated to match new padding values
        self._update_node_geometry(self.text_content)

        # Trigger repaint
        self.update()

    def itemChange(self, change, value):
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

    def paint(self, painter, option, widget=None):
        """Custom paint using border strategy pattern."""
        from PySide6.QtGui import QPainter

        from cogist.domain.borders.registry import BorderStrategyRegistry

        painter.setRenderHint(QPainter.Antialiasing, True)

        shape_type = self.template_style.shape.basic_shape
        rect = self.rect()

        # Map depth to role
        role = self._depth_to_role(self.depth)

        # Read colors directly from global style_config (no caching)
        if self.style_config and self.style_config.resolved_color_scheme:
            color_scheme = self.style_config.resolved_color_scheme
            bg_color = color_scheme.node_colors[role]
            border_color = (
                color_scheme.border_colors[role]
                if color_scheme.border_colors and role in color_scheme.border_colors
                else None
            )
        else:
            bg_color = "#FFFFFF"
            border_color = None

        # Build style config dict for strategy
        style_config = {
            "bg_color": bg_color,
            "border_color": border_color,
            "border_width": self.template_style.border.border_width,
            "border_radius": self.template_style.shape.border_radius,
            "border_style": self.template_style.border.border_style,
            "padding_w": self.template_style.padding_w,
            "padding_h": self.template_style.padding_h,
            "is_right_side": self.is_right_side,  # For adaptive decorative lines
        }

        # Get and execute border strategy
        try:
            strategy = BorderStrategyRegistry.get_strategy(shape_type)
        except ValueError:
            # Fallback to default rounded rect
            strategy = BorderStrategyRegistry.get_strategy("rounded_rect")

        # Draw selection highlight first (if selected)
        if self.isSelected():
            highlight_path = strategy.get_selection_path(rect, style_config)
            painter.setPen(QPen(QColor("#FFD700"), 3))  # Gold border
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(highlight_path)

        # Draw node shape/border
        strategy.draw(painter, rect, style_config)

    def get_text(self) -> str:
        """Get node text."""
        return self.text_content

    def _calculate_node_size(self, text: str, style=None) -> tuple[float, float, object]:
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
        # CRITICAL: Use template_style from instance if available (new architecture)
        if hasattr(self, "template_style") and self.template_style:
            style = self.template_style
        elif style is None:
            # Fallback to legacy NodeStyle if no style provided
            style = NodeStyle.get_style_for_depth(self.depth, self.is_root)

        # Support RoleBasedStyle, NodeStyleConfig, and dict
        if hasattr(style, "padding_w"):
            # It's a RoleBasedStyle object (new architecture)
            # CRITICAL: Always read from style object, never use hardcoded defaults
            max_text_width = style.max_text_width
            padding_width = (
                style.padding_w * 2
            )  # padding_w is single-side, need both sides
            padding_height = (
                style.padding_h * 2
            )  # padding_h is single-side, need top+bottom
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

        # Ensure wrap mode is set based on max_text_width
        from PySide6.QtGui import QTextOption

        doc = self.text_item.document()
        text_option = doc.defaultTextOption()

        # CRITICAL: max_text_width=0 means unlimited width (no wrapping)
        if max_text_width > 0:
            text_option.setWrapMode(QTextOption.WrapAnywhere)
        else:
            text_option.setWrapMode(QTextOption.NoWrap)

        doc.setDefaultTextOption(text_option)

        # First, measure text width without wrapping
        self.text_item.setTextWidth(-1)  # -1 means no wrap
        self.text_item.setPlainText(text)
        text_rect_no_wrap = self.text_item.boundingRect()
        text_width_no_wrap = text_rect_no_wrap.width()

        # If max_text_width is 0, use natural width (unlimited)
        # Otherwise, wrap if text exceeds max width
        if max_text_width > 0 and text_width_no_wrap > max_text_width:
            self.text_item.setTextWidth(max_text_width)
            text_rect = self.text_item.boundingRect()
        else:
            # Use natural width (no wrapping needed or unlimited)
            text_rect = text_rect_no_wrap

        # Calculate actual size with padding from style
        if max_text_width > 0:
            # Limit width to max_text_width
            actual_width = min(
                text_rect.width() + padding_width,
                max_text_width + padding_width,
            )
        else:
            # Unlimited width - use natural text width
            actual_width = text_rect.width() + padding_width

        # CRITICAL FIX for Qt Anti-aliasing:
        # Ensure height is always an even number.
        # If height is odd, rect.bottom() lands on a half-pixel (e.g., 15.5),
        # causing blurry anti-aliased lines that look misaligned.
        # Even height ensures rect.bottom() is an integer (e.g., 15.0) for crisp rendering.
        raw_height = text_rect.height() + padding_height
        actual_height = (
            int(raw_height) if int(raw_height) % 2 == 0 else int(raw_height) + 1
        )

        return actual_width, actual_height, text_rect

    def _update_node_geometry(self, text: str):
        """
        Unified method to update node geometry (size and text position).

        This method recalculates node size and repositions text.

        Args:
            text: New text content
        """
        # Use template_style if available (new architecture), otherwise fallback to legacy
        if hasattr(self, "template_style") and self.template_style:
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
        actual_width, actual_height, text_rect = self._calculate_node_size(
            text, style_for_calc
        )

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

    def start_editing(
        self, on_edit_callback=None, cursor_position: int = -1, mindmap_view=None
    ):
        """Start inline editing with EditableTextItem.

        Args:
            on_edit_callback: Callback when editing finishes
            cursor_position: Cursor position in text (-1 for select all)
            mindmap_view: Reference to MindMapView for Tab key handling
        """
        if self.edit_widget is not None:
            return  # Already editing

        # Create editable text item with proper Tab key handling
        # CRITICAL: Read max_text_width from template_style, never use hardcoded constants
        if hasattr(self, "template_style") and self.template_style:
            max_width = self.template_style.max_text_width
        else:
            # Fallback to global constant for backward compatibility
            max_width = MAX_TEXT_WIDTH

        self.edit_widget = EditableTextItem(
            text=self.text_content,
            max_width=max_width,  # Read from style object
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
        if hasattr(self, "template_style") and self.template_style:
            padding_left = self.template_style.padding_w
            padding_top = self.template_style.padding_h
        else:
            style = NodeStyle.get_style_for_depth(self.depth, self.is_root)
            padding_left = style["padding_width"]
            padding_top = style["padding_height"]

        # CRITICAL: Use the same calculation as text_item position
        # text_item is positioned at: -actual_width/2 + padding_left
        # This ensures no visual jump when entering edit mode
        self.edit_widget.setPos(
            -self.node_width / 2 + padding_left, -self.node_height / 2 + padding_top
        )

        # Hide text item during editing
        self.text_item.setVisible(False)

        # Store callback for manual finish_editing calls
        self.edit_callback = on_edit_callback

        # Cache original dimensions for cancel support
        self._original_node_width = self.node_width
        self._original_node_height = self.node_height

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
            if hasattr(self, "template_style") and self.template_style:
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

            # Update node dimensions and determine expansion direction
            self.node_width = new_node_width
            self.node_height = new_node_height

            new_rect_left = None
            new_rect_top = -new_node_height / 2

            if self.depth == 0 or self.is_root:
                # Root node: centered expansion (both sides)
                new_rect_left = -new_node_width / 2
                self.setRect(
                    new_rect_left,
                    new_rect_top,
                    new_node_width,
                    new_node_height,
                )
            else:
                # Determine expansion direction based on node position
                current_x = self.pos().x()
                is_right_branch = current_x >= 0  # Right side of parent (or root)

                if is_right_branch:
                    # Right branch: LEFT edge stays fixed in scene coordinates
                    # Old left edge (scene) = pos.x + old_left
                    # New left edge (local) should result in same scene position
                    # new_left = old_left (keep same local left)
                    new_rect_left = old_left
                    self.setRect(
                        new_rect_left, new_rect_top, new_node_width, new_node_height
                    )
                else:
                    # Left branch: RIGHT edge stays fixed in scene coordinates
                    # Old right edge (scene) = pos.x + old_right
                    # New right edge (local) should result in same scene position
                    # new_right = old_right, so new_left = old_right - new_width
                    new_rect_right = old_right
                    new_rect_left = new_rect_right - new_node_width
                    self.setRect(
                        new_rect_left, new_rect_top, new_node_width, new_node_height
                    )

            # Update edit widget position (relative to new rect with padding)
            # CRITICAL: Must match the node expansion direction to prevent separation
            # Edit widget left edge always aligns with node left edge + padding
            padding_left = padding_width / 2
            padding_top = padding_height / 2
            edit_x = new_rect_left + padding_left
            edit_y = new_rect_top + padding_top
            self.edit_widget.setPos(edit_x, edit_y)

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
        select_all = cursor_position < 0
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

        # Clear cached original dimensions (editing finished successfully)
        if hasattr(self, '_original_node_width'):
            del self._original_node_width
        if hasattr(self, '_original_node_height'):
            del self._original_node_height

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

        # Restore original dimensions
        if hasattr(self, '_original_node_width') and hasattr(self, '_original_node_height'):
            self.node_width = self._original_node_width
            self.node_height = self._original_node_height

            # Update rect with original dimensions (centered)
            new_rect_left = -self.node_width / 2
            new_rect_top = -self.node_height / 2
            self.setRect(new_rect_left, new_rect_top, self.node_width, self.node_height)

            # Force repaint
            self.update()

            # Update all connected edges
            for edge in self.connected_edges:
                edge.update_curve()

            # Clear cached dimensions
            del self._original_node_width
            del self._original_node_height

        # Show text item again (text remains unchanged)
        self.text_item.setVisible(True)
