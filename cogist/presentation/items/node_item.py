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

from cogist.presentation.items.editable_text_item import EditableTextItem

# === Color Adjustment Helper Functions ===

def adjust_color_brightness(hex_color: str, brightness: float) -> str:
    """Adjust color brightness.

    Args:
        hex_color: Color in #AARRGGBB or #RRGGBB format
        brightness: Brightness factor (0.5-1.5, where 1.0 = no change)

    Returns:
        Adjusted color in #AARRGGBB format
    """
    hex_color = hex_color.lstrip("#")

    # Parse alpha channel if present
    if len(hex_color) == 8:
        alpha = hex_color[:2]
        rgb = hex_color[2:]
    else:
        alpha = "FF"
        rgb = hex_color

    if len(rgb) != 6:
        return f"#{alpha}000000"

    try:
        r = int(rgb[0:2], 16)
        g = int(rgb[2:4], 16)
        b = int(rgb[4:6], 16)
    except ValueError:
        return f"#{alpha}000000"

    # Apply brightness adjustment
    r = min(255, max(0, int(r * brightness)))
    g = min(255, max(0, int(g * brightness)))
    b = min(255, max(0, int(b * brightness)))

    return f"#{alpha}{r:02X}{g:02X}{b:02X}"


def apply_opacity_to_color(hex_color: str, opacity: int) -> str:
    """Apply opacity to color.

    Args:
        hex_color: Color in #RRGGBB or #AARRGGBB format
        opacity: Opacity value (0-255)

    Returns:
        Color with opacity in #AARRGGBB format
    """
    hex_color = hex_color.lstrip("#")

    # Extract RGB
    if len(hex_color) == 8:
        rgb = hex_color[2:]
    elif len(hex_color) == 6:
        rgb = hex_color
    else:
        return hex_color

    return f"#{opacity:02X}{rgb}"


def blend_colors(fg_color: str, bg_color: str, fg_alpha: int = 255) -> str:
    """Blend foreground color over background color using alpha compositing.

    This implements the standard alpha blending formula:
        result = fg * alpha + bg * (1 - alpha)

    Args:
        fg_color: Foreground color in #AARRGGBB or #RRGGBB format
        bg_color: Background color in #AARRGGBB or #RRGGBB format
        fg_alpha: Foreground alpha (0-255). If fg_color has alpha, this is ignored.

    Returns:
        Blended color in #FFRRGGBB format (fully opaque)
    """
    def parse_color(color: str) -> tuple:
        """Parse color to (r, g, b, a) tuple."""
        color = color.lstrip("#")
        if len(color) == 8:
            a = int(color[0:2], 16)
            r = int(color[2:4], 16)
            g = int(color[4:6], 16)
            b = int(color[6:8], 16)
        elif len(color) == 6:
            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)
            a = 255
        else:
            raise ValueError(f"Invalid color format: {color}")
        return r, g, b, a

    try:
        fg_r, fg_g, fg_b, fg_a = parse_color(fg_color)
        bg_r, bg_g, bg_b, bg_a = parse_color(bg_color)

        # Use fg_color's alpha if it has one, otherwise use provided alpha
        alpha = fg_a if len(fg_color.lstrip("#")) == 8 else fg_alpha
        alpha_factor = alpha / 255.0

        # Alpha blending formula
        r = int(fg_r * alpha_factor + bg_r * (1 - alpha_factor))
        g = int(fg_g * alpha_factor + bg_g * (1 - alpha_factor))
        b = int(fg_b * alpha_factor + bg_b * (1 - alpha_factor))

        return f"#FF{r:02X}{g:02X}{b:02X}"
    except (ValueError, IndexError):
        # Fallback to foreground color if parsing fails
        return fg_color


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
            # ROOT: max_text_width=300
            return {
                "font_size": 22,
                "font_weight": QFont.Bold,
                "max_text_width": 300,
                "padding_width": 20,
                "padding_height": 16,
                "border_radius": 10,
            }
        elif depth == 1:
            # PRIMARY: max_text_width=250
            return {
                "font_size": 18,
                "font_weight": QFont.Bold,
                "max_text_width": 250,
                "padding_width": 16,  # Match RoleBasedStyle PRIMARY
                "padding_height": 12,
                "border_radius": 8,
            }
        elif depth == 2:
            # SECONDARY: max_text_width=200
            return {
                "font_size": 16,
                "font_weight": QFont.Normal,
                "max_text_width": 200,
                "padding_width": 12,  # Match RoleBasedStyle SECONDARY
                "padding_height": 10,
                "border_radius": 6,
            }
        else:
            # Depth >= 3: TERTIARY: max_text_width=0 (unlimited, no wrapping)
            return {
                "font_size": 14,
                "font_weight": QFont.Normal,
                "max_text_width": 0,
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
        color: str,  # CRITICAL: Must be provided - no fallback allowed
        text: str = "",
        width: float = None,  # Must be provided - no default
        height: float = None,  # Must be provided - no default
        is_root: bool = False,
        depth: int = 0,
        use_domain_size: bool = False,
        style_config=None,  # MindMapStyle instance for unified styling
        domain_node=None,  # Domain Node entity reference (for accessing parent/children)
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
        self.domain_node = domain_node  # Store domain node reference
        self.is_right_side = (
            True  # Default: right side of root (will be set by main.py)
        )

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

        # NEW: Get role style from MindMapStyle.role_styles (flat structure)
        if not hasattr(self.style_config, 'role_styles') or role not in self.style_config.role_styles:
            node_id = self.domain_node.id if self.domain_node else "unknown"
            available_roles = list(self.style_config.role_styles.keys()) if hasattr(self.style_config, 'role_styles') else []
            import sys
            print(f"DEBUG: Role {role} not found. Available roles: {available_roles}", file=sys.stderr)
            print(f"DEBUG: style_config type: {type(self.style_config)}", file=sys.stderr)
            print(f"DEBUG: style_config.name: {self.style_config.name if hasattr(self.style_config, 'name') else 'N/A'}", file=sys.stderr)
            raise RuntimeError(
                f"Role {role} not found in style_config.role_styles for node {node_id}. Available: {available_roles}"
            )

        role_style = self.style_config.role_styles[role]
        branch_colors = self.style_config.color_pool

        # Extract font properties from role style
        font_size = role_style.font_size
        font_weight_str = role_style.font_weight
        font_family = role_style.font_family

        # === Color Resolution ===
        # Check if rainbow branches are enabled
        if self.style_config.use_rainbow_branches and len(branch_colors) >= 8:
            # Level 1: Use rainbow colors
            if depth == 1 and self.domain_node and self.domain_node.parent:
                try:
                    branch_idx = self.domain_node.parent.children.index(self.domain_node)
                    base_color = branch_colors[branch_idx % 8]  # Cycle through 8 colors

                    # Apply background color with adjustments
                    if role_style.bg_enabled:
                        bg_color = adjust_color_brightness(base_color, role_style.bg_brightness)
                        if role_style.bg_opacity < 255:
                            bg_color = apply_opacity_to_color(bg_color, role_style.bg_opacity)
                    else:
                        bg_color = "#00000000"  # Transparent

                    # Apply border color with adjustments
                    if role_style.border_enabled:
                        border_color = adjust_color_brightness(base_color, role_style.border_brightness)
                        if role_style.border_opacity < 255:
                            border_color = apply_opacity_to_color(border_color, role_style.border_opacity)
                    else:
                        border_color = None
                except (ValueError, AttributeError):
                    # Fallback to default color index
                    bg_color = self._get_color_from_index(role_style.bg_color_index, branch_colors,
                                                          role_style.bg_brightness, role_style.bg_opacity,
                                                          role_style.bg_enabled)
                    border_color = self._get_color_from_index(role_style.border_color_index, branch_colors,
                                                             role_style.border_brightness, role_style.border_opacity,
                                                             role_style.border_enabled)

            # Level 2+: Inherit from Level 1 ancestor
            elif depth >= 2 and self.domain_node:
                level_1_ancestor = self._find_level_1_ancestor()
                if level_1_ancestor:
                    try:
                        if level_1_ancestor.parent:
                            branch_idx = level_1_ancestor.parent.children.index(level_1_ancestor)
                            ancestor_color = branch_colors[branch_idx % 8]

                            # Background
                            if role_style.bg_enabled:
                                bg_color = adjust_color_brightness(ancestor_color, role_style.bg_brightness)
                                if role_style.bg_opacity < 255:
                                    bg_color = apply_opacity_to_color(bg_color, role_style.bg_opacity)
                            else:
                                bg_color = "#00000000"

                            # Border
                            if role_style.border_enabled:
                                border_color = adjust_color_brightness(ancestor_color, role_style.border_brightness)
                                if role_style.border_opacity < 255:
                                    border_color = apply_opacity_to_color(border_color, role_style.border_opacity)
                            else:
                                border_color = None
                        else:
                            bg_color = self._get_color_from_index(role_style.bg_color_index, branch_colors,
                                                                 role_style.bg_brightness, role_style.bg_opacity,
                                                                 role_style.bg_enabled)
                            border_color = self._get_color_from_index(role_style.border_color_index, branch_colors,
                                                                     role_style.border_brightness, role_style.border_opacity,
                                                                     role_style.border_enabled)
                    except (ValueError, AttributeError):
                        bg_color = self._get_color_from_index(role_style.bg_color_index, branch_colors,
                                                             role_style.bg_brightness, role_style.bg_opacity,
                                                             role_style.bg_enabled)
                        border_color = self._get_color_from_index(role_style.border_color_index, branch_colors,
                                                                 role_style.border_brightness, role_style.border_opacity,
                                                                 role_style.border_enabled)
                else:
                    bg_color = self._get_color_from_index(role_style.bg_color_index, branch_colors,
                                                         role_style.bg_brightness, role_style.bg_opacity,
                                                         role_style.bg_enabled)
                    border_color = self._get_color_from_index(role_style.border_color_index, branch_colors,
                                                             role_style.border_brightness, role_style.border_opacity,
                                                             role_style.border_enabled)
            else:
                # Root node (depth == 0): use color index from role_style
                bg_color = self._get_color_from_index(role_style.bg_color_index, branch_colors,
                                                     role_style.bg_brightness, role_style.bg_opacity,
                                                     role_style.bg_enabled)
                border_color = self._get_color_from_index(role_style.border_color_index, branch_colors,
                                                         role_style.border_brightness, role_style.border_opacity,
                                                         role_style.border_enabled)
        else:
            # Rainbow disabled: use color indices directly
            bg_color = self._get_color_from_index(role_style.bg_color_index, branch_colors,
                                                 role_style.bg_brightness, role_style.bg_opacity,
                                                 role_style.bg_enabled)
            border_color = self._get_color_from_index(role_style.border_color_index, branch_colors,
                                                     role_style.border_brightness, role_style.border_opacity,
                                                     role_style.border_enabled)

        # Text color: auto-contrast or manual
        if role_style.text_color:
            text_color = role_style.text_color
        else:
            # Calculate effective background color for text contrast
            # If node background is disabled or transparent, blend with canvas background
            if bg_color is None:
                # Background disabled: use canvas background directly
                canvas_bg = self.style_config.color_pool[8] if (
                    self.style_config and
                    hasattr(self.style_config, 'color_pool') and
                    len(self.style_config.color_pool) > 8
                ) else "#FFFFFFFF"
                text_color = self._auto_contrast(canvas_bg)
            else:
                # Background enabled: check if it's transparent or semi-transparent
                bg_alpha = int(bg_color[1:3], 16) if len(bg_color) == 9 else 255

                if bg_alpha < 255:
                    # Semi-transparent: blend node bg with canvas bg
                    canvas_bg = self.style_config.color_pool[8] if (
                        self.style_config and
                        hasattr(self.style_config, 'color_pool') and
                        len(self.style_config.color_pool) > 8
                    ) else "#FFFFFFFF"

                    # Blend node background over canvas background
                    effective_bg = blend_colors(bg_color, canvas_bg, bg_alpha)
                    text_color = self._auto_contrast(effective_bg)
                else:
                    # Fully opaque: use node background directly
                    text_color = self._auto_contrast(bg_color)

        # Store for rendering
        self.template_style = role_style  # Keep same attribute name for compatibility
        self.bg_color = bg_color
        self.text_color = text_color
        self.border_color = border_color

        style_for_calc = role_style

        # Store for rendering
        self.template_style = role_style  # Keep same attribute name for compatibility
        self.bg_color = bg_color
        self.text_color = text_color
        self.border_color = border_color

        style_for_calc = role_style

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

        # Apply font decorations from role_style
        if hasattr(role_style, "font_italic") and role_style.font_italic:
            font.setItalic(True)
        if hasattr(role_style, "font_underline") and role_style.font_underline:
            font.setUnderline(True)
        if hasattr(role_style, "font_strikeout") and role_style.font_strikeout:
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
            bg_color: Background color in hex format (#RRGGBB or #AARRGGBB)

        Returns:
            '#FFFFFF' for dark backgrounds, '#000000' for light backgrounds
        """
        # Parse hex color
        bg_color = bg_color.lstrip("#")

        # Support both 6-digit (#RRGGBB) and 8-digit (#AARRGGBB) formats
        if len(bg_color) == 8:
            # 8-digit format: skip alpha channel, use RGB
            bg_color = bg_color[2:]  # Remove AA prefix
        elif len(bg_color) != 6:
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
        return "#FFFFFFFF" if luminance < 0.5 else "#FF000000"

    def _get_color_from_index(self, color_index: int, branch_colors: list,
                              brightness: float, opacity: int, enabled: bool) -> str | None:
        """Get color from branch_colors index with adjustments.

        Args:
            color_index: Index into branch_colors array
            branch_colors: List of colors
            brightness: Brightness adjustment factor
            opacity: Opacity value (0-255)
            enabled: Whether the element is enabled

        Returns:
            Color string or None if disabled
        """
        if not enabled:
            return None

        if not branch_colors or color_index >= len(branch_colors):
            return "#FF000000"  # Default black

        base_color = branch_colors[color_index]
        adjusted = adjust_color_brightness(base_color, brightness)
        if opacity < 255:
            adjusted = apply_opacity_to_color(adjusted, opacity)
        return adjusted

    def _find_level_1_ancestor(self):  # type: ignore
        """Find the Level 1 ancestor node (direct child of root).

        Returns:
            The Level 1 ancestor node, or None if not found.
        """
        if not self.domain_node or not self.domain_node.parent:
            return None

        # Walk up the tree to find the Level 1 node
        current = self.domain_node
        while current.parent and current.parent.parent:  # Stop when parent is root
            current = current.parent

        # Check if current's parent is root
        if current.parent and hasattr(current.parent, 'is_root') and current.parent.is_root:
            return current

        return None

    def _adjust_color_brightness(self, color_hex: str, brightness_factor: float) -> str:
        """Adjust color brightness using HSL color space.

        Args:
            color_hex: Color in hex format (#AARRGGBB or #RRGGBB)
            brightness_factor: Brightness adjustment factor (0.0-2.0)
                             0.0 = fully darkened, 1.0 = no change, 2.0 = fully brightened

        Returns:
            Adjusted color in #AARRGGBB format
        """
        import colorsys

        # Parse hex color
        color_hex = color_hex.lstrip("#")

        # Extract alpha channel
        if len(color_hex) == 8:
            alpha = int(color_hex[0:2], 16)
            rgb_hex = color_hex[2:]
        elif len(color_hex) == 6:
            alpha = 255
            rgb_hex = color_hex
        else:
            return color_hex

        try:
            r = int(rgb_hex[0:2], 16) / 255.0
            g = int(rgb_hex[2:4], 16) / 255.0
            b = int(rgb_hex[4:6], 16) / 255.0
        except ValueError:
            return color_hex

        # Convert RGB to HLS
        h, lightness, s = colorsys.rgb_to_hls(r, g, b)

        # Adjust lightness
        new_lightness = lightness * brightness_factor
        new_lightness = max(0.0, min(1.0, new_lightness))  # Clamp to [0, 1]

        # Convert back to RGB
        new_r, new_g, new_b = colorsys.hls_to_rgb(h, new_lightness, s)

        # Convert to hex
        r_int = int(new_r * 255)
        g_int = int(new_g * 255)
        b_int = int(new_b * 255)

        return f"#{alpha:02X}{r_int:02X}{g_int:02X}{b_int:02X}"

    def _apply_opacity(self, color_hex: str, opacity: int) -> str:
        """Apply opacity to a color by modifying the alpha channel.

        Args:
            color_hex: Color in hex format (#AARRGGBB or #RRGGBB)
            opacity: Opacity value (0-255), 255 = fully opaque

        Returns:
            Color with modified alpha channel in #AARRGGBB format
        """
        color_hex = color_hex.lstrip("#")

        # Extract RGB components
        if len(color_hex) == 8:
            rgb_hex = color_hex[2:]
        elif len(color_hex) == 6:
            rgb_hex = color_hex
        else:
            return color_hex

        # Apply new opacity
        return f"#{opacity:02X}{rgb_hex}"

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
        if self.style_config:
            # Map depth to role
            role = self._depth_to_role(self.depth)

            # Get role style directly from role_styles (flat structure)
            if role in self.style_config.role_styles:
                role_style = self.style_config.role_styles[role]
                branch_colors = self.style_config.color_pool

                if role_style:
                    # text_color from role_style or auto contrast
                    text_color = role_style.text_color

                    # Check if rainbow branches are enabled
                    if self.style_config.use_rainbow_branches:
                        # Level 1: Use rainbow colors if enabled
                        if self.depth == 1 and self.domain_node and self.domain_node.parent:
                            # Get branch index from parent's children list
                            try:
                                branch_idx = self.domain_node.parent.children.index(self.domain_node)
                                from cogist.domain.styles.extended_styles import (
                                    get_rainbow_branch_color,
                                )
                                branch_color = get_rainbow_branch_color(branch_idx, self.style_config.color_pool)

                                # In rainbow mode: switches control whether to draw color (rainbow) or not (transparent)
                                # Background: if enabled, draw rainbow color; if disabled, no background
                                if role_style.bg_enabled:
                                    bg_color = branch_color
                                    # Apply brightness adjustment
                                    if role_style.bg_brightness != 1.0:
                                        bg_color = self._adjust_color_brightness(bg_color, role_style.bg_brightness)
                                    # Apply opacity adjustment
                                    if role_style.bg_opacity < 255:
                                        bg_color = self._apply_opacity(bg_color, role_style.bg_opacity)
                                else:
                                    bg_color = "#00000000"  # Transparent (no background)

                                # Border: if enabled, draw rainbow color; if disabled, no border
                                if role_style.border_enabled:
                                    border_color = branch_color
                                    # Apply brightness adjustment
                                    if role_style.border_brightness != 1.0:
                                        border_color = self._adjust_color_brightness(border_color, role_style.border_brightness)
                                    # Apply opacity adjustment
                                    if role_style.border_opacity < 255:
                                        border_color = self._apply_opacity(border_color, role_style.border_opacity)
                                else:
                                    border_color = None  # No border
                            except (ValueError, AttributeError):
                                # Fallback to default color if index not found
                                bg_color = "#FFFFFFFF"
                                border_color = "#FF000000"

                        # Level 2+: Inherit from Level 1 ancestor with brightness adjustment
                        elif self.depth >= 2 and self.domain_node:
                            level_1_ancestor = self._find_level_1_ancestor()
                            if level_1_ancestor:
                                # Get Level 1 ancestor's branch color
                                try:
                                    # Find the Level 1 node's position in its parent's children
                                    if level_1_ancestor.parent:
                                        branch_idx = level_1_ancestor.parent.children.index(level_1_ancestor)
                                        from cogist.domain.styles.extended_styles import (
                                            get_rainbow_branch_color,
                                        )
                                        ancestor_branch_color = get_rainbow_branch_color(
                                            branch_idx, self.style_config.color_pool
                                        )

                                        # Background: if enabled, draw rainbow color; if disabled, no background
                                        if role_style.bg_enabled:
                                            bg_color = self._adjust_color_brightness(ancestor_branch_color, role_style.bg_brightness)
                                            # Apply opacity adjustment (0-255)
                                            if role_style.bg_opacity < 255:
                                                bg_color = self._apply_opacity(bg_color, role_style.bg_opacity)
                                        else:
                                            bg_color = "#00000000"  # Transparent (no background)

                                        # Border: if enabled, draw rainbow color; if disabled, no border
                                        if role_style.border_enabled:
                                            border_color = self._adjust_color_brightness(ancestor_branch_color, role_style.border_brightness)
                                            # Apply opacity adjustment to border as well
                                            if role_style.border_opacity < 255:
                                                border_color = self._apply_opacity(border_color, role_style.border_opacity)
                                        else:
                                            border_color = None  # No border
                                    else:
                                        bg_color = "#FFFFFFFF"
                                        border_color = "#FF000000"
                                except (ValueError, AttributeError):
                                    bg_color = "#FFFFFFFF"
                                    border_color = "#FF000000"
                            else:
                                bg_color = "#FFFFFFFF"
                                border_color = "#FF000000"
                        else:
                            # Root node (depth == 0): use color index from role_style
                            bg_color = self._get_color_from_index(role_style.bg_color_index, branch_colors,
                                                                 role_style.bg_brightness, role_style.bg_opacity,
                                                                 role_style.bg_enabled)
                            border_color = self._get_color_from_index(role_style.border_color_index, branch_colors,
                                                                     role_style.border_brightness, role_style.border_opacity,
                                                                     role_style.border_enabled)
                    else:
                        # Rainbow disabled: use color indices from role_style
                        bg_color = self._get_color_from_index(role_style.bg_color_index, branch_colors,
                                                             role_style.bg_brightness, role_style.bg_opacity,
                                                             role_style.bg_enabled)
                        border_color = self._get_color_from_index(role_style.border_color_index, branch_colors,
                                                                 role_style.border_brightness, role_style.border_opacity,
                                                                 role_style.border_enabled)

                    # text_color from role_style or auto contrast
                    if not text_color:
                        # Calculate effective background color for text contrast
                        # If node background is disabled or transparent, blend with canvas background
                        if bg_color is None:
                            # Background disabled: use canvas background directly
                            canvas_bg = self.style_config.color_pool[8] if (
                                self.style_config and
                                hasattr(self.style_config, 'color_pool') and
                                len(self.style_config.color_pool) > 8
                            ) else "#FFFFFFFF"
                            text_color = self._auto_contrast(canvas_bg)
                        else:
                            # Background enabled: check if it's transparent or semi-transparent
                            bg_alpha = int(bg_color[1:3], 16) if len(bg_color) == 9 else 255

                            if bg_alpha < 255:
                                # Semi-transparent: blend node bg with canvas bg
                                canvas_bg = self.style_config.color_pool[8] if (
                                    self.style_config and
                                    hasattr(self.style_config, 'color_pool') and
                                    len(self.style_config.color_pool) > 8
                                ) else "#FFFFFFFF"

                                # Blend node background over canvas background
                                effective_bg = blend_colors(bg_color, canvas_bg, bg_alpha)
                                text_color = self._auto_contrast(effective_bg)
                            else:
                                # Fully opaque: use node background directly
                                text_color = self._auto_contrast(bg_color)
                else:
                    # CRITICAL: color_scheme must be available - no fallback allowed
                    node_id = self.domain_node.id if self.domain_node else "unknown"
                    raise RuntimeError(
                        f"color_scheme is required but got None for node {node_id} at depth {self.depth}"
                    )

                # Store for rendering
                self.template_style = role_style
                self.bg_color = bg_color
                self.text_color = text_color
                self.border_color = border_color

                # Update font
                font_size = role_style.font_size
                font_weight_str = role_style.font_weight
                font_family = role_style.font_family

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
                # CRITICAL: Always apply font_italic from role_style
                if role_style.font_italic:
                    font.setItalic(True)

                # CRITICAL: Apply underline and strikeout
                if hasattr(role_style, "font_underline") and role_style.font_underline:
                    font.setUnderline(True)
                if hasattr(role_style, "font_strikeout") and role_style.font_strikeout:
                    font.setStrikeOut(True)

                self.text_item.setFont(font)

                # Update text color
                if isinstance(text_color, str):
                    self.text_item.setDefaultTextColor(QColor(text_color))
                else:
                    self.text_item.setDefaultTextColor(text_color)

                # Apply font shadow effect
                self._apply_font_shadow()
            else:
                # CRITICAL: role_style must exist for all roles - no fallback allowed
                node_id = self.domain_node.id if self.domain_node else "unknown"
                raise RuntimeError(
                    f"role_style is required for role '{role}' but got None for node {node_id}"
                )

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
                child_item.setPos(child_item.scenePos() + offset)

            # Update last position
            self._last_pos = new_pos

            # Update all connected edges (both incoming from parent and outgoing to children)
            for edge in self.connected_edges:
                edge.update_curve()

        return super().itemChange(change, value)

    def paint(self, painter, option, widget=None):
        """Custom paint using border strategy pattern."""
        from PySide6.QtGui import QPainter

        from cogist.presentation.borders.registry import BorderStrategyRegistry

        painter.setRenderHint(QPainter.Antialiasing, True)

        # NEW: Use flat RoleStyle fields
        shape_type = self.template_style.basic_shape if hasattr(self.template_style, 'basic_shape') else "rounded_rect"
        rect = self.rect()

        # Use cached colors from update_style (no recalculation needed)
        bg_color = self.bg_color
        border_color = self.border_color

        # Build style config dict for strategy
        style_config = {
            "bg_color": bg_color,
            "border_color": border_color,
            "border_width": self.template_style.border_width if hasattr(self.template_style, 'border_width') else 0,
            "border_radius": self.template_style.border_radius if hasattr(self.template_style, 'border_radius') else 8,
            "border_style": self.template_style.border_style if hasattr(self.template_style, 'border_style') else "solid",
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

    def _calculate_node_size(
        self, text: str, style=None
    ) -> tuple[float, float, object]:
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
            # Fallback to RoleBasedStyle values based on depth
            # ROOT (depth=0): 300, PRIMARY (depth=1): 250, SECONDARY (depth=2): 200, TERTIARY (depth>=3): 0
            fallback_widths = {0: 300, 1: 250, 2: 200}
            max_width = fallback_widths.get(self.depth, 0)

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
            current_x = self.scenePos().x()
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
                current_x = self.scenePos().x()
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
        if hasattr(self, "_original_node_width"):
            del self._original_node_width
        if hasattr(self, "_original_node_height"):
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
        if hasattr(self, "_original_node_width") and hasattr(
            self, "_original_node_height"
        ):
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
