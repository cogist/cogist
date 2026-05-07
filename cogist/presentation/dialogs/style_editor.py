"""
Style Editor - Real-time Style Editing and Template Creation (Refactored)

A dockable panel for real-time style editing and template creation.
Uses modular components with lazy initialization for better performance.

Refactored version: Uses component-based architecture from style_widgets/
"""

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from ..items.node_item import adjust_color_brightness
from .style_widgets import (
    BorderSection,
    CanvasPanel,
    ConnectorSection,
    FontStyleSection,
    LayerSelector,
    NodeStyleSection,
    ShadowSection,
    SpacingSection,
)


class StyleEditorTab(QWidget):
    """Style editor tab using modular components with lazy initialization.

    This refactored version uses component-based architecture:
    - LayerSelector: Layer switching
    - ColorSchemeSection: Color scheme management
    - NodeStyleSection: Node appearance
    - BorderSection: Border styling
    - ConnectorSection: Edge styling

    All components implement lazy initialization - they only create
    their internal widgets when expanded by the user.
    """

    # Panel dimensions
    PANEL_WIDTH = 260  # Original carefully designed width
    LABEL_WIDTH = 90  # Unified label column width for all sections

    def __init__(
        self, style_config=None, config_manager=None, command_history=None, parent=None
    ):
        super().__init__(parent)

        # Set initial width (fixed, non-resizable)
        self.setMinimumWidth(self.PANEL_WIDTH)
        self.setMaximumWidth(self.PANEL_WIDTH)

        # Store reference to global style configuration
        self.style_config = style_config
        if not self.style_config:
            raise ValueError(
                "style_config is required - panel must have access to global style data"
            )

        # Store reference to config manager
        self.config_manager = config_manager

        # Store reference to command history for undo/redo
        self.command_history = command_history

        # Flag to prevent command creation during undo/redo
        self._updating_from_undo_redo = False

        self.current_layer = "canvas"

        # Initialize UI with modular components
        self._init_ui()

        # Connect signals
        self._connect_signals()

        # Set initial visibility based on default layer (canvas)
        self._set_initial_visibility()

        # Load initial layer style
        self._load_current_layer_style()

    def _get_layer_data(self, layer_name: str) -> dict:
        """Get style data for a layer directly from global style_config.

        This method reads from style_config.role_styles and color_pool,
        ensuring panel always uses the authoritative data source.

        Args:
            layer_name: Layer name (canvas, root, level_1, level_2, level_3_plus, etc.)

        Returns:
            Dictionary with all style fields for the layer
        """
        assert self.style_config is not None, "style_config must be set"

        if layer_name == "canvas":
            # Canvas needs global rainbow config too
            canvas_bg = self.style_config.special_colors["canvas_bg"]
            data = {
                "bg_color": canvas_bg,
                "use_rainbow_branches": self.style_config.use_rainbow_branches,
                "color_pool": self.style_config.color_pool,
            }
            return data

        # Map layer names to NodeRole
        layer_to_role = {
            "root": "root",
            "level_1": "primary",
            "level_2": "secondary",
            "level_3_plus": "tertiary",
            "critical": "tertiary",
            "minor": "tertiary",
        }

        role_str = layer_to_role.get(layer_name)
        if not role_str:
            raise ValueError(f"Unknown layer: {layer_name}")

        from cogist.domain.styles import NodeRole

        role = NodeRole(role_str)

        # NEW: Get role style directly from MindMapStyle.role_styles (flat structure)
        if (
            not hasattr(self.style_config, "role_styles")
            or role not in self.style_config.role_styles
        ):
            raise ValueError(
                f"No style data for role {role} in style_config.role_styles"
            )

        role_style = self.style_config.role_styles[role]
        color_pool = self.style_config.color_pool

        # Build complete layer data from global style config
        # NEW: Use flat RoleStyle structure with color indices

        # Get background color
        if layer_name == "root":
            bg_color = self.style_config.special_colors["root_background"]
        else:
            # Other layers: use bg_color_index to reference the pool
            bg_color_index = role_style.bg_color_index

            # Apply brightness and opacity to get final color
            base_bg_color = color_pool[bg_color_index]
            bg_color = adjust_color_brightness(base_bg_color, role_style.bg_brightness)
            # Apply opacity by modifying alpha channel
            if role_style.bg_opacity < 255:
                # Convert opacity to hex and replace alpha channel
                opacity_hex = f"{role_style.bg_opacity:02X}"
                if len(bg_color) == 9:  # #AARRGGBB format
                    bg_color = "#" + opacity_hex + bg_color[3:]
                else:  # #RRGGBB format
                    bg_color = "#" + opacity_hex + bg_color[1:]

        # Text color: auto-contrast or manual
        text_color = (
            role_style.text_color
            if role_style.text_color
            else self._auto_contrast(bg_color)
        )

        # Border color using index system
        if layer_name == "root":
            border_color = self.style_config.special_colors["root_border"]
        else:
            border_color_index = role_style.border_color_index
            border_color = color_pool[border_color_index]

        layer_data = {
            # Shape - flat fields from RoleStyle
            "shape": role_style.basic_shape,
            "radius": role_style.border_radius,
            # Background enabled
            "bg_enabled": role_style.bg_enabled,
            # Colors
            "bg_color": bg_color,
            "text_color": text_color,
            "border_color": border_color,
            # Font
            "font_family": role_style.font_family,
            "font_size": role_style.font_size,
            "font_weight": role_style.font_weight,
            "font_italic": role_style.font_italic,
            "font_underline": role_style.font_underline,
            "font_strikeout": role_style.font_strikeout,
            # Shadow
            "shadow_enabled": role_style.shadow_enabled,
            "shadow_offset_x": role_style.shadow_offset_x,
            "shadow_offset_y": role_style.shadow_offset_y,
            "shadow_blur": role_style.shadow_blur,
            "shadow_color": role_style.shadow_color,
            # Border - NEW: flat fields
            "border_enabled": role_style.border_enabled,
            "border_style": role_style.border_style,
            "border_width": role_style.border_width,
            "border_color_index": role_style.border_color_index,
            "border_brightness": role_style.border_brightness,
            "border_opacity": role_style.border_opacity,
            # Padding
            "padding_w": role_style.padding_w,
            "padding_h": role_style.padding_h,
            # Max text width
            "max_text_width": role_style.max_text_width,
            # Connector - read from role-based configuration
            "connector_type": self._get_connector_type_for_layer(layer_name),
            "connector_style": self._get_connector_style_for_layer(layer_name),
            "connector_width": self._get_connector_width_for_layer(layer_name),
            "connector_color": self._get_connector_color_for_layer(layer_name),
            "connector_color_index": role_style.connector_color_index,
            # Spacing - read from role-based configuration
            "parent_child_spacing": self._get_level_spacing_for_layer(layer_name),
            "sibling_spacing": self._get_sibling_spacing_for_layer(layer_name),
            # Rainbow branch - global MindMapStyle properties
            "use_rainbow": self.style_config.use_rainbow_branches,
            "rainbow_pool": color_pool,
            # Rainbow bg/border - per-role flags (NEW: use simple booleans)
            "rainbow_bg_enabled": True,  # TODO: Add to RoleStyle
            "rainbow_border_enabled": True,  # TODO: Add to RoleStyle
            # Brightness and opacity - per-role (from RoleStyle)
            "brightness_amount": role_style.bg_brightness,
            "opacity_amount": role_style.bg_opacity,
        }

        return layer_data

    def _get_current_layer_role(self):
        """Map current layer to node role for spacing configuration."""
        from cogist.domain.styles.extended_styles import NodeRole

        role_map = {
            "canvas": None,  # Canvas is special
            "root": NodeRole.ROOT,
            "level_1": NodeRole.PRIMARY,
            "level_2": NodeRole.SECONDARY,
            "level_3_plus": NodeRole.TERTIARY,
            "critical": NodeRole.TERTIARY,
            "minor": NodeRole.TERTIARY,
        }
        return role_map.get(self.current_layer)

    def _get_level_spacing_for_layer(self, layer_name: str) -> float:
        """Get parent-child spacing for a layer from role-based configuration."""
        assert self.style_config is not None

        # NEW: Get from MindMapStyle.role_styles
        role = self._get_current_layer_role()
        assert role is not None, f"Role should not be None for layer {layer_name}"
        assert (
            hasattr(self.style_config, 'role_styles')
            and role in self.style_config.role_styles
        ), f"Role {role} should exist in style_config.role_styles"

        return self.style_config.role_styles[role].parent_child_spacing

    def _get_sibling_spacing_for_layer(self, layer_name: str) -> float:
        """Get sibling spacing for a layer from role-based configuration."""
        assert self.style_config is not None
        if layer_name == "root":
            return 0

        # NEW: Get from MindMapStyle.role_styles
        role = self._get_current_layer_role()
        assert role is not None, f"Role should not be None for layer {layer_name}"
        assert (
            hasattr(self.style_config, 'role_styles')
            and role in self.style_config.role_styles
        ), f"Role {role} should exist in style_config.role_styles"

        return self.style_config.role_styles[role].sibling_spacing

    def _get_connector_type_for_layer(self, layer_name: str) -> str:
        """Get connector type for a layer from role-based configuration."""
        assert self.style_config is not None

        # NEW: Get from MindMapStyle.role_styles
        role = self._get_current_layer_role()
        assert role is not None, f"Role should not be None for layer {layer_name}"
        assert (
            hasattr(self.style_config, 'role_styles')
            and role in self.style_config.role_styles
        ), f"Role {role} should exist in style_config.role_styles"

        return self.style_config.role_styles[role].connector_shape

    def _get_connector_style_for_layer(self, layer_name: str) -> str:
        """Get connector style for a layer from role-based configuration."""
        assert self.style_config is not None

        # NEW: Get from MindMapStyle.role_styles
        role = self._get_current_layer_role()
        assert role is not None, f"Role should not be None for layer {layer_name}"
        assert (
            hasattr(self.style_config, 'role_styles')
            and role in self.style_config.role_styles
        ), f"Role {role} should exist in style_config.role_styles"

        return self.style_config.role_styles[role].connector_style

    def _get_connector_width_for_layer(self, layer_name: str) -> float:
        """Get connector width for a layer from role-based configuration."""
        assert self.style_config is not None

        # NEW: Get from MindMapStyle.role_styles
        role = self._get_current_layer_role()
        assert role is not None, f"Role should not be None for layer {layer_name}"
        assert (
            hasattr(self.style_config, 'role_styles')
            and role in self.style_config.role_styles
        ), f"Role {role} should exist in style_config.role_styles"

        return self.style_config.role_styles[role].line_width

    def _get_connector_color_for_layer(self, layer_name: str) -> str:
        """Get connector color for a layer from role-based configuration."""
        assert self.style_config is not None

        # NEW: Get from MindMapStyle.role_styles using color index
        role = self._get_current_layer_role()
        assert role is not None, f"Role should not be None for layer {layer_name}"
        assert (
            hasattr(self.style_config, 'role_styles')
            and role in self.style_config.role_styles
        ), f"Role {role} should exist in style_config.role_styles"

        role_style = self.style_config.role_styles[role]
        color_pool = self.style_config.color_pool

        # Use connector_color_index to get color from pool
        color_index = role_style.connector_color_index
        return color_pool[color_index]

    def _update_role_style_in_config(self, layer_name: str, updates: dict):
        """Update specific fields of a role's style in global style_config.

        Args:
            layer_name: Layer name (root, level_1, etc.)
            updates: Dictionary of fields to update
        """
        assert self.style_config is not None

        if layer_name == "canvas":
            # Handle canvas background color separately
            self.style_config.special_colors["canvas_bg"] = updates["bg_color"]
            return  # Canvas doesn't have role styles

        # Map layer to role
        layer_to_role = {
            "root": "root",
            "level_1": "primary",
            "level_2": "secondary",
            "level_3_plus": "tertiary",
            "critical": "tertiary",
            "minor": "tertiary",
        }

        role_str = layer_to_role.get(layer_name)
        if not role_str:
            return

        from cogist.domain.styles import NodeRole

        role = NodeRole(role_str)

        if role not in self.style_config.role_styles:
            return

        role_style = self.style_config.role_styles[role]

        # Apply updates to role_style
        for key, value in updates.items():
            if key == "shape":
                # Handle shape type update
                if hasattr(role_style, "basic_shape"):
                    role_style.basic_shape = value
            elif key == "radius":
                # Handle border radius update
                if hasattr(role_style, "border_radius"):
                    role_style.border_radius = value
            elif key == "bg_color":
                # Background color
                if role == NodeRole.ROOT:
                    # Root node: update special_colors directly
                    self.style_config.special_colors["root_background"] = value
                else:
                    # Other nodes: find color index in color_pool
                    if hasattr(role_style, "bg_color_index"):
                        if value in self.style_config.color_pool:
                            role_style.bg_color_index = self.style_config.color_pool.index(value)
                        else:
                            # If color not in pool, use default index
                            role_style.bg_color_index = 0
            elif key == "text_color":
                # Text color goes to role_style
                if hasattr(role_style, "text_color"):
                    role_style.text_color = value
            elif key == "border_color":
                # Border color
                if role == NodeRole.ROOT:
                    # Root node: update special_colors directly
                    self.style_config.special_colors["root_border"] = value
                else:
                    # Other nodes: find color index in color_pool
                    if hasattr(role_style, "border_color_index"):
                        if value in self.style_config.color_pool:
                            role_style.border_color_index = self.style_config.color_pool.index(value)
                        else:
                            # If color not in pool, use default index
                            role_style.border_color_index = 0
            elif key == "font_italic":
                # Direct boolean assignment
                if hasattr(role_style, "font_italic"):
                    role_style.font_italic = value
            elif key == "max_text_width":
                # Handle max text width update
                if hasattr(role_style, "max_text_width"):
                    role_style.max_text_width = value
            elif hasattr(role_style, key):
                setattr(role_style, key, value)
            elif key.startswith("shadow_"):
                # Handle shadow attributes
                attr_name = key
                if hasattr(role_style, attr_name):
                    setattr(role_style, attr_name, value)
            elif key.startswith("border_") and hasattr(role_style, "border"):
                # Handle border attributes on border object
                # border_style and border_width are the actual field names in BorderStyle
                border_attr = key  # Keep the full name (border_style, border_width)
                if hasattr(role_style.border, border_attr):
                    setattr(role_style.border, border_attr, value)

    def _init_ui(self):
        """Initialize UI with modular components."""
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setFrameShadow(QScrollArea.Plain)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("QScrollArea { border: none; padding: 0; margin: 0; }")

        # Create content widget
        content_widget = QWidget()
        content_widget.setMinimumWidth(
            self.PANEL_WIDTH
        )  # Ensure content fills panel width
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)  # No spacing between collapsible panels

        # Add modular components
        self.layer_selector = LayerSelector()
        self.canvas_panel = CanvasPanel(self)  # NEW: Canvas panel for background color
        # ColorSchemeSection removed - now in separate ColorSchemeTab
        self.spacing_section = SpacingSection(parent=self)
        self.node_style_section = NodeStyleSection(parent=self)
        self.font_style_section = FontStyleSection()
        self.shadow_section = ShadowSection()
        self.border_section = BorderSection(parent=self)
        self.connector_section = ConnectorSection(parent=self)

        layout.addWidget(self.layer_selector)
        layout.addWidget(self.canvas_panel)  # NEW: Canvas panel
        layout.addWidget(self.spacing_section)
        layout.addWidget(self.node_style_section)
        layout.addWidget(self.font_style_section)
        layout.addWidget(self.shadow_section)
        layout.addWidget(self.border_section)
        layout.addWidget(self.connector_section)
        layout.addStretch()

        # Connect signals
        # CanvasPanel signal handling removed - canvas background is managed in ColorSchemeTab

        scroll.setWidget(content_widget)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        # Apply custom styles
        self._apply_styles()

    def _apply_styles(self):
        """Apply custom QSS styles to the panel."""
        self.setStyleSheet("""
            StyleEditorTab {
                background-color: #F5F5F5;
            }
            QGroupBox {
                background-color: #FFFFFF;
                border: 1px solid #C8C8C8;
                border-radius: 8px;
                margin-top: 24px;
                padding-top: 12px;
                padding-bottom: 12px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 12px;
                background-color: transparent;
                font-weight: bold;
                font-size: 13px;
            }
        """)

    def _connect_signals(self):
        """Connect component signals to handlers."""
        # Layer selection
        self.layer_selector.layer_changed.connect(self._on_layer_changed)

        # ColorSchemeSection removed - now in separate ColorSchemeTab

        # NEW: Connect CanvasPanel signal for background color changes
        self.canvas_panel.style_changed.connect(self._on_canvas_bg_color_changed)

        # Spacing configuration
        self.spacing_section.spacing_changed.connect(self._on_spacing_changed)

        # Node style
        self.node_style_section.style_changed.connect(self._on_node_style_changed)
        self.node_style_section.shadow_enabled_changed.connect(
            self._on_shadow_enabled_changed
        )

        # Font style
        self.font_style_section.style_changed.connect(self._on_font_style_changed)
        self.font_style_section.shadow_enabled_changed.connect(
            self._on_font_shadow_enabled_changed
        )

        # Shadow style
        self.shadow_section.shadow_changed.connect(self._on_shadow_changed)

        # Border style
        self.border_section.style_changed.connect(self._on_border_style_changed)

        # Connector style
        self.connector_section.style_changed.connect(self._on_connector_style_changed)

    def _on_canvas_bg_color_changed(self, style: dict):
        """Handle canvas background color change from CanvasPanel.

        Args:
            style: Dictionary with 'bg_color' key containing the new color
        """
        assert self.style_config is not None

        if "bg_color" not in style:
            return

        # Note: CanvasPanel already updated style_config.special_colors["canvas_bg"]
        # and created undo command. Just need to refresh the UI.

        # Apply styles to mindmap (this will update canvas background)
        self._apply_styles_to_mindmap()

    def _on_layer_changed(self, layer_name: str):
        """Handle layer selection change."""
        # No need to save - styles are already saved directly to global config
        # Update current layer
        self.current_layer = layer_name

        # Show/hide sections based on layer type
        is_canvas = layer_name == "canvas"
        is_priority = layer_name in ["critical", "minor"]

        # Canvas panel: only show for canvas layer
        self.canvas_panel.setVisible(is_canvas)

        # Spacing: only show for non-canvas layers (not a global setting)
        self.spacing_section.setVisible(not is_canvas)

        # Node/Border/Connector: only show for non-canvas layers
        self.node_style_section.setVisible(not is_canvas)

        # Set root mode for node style section
        is_root = layer_name == "root"
        self.node_style_section.set_root_mode(is_root)

        self.font_style_section.setVisible(not is_canvas)
        # Shadow section visibility is controlled by shadow_enabled state in _load_current_layer_style
        self.border_section.setVisible(not is_canvas)
        self.connector_section.setVisible(not is_canvas and not is_priority)

        # Load style for selected layer
        self._load_current_layer_style()

    def _on_color_scheme_changed(self, colors: dict):
        """Handle color scheme change.

        This method routes color changes to the appropriate place in style_config:
        - bg_color -> color_scheme.node_colors[current_role]
        - text_color -> color_scheme.text_colors[current_role]
        - border_color -> color_scheme.border_colors[current_role]
        - connector_color -> role_style.connector_color
        - canvas_bg -> color_scheme.canvas_bg

        Args:
            colors: Dictionary of changed color values
        """
        from cogist.domain.styles import NodeRole

        assert self.style_config is not None

        # Get current role
        role = self._get_current_layer_role()

        # Handle global rainbow config FIRST (before checking role)
        # This ensures rainbow state is synced across all layers including canvas
        # NOTE: Rainbow config changes are handled by command system below
        # Do NOT modify style_config here to avoid duplicate updates

        # Use command system if available
        if self.command_history:
            from cogist.application.commands import ChangeStyleCommand
            from cogist.application.commands.change_style_command import StyleChange

            style_updates = {}

            # Build style updates based on changed colors
            if "use_rainbow_branches" in colors:
                style_updates["use_rainbow_branches"] = colors["use_rainbow_branches"]
            if "color_pool" in colors:
                style_updates["color_pool"] = colors["color_pool"]
            if "bg_color" in colors:
                style_updates["bg_color"] = colors["bg_color"]
            if "text_color" in colors:
                style_updates["text_color"] = colors["text_color"]
            if "border_color" in colors:
                style_updates["border_color"] = colors["border_color"]
            if "connector_color" in colors:
                style_updates["connector_color"] = colors["connector_color"]
            if "canvas_bg" in colors:
                style_updates["bg_color"] = colors["canvas_bg"]  # Map canvas_bg to bg_color for canvas layer

            if style_updates:
                change = StyleChange(
                    layer=self.current_layer,
                    style_updates=style_updates,
                )
                command = ChangeStyleCommand(
                    style_config=self.style_config,
                    changes=[change],
                )
                command.execute()
                self.command_history.push(command)

                # Apply styles to mindmap after command execution
                self._apply_styles_to_mindmap()

                # Refresh UI after rainbow config change
                if "use_rainbow_branches" in style_updates or "color_pool" in style_updates:
                    self._load_current_layer_style()
                return

        # Fallback: direct update without undo/redo
        if not role:
            # Canvas layer - handle canvas_bg if present
            if "canvas_bg" in colors:
                self.style_config.special_colors["canvas_bg"] = colors["canvas_bg"]

            # Apply styles to mindmap after updating canvas/rainbow config
            self._apply_styles_to_mindmap()
            return

        # Handle per-role rainbow mode controls (for root/level_1/2/3+)
        if role and self.current_layer in [
            "root",
            "level_1",
            "level_2",
            "level_3_plus",
        ] and role in self.style_config.role_styles:
            role_style = self.style_config.role_styles[role]

            # TODO: rainbow_bg_enabled and rainbow_border_enabled will be handled later
            # if "rainbow_bg_enabled" in colors:
            #     role_style.bg_enabled = colors["rainbow_bg_enabled"]
            # if "rainbow_border_enabled" in colors:
            #     role_style.border_enabled = colors["rainbow_border_enabled"]
            #     # Control border section visibility based on rainbow_border_enabled
            #     self.border_section.setVisible(colors["rainbow_border_enabled"])

            # Brightness and opacity adjustments
            if "brightness_amount" in colors:
                role_style.bg_brightness = colors["brightness_amount"]
                role_style.border_brightness = colors["brightness_amount"]
            if "opacity_amount" in colors:
                role_style.bg_opacity = colors["opacity_amount"]
                role_style.border_opacity = colors["opacity_amount"]

        # Apply styles to mindmap after updating role configs
        self._apply_styles_to_mindmap()

        # Fallback: direct update without undo/redo (already handled above if command_history exists)
        if not self.command_history and role in self.style_config.role_styles:
            role_style = self.style_config.role_styles[role]

            # Handle node background color
            if "bg_color" in colors:
                if role == NodeRole.ROOT:
                    # Root node: update special_colors directly
                    self.style_config.special_colors["root_background"] = colors["bg_color"]
                else:
                    # Other nodes: find color index in color_pool
                    if colors["bg_color"] in self.style_config.color_pool:
                        role_style.bg_color_index = self.style_config.color_pool.index(colors["bg_color"])
                    else:
                        # If color not in pool, use default index
                        role_style.bg_color_index = 0

            # Handle text/foreground color
            if "text_color" in colors:
                role_style.text_color = colors["text_color"]

            # Handle border color
            if "border_color" in colors:
                if role == NodeRole.ROOT:
                    # Root node: update special_colors directly
                    self.style_config.special_colors["root_border"] = colors["border_color"]
                else:
                    # Other nodes: find color index in color_pool
                    if colors["border_color"] in self.style_config.color_pool:
                        role_style.border_color_index = self.style_config.color_pool.index(colors["border_color"])
                    else:
                        # If color not in pool, use default index
                        role_style.border_color_index = 0

            # Handle connector color
            if "connector_color" in colors:
                # Find color index in color_pool
                if colors["connector_color"] in self.style_config.color_pool:
                    role_style.connector_color_index = self.style_config.color_pool.index(colors["connector_color"])
                else:
                    # If color not in pool, use default index
                    role_style.connector_color_index = 0

        self._apply_styles_to_mindmap()

    def _on_spacing_changed(self, spacing: dict):
        """Handle spacing configuration change for the current layer."""
        assert self.style_config is not None
        if self.current_layer != "canvas":
            # Get role for current layer
            role = self._get_current_layer_role()
            if not role:
                return

            # Prepare style updates for command
            style_updates = {}
            if "parent_child" in spacing:
                style_updates["parent_child_spacing"] = spacing["parent_child"]

            if "sibling" in spacing:
                style_updates["sibling_spacing"] = spacing["sibling"]

            # Skip command creation if we're updating from undo/redo
            if (
                self._updating_from_undo_redo
                and style_updates
                and role in self.style_config.role_styles
            ):
                # Direct update to role-based config
                role_style = self.style_config.role_styles[role]
                if "parent_child" in spacing:
                    role_style.parent_child_spacing = spacing["parent_child"]
                if "sibling" in spacing:
                    role_style.sibling_spacing = spacing["sibling"]
            elif self.command_history and style_updates:
                from cogist.application.commands import ChangeStyleCommand
                from cogist.application.commands.change_style_command import StyleChange

                change = StyleChange(
                    layer=self.current_layer,
                    style_updates=style_updates,
                )
                command = ChangeStyleCommand(
                    style_config=self.style_config,
                    changes=[change],
                )
                command.execute()
                self.command_history.push(command)
            elif style_updates:
                # Fallback: direct update to role-based config without undo/redo
                if role in self.style_config.role_styles:
                    role_style = self.style_config.role_styles[role]
                    if "parent_child" in spacing:
                        role_style.parent_child_spacing = spacing["parent_child"]
                    if "sibling" in spacing:
                        role_style.sibling_spacing = spacing["sibling"]

            # Trigger layout refresh through _apply_styles_to_mindmap
            self._apply_styles_to_mindmap()

    def _on_node_style_changed(self, style: dict):
        """Handle node style changes."""
        if self.current_layer != "canvas":
            # Check if this change affects node dimensions (requires size recalculation)
            dimension_keys = {
                "max_text_width",
                "padding_w",
                "padding_h",
                "font_size",
                "font_family",
                "font_weight",
                "font_italic",
                "font_underline",
                "font_strikeout",
            }
            affects_dimensions = any(key in style for key in dimension_keys)

            # Check if this change requires style update (affects colors, visibility, etc.)
            style_update_keys = {
                "bg_enabled",
                "border_enabled",
                "bg_color",
                "border_color",
                "text_color",
                "bg_brightness",
                "bg_opacity",
            }
            requires_style_update = any(key in style for key in style_update_keys)

            # Skip command creation if we're updating from undo/redo
            if self._updating_from_undo_redo:
                # Direct update without creating a command
                self._update_role_style_in_config(self.current_layer, style)
            elif self.command_history:
                from cogist.application.commands import ChangeStyleCommand
                from cogist.application.commands.change_style_command import StyleChange

                # Create and execute style change command
                change = StyleChange(
                    layer=self.current_layer,
                    style_updates=style,
                )
                command = ChangeStyleCommand(
                    style_config=self.style_config,
                    changes=[change],
                )
                command.execute()
                self.command_history.push(command)
            else:
                # Fallback: direct update without undo/redo
                self._update_role_style_in_config(self.current_layer, style)

            self._apply_styles_to_mindmap(force_rebuild=affects_dimensions or requires_style_update)

    def _on_shadow_enabled_changed(self, enabled: bool):
        """Handle font shadow enabled state change."""
        if enabled:
            # Disable updates on parent to prevent layout flash
            self.setUpdatesEnabled(False)

            # Initialize content first if not already initialized (lazy init)
            if not self.shadow_section._initialized:
                self.shadow_section._init_content()
                self.shadow_section._initialized = True

            # Set collapsed state and make visible while updates are disabled
            self.shadow_section.setCollapsed(False)
            self.shadow_section.setVisible(True)

            # Re-enable updates - Qt will do a single layout update
            self.setUpdatesEnabled(True)
        else:
            self.shadow_section.setVisible(False)

        # Update using command system if available
        if self.current_layer != "canvas":
            if self.command_history:
                from cogist.application.commands import ChangeStyleCommand
                from cogist.application.commands.change_style_command import StyleChange

                change = StyleChange(
                    layer=self.current_layer,
                    style_updates={"shadow_enabled": enabled},
                )
                command = ChangeStyleCommand(
                    style_config=self.style_config,
                    changes=[change],
                )
                command.execute()
                self.command_history.push(command)
            else:
                # Fallback: direct update without undo/redo
                self._update_role_style_in_config(
                    self.current_layer, {"shadow_enabled": enabled}
                )

            self._apply_styles_to_mindmap()

    def _on_font_style_changed(self, style: dict):
        """Handle font style changes."""
        if self.current_layer != "canvas":
            # Check if this change affects node dimensions (requires size recalculation)
            dimension_keys = {
                "font_size",
                "font_family",
                "font_weight",
                "font_italic",
                "font_underline",
                "font_strikeout",
            }
            affects_dimensions = any(key in style for key in dimension_keys)

            # Font style changes always require style update (affects text rendering)
            requires_style_update = True

            # Skip command creation if we're updating from undo/redo
            if self._updating_from_undo_redo:
                # Direct update without creating a command
                self._update_role_style_in_config(self.current_layer, style)
            elif self.command_history:
                from cogist.application.commands import ChangeStyleCommand
                from cogist.application.commands.change_style_command import StyleChange

                # Create and execute style change command
                change = StyleChange(
                    layer=self.current_layer,
                    style_updates=style,
                )
                command = ChangeStyleCommand(
                    style_config=self.style_config,
                    changes=[change],
                )
                command.execute()
                self.command_history.push(command)
            else:
                # Fallback: direct update without undo/redo
                self._update_role_style_in_config(self.current_layer, style)

            self._apply_styles_to_mindmap(force_rebuild=affects_dimensions or requires_style_update)

    def _on_font_shadow_enabled_changed(self, enabled: bool):
        """Handle font shadow enabled state change from FontStyleSection."""
        if enabled:
            # Disable updates on parent to prevent layout flash
            self.setUpdatesEnabled(False)

            # Initialize content first if not already initialized (lazy init)
            if not self.shadow_section._initialized:
                self.shadow_section._init_content()
                self.shadow_section._initialized = True

            # Set collapsed state and make visible while updates are disabled
            self.shadow_section.setCollapsed(False)
            self.shadow_section.setVisible(True)

            # Re-enable updates - Qt will do a single layout update
            self.setUpdatesEnabled(True)
        else:
            self.shadow_section.setVisible(False)

        # Update using command system if available
        if self.current_layer != "canvas":
            if self.command_history:
                from cogist.application.commands import ChangeStyleCommand
                from cogist.application.commands.change_style_command import StyleChange

                change = StyleChange(
                    layer=self.current_layer,
                    style_updates={"shadow_enabled": enabled},
                )
                command = ChangeStyleCommand(
                    style_config=self.style_config,
                    changes=[change],
                )
                command.execute()
                self.command_history.push(command)
            else:
                # Fallback: direct update without undo/redo
                self._update_role_style_in_config(
                    self.current_layer, {"shadow_enabled": enabled}
                )

            self._apply_styles_to_mindmap()

    def _on_shadow_changed(self, shadow: dict):
        """Handle shadow style changes."""
        if self.current_layer != "canvas":
            # Skip command creation if we're updating from undo/redo
            if self._updating_from_undo_redo:
                # Direct update without creating a command
                self._update_role_style_in_config(self.current_layer, shadow)
            elif self.command_history:
                from cogist.application.commands import ChangeStyleCommand
                from cogist.application.commands.change_style_command import StyleChange

                change = StyleChange(
                    layer=self.current_layer,
                    style_updates=shadow,
                )
                command = ChangeStyleCommand(
                    style_config=self.style_config,
                    changes=[change],
                )
                command.execute()
                self.command_history.push(command)
            else:
                # Fallback: direct update without undo/redo
                self._update_role_style_in_config(self.current_layer, shadow)

            self._apply_styles_to_mindmap()

    def _on_border_style_changed(self, style: dict):
        """Handle border style changes."""
        if self.current_layer != "canvas":
            # Border style changes always require style update (affects colors, visibility)
            requires_style_update = True

            # Skip command creation if we're updating from undo/redo
            if self._updating_from_undo_redo:
                # Direct update without creating a command
                self._update_role_style_in_config(self.current_layer, style)
            elif self.command_history:
                from cogist.application.commands import ChangeStyleCommand
                from cogist.application.commands.change_style_command import StyleChange

                change = StyleChange(
                    layer=self.current_layer,
                    style_updates=style,
                )
                command = ChangeStyleCommand(
                    style_config=self.style_config,
                    changes=[change],
                )
                command.execute()
                self.command_history.push(command)
            else:
                # Fallback: direct update without undo/redo
                self._update_role_style_in_config(self.current_layer, style)

            self._apply_styles_to_mindmap(force_rebuild=requires_style_update)

    def _on_connector_style_changed(self, style: dict):
        """Handle connector style changes for the current layer."""
        if self.current_layer != "canvas":
            assert self.style_config is not None

            # Get role for current layer
            role = self._get_current_layer_role()
            if not role:
                return

            # Prepare style updates for command system
            connector_updates = {}
            if "connector_shape" in style:
                connector_updates["connector_shape"] = style["connector_shape"]
            if "connector_style" in style:
                connector_updates["connector_style"] = style["connector_style"]
            if "line_width" in style:
                connector_updates["line_width"] = style["line_width"]
            if "connector_color_index" in style:
                connector_updates["connector_color_index"] = style["connector_color_index"]
            if "connector_brightness" in style:
                connector_updates["connector_brightness"] = style["connector_brightness"]
            if "connector_opacity" in style:
                connector_updates["connector_opacity"] = style["connector_opacity"]

            # Use command system if available
            if (
                self._updating_from_undo_redo
                and connector_updates
                and role in self.style_config.role_styles
            ):
                # Direct update to role-based config without creating a command
                role_style = self.style_config.role_styles[role]

                if "connector_shape" in style:
                    role_style.connector_shape = style["connector_shape"]
                if "connector_style" in style:
                    role_style.connector_style = style["connector_style"]
                if "line_width" in style:
                    role_style.line_width = style["line_width"]
                if "connector_color_index" in style:
                    role_style.connector_color_index = style["connector_color_index"]
                if "connector_brightness" in style:
                    role_style.connector_brightness = style["connector_brightness"]
                if "connector_opacity" in style:
                    role_style.connector_opacity = style["connector_opacity"]
            elif self.command_history and connector_updates:
                from cogist.application.commands import ChangeStyleCommand
                from cogist.application.commands.change_style_command import StyleChange

                change = StyleChange(
                    layer=self.current_layer,
                    style_updates=connector_updates,
                )
                command = ChangeStyleCommand(
                    style_config=self.style_config,
                    changes=[change],
                )
                command.execute()
                self.command_history.push(command)
            elif connector_updates:
                # Fallback: direct update to role-based config without undo/redo
                if role in self.style_config.role_styles:
                    role_style = self.style_config.role_styles[role]

                    if "connector_shape" in style:
                        role_style.connector_shape = style["connector_shape"]
                    if "connector_style" in style:
                        role_style.connector_style = style["connector_style"]
                    if "line_width" in style:
                        role_style.line_width = style["line_width"]
                    if "connector_color_index" in style:
                        role_style.connector_color_index = style["connector_color_index"]
                    if "connector_brightness" in style:
                        role_style.connector_brightness = style["connector_brightness"]
                    if "connector_opacity" in style:
                        role_style.connector_opacity = style["connector_opacity"]

            self._apply_styles_to_mindmap()

    @staticmethod
    def _auto_contrast(bg_color: str) -> str:
        """Auto-select text color based on background brightness.

        Args:
            bg_color: Background color in hex format (#RRGGBB or #AARRGGBB)

        Returns:
            White (#FFFFFF) for dark backgrounds, black (#000000) for light
        """
        # Remove '#' if present
        bg_color = bg_color.lstrip("#")

        # Support both 6-digit (#RRGGBB) and 8-digit (#AARRGGBB) formats
        if len(bg_color) == 8:
            # 8-digit format: skip alpha channel, use RGB
            bg_color = bg_color[2:]  # Remove AA prefix
        elif len(bg_color) != 6:
            return "#000000"

        # Convert to RGB
        r = int(bg_color[0:2], 16)
        g = int(bg_color[2:4], 16)
        b = int(bg_color[4:6], 16)

        # Calculate luminance
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0

        # Return white for dark backgrounds, black for light
        return "#FFFFFF" if luminance < 0.5 else "#000000"

    def _set_initial_visibility(self):
        """Set initial visibility of sections based on default layer (canvas)."""
        # Hide spacing for canvas layer
        self.spacing_section.setVisible(False)
        self.spacing_section.setCollapsed(True)

        # Hide node/shadow/border/connector for canvas layer
        self.node_style_section.setVisible(False)
        self.font_style_section.setVisible(False)
        # Shadow section is controlled by shadow_enabled checkbox
        self.shadow_section.setVisible(False)
        self.border_section.setVisible(False)
        self.connector_section.setVisible(False)

    def _load_current_layer_style(self):
        """Load style for current layer into UI components."""
        # Get style data directly from global style_config
        layer_data = self._get_layer_data(self.current_layer)

        if self.current_layer == "canvas":
            # Load canvas background color into CanvasPanel
            canvas_style = {"bg_color": layer_data["bg_color"]}
            self.canvas_panel.set_style(canvas_style)

            # Hide shadow section for canvas
            self.shadow_section.setVisible(False)
        else:
            # Set root mode for node and border sections
            is_root = self.current_layer == "root"
            self.node_style_section.set_root_mode(is_root)
            self.border_section.set_root_mode(is_root)

            # Load node/border style into respective sections
            # Node style section handles background
            self.node_style_section.set_style(layer_data)

            # Border section handles border
            self.border_section.set_style(layer_data)

            # Load font style
            self.font_style_section.set_style(layer_data)
            # Sync shadow section visibility with shadow_enabled state
            shadow_enabled = layer_data["shadow_enabled"]
            self.shadow_section.setVisible(shadow_enabled)

            # Load shadow configuration
            shadow_config = {
                "enabled": shadow_enabled,
                "offset_x": layer_data["shadow_offset_x"],
                "offset_y": layer_data["shadow_offset_y"],
                "blur": layer_data["shadow_blur"],
                "color": layer_data["shadow_color"],
            }
            self.shadow_section.set_shadow(shadow_config)

            # Sync border section visibility with rainbow_border_enabled state
            if "rainbow_border_enabled" in layer_data:
                self.border_section.setVisible(layer_data["rainbow_border_enabled"])

            # Hide connector section for root layer (edge belongs to target node)
            self.connector_section.setVisible(self.current_layer != "root")

            # Load spacing configuration (per-layer)
            spacing_config = {
                "parent_child": layer_data["parent_child_spacing"],
                "sibling": layer_data["sibling_spacing"],
            }
            self.spacing_section.set_spacing(spacing_config)

            # Hide entire Spacing section for root layer (root has no parent or siblings)
            self.spacing_section.setVisible(self.current_layer != "root")

        # Load connector style (per-layer, only for non-canvas and non-root)
        # Edge belongs to target node, so root layer doesn't need connector config
        if self.current_layer not in ["canvas", "root"]:
            connector_style = {
                "connector_shape": layer_data["connector_type"],
                "connector_style": layer_data["connector_style"],
                "line_width": layer_data["connector_width"],
                "connector_color_index": layer_data["connector_color_index"],
                "connector_brightness": layer_data["connector_color_index"],  # Will be replaced below
                "connector_opacity": layer_data["connector_color_index"],  # Will be replaced below
                "use_rainbow": layer_data.get("use_rainbow", False),  # Pass rainbow mode state
            }

            # Get brightness and opacity from role_styles
            assert self.style_config is not None
            role = self._get_current_layer_role()
            if role and role in self.style_config.role_styles:
                role_style = self.style_config.role_styles[role]
                connector_style["connector_brightness"] = role_style.connector_brightness
                connector_style["connector_opacity"] = role_style.connector_opacity

            self.connector_section.set_style(connector_style)

    def refresh_current_layer(self):
        """Public method to refresh UI controls with current layer's style from global config.

        This should be called when style_config is reset (e.g., when creating a new file).
        """
        self._load_current_layer_style()

    def _apply_styles_to_mindmap(self, force_rebuild: bool = False):
        """Unified method to apply all styles to mindmap_view.

        This method:
        1. Gets mindmap_view from app_context
        2. Applies all styles (node, connector, spacing) to style_config
        3. Updates node items' template_style if needed
        4. Refreshes the layout

        Args:
            force_rebuild: If True, update all node items' template_style and force full rebuild
                          (needed when style changes affect node dimensions like max_text_width)
        """
        try:
            from cogist.application.services.app_context import get_app_context

            app_context = get_app_context()
            if not app_context:
                return

            mindmap_view = app_context.get_mindmap_view()
            if not mindmap_view:
                return

            # Apply node styles (includes canvas background)
            self._apply_node_styles_to_mindmap(mindmap_view)

            # Apply connector styles (per-layer)
            self._apply_connector_styles_to_mindmap(mindmap_view)

            # Apply spacing configuration (per-layer, skip canvas)
            # Sync spacing from panel's style_config to mindmap_view's style_config
            # CRITICAL: If style affects dimensions, update all node items' template_style first
            if force_rebuild and hasattr(mindmap_view, "node_items"):
                for node_item in mindmap_view.node_items.values():
                    if hasattr(node_item, "update_style"):
                        node_item.update_style(mindmap_view.style_config)

            # Refresh layout to apply all changes
            # CRITICAL: Set skip_measurement=False when style changes affect node dimensions
            # (e.g., padding, font_size, max_text_width) so nodes recalculate sizes and layout updates
            if hasattr(mindmap_view, "_refresh_layout"):
                mindmap_view._refresh_layout(skip_measurement=False)

        except Exception as e:
            # Error already shown in UI, no need to print to console
            import traceback
            print(f"[_apply_styles_to_mindmap] ERROR: {e}")
            traceback.print_exc()

    def _apply_node_styles_to_mindmap(self, mindmap_view):
        """Apply node layer styles using RoleBasedStyle architecture."""
        from cogist.domain.styles import NodeRole

        if not mindmap_view.style_config:
            return

        style = mindmap_view.style_config

        # Build role mapping: panel layer -> NodeRole
        layer_to_role = {
            "root": NodeRole.ROOT,
            "level_1": NodeRole.PRIMARY,
            "level_2": NodeRole.SECONDARY,
            "level_3_plus": NodeRole.TERTIARY,
            "critical": NodeRole.TERTIARY,
            "minor": NodeRole.TERTIARY,
        }

        # Convert each layer to RoleBasedStyle
        for layer_name, _role in layer_to_role.items():
            # Skip priority layers (critical/minor) - they use tertiary styles
            if layer_name in ["critical", "minor"]:
                continue

            # CRITICAL: Do NOT recreate RoleBasedStyle objects!
            # Panel already updated the global config directly via _update_role_style_in_config.
            # Recreating would overwrite the changes with old values.

        # Update canvas background color
        canvas_data = self._get_layer_data("canvas")
        if "bg_color" in canvas_data:
            canvas_color = canvas_data["bg_color"]
            style.special_colors["canvas_bg"] = canvas_color

            # Use mindmap_view's method to update scene background
            if hasattr(mindmap_view, '_update_canvas_background'):
                mindmap_view._update_canvas_background()

        # Update all existing node items with new style
        if hasattr(mindmap_view, "node_items"):
            for _node_id, node_item in mindmap_view.node_items.items():
                if hasattr(node_item, "update_style"):
                    node_item.update_style(style)

        # Note: Layout refresh is handled by _apply_styles_to_mindmap()

    def _apply_connector_styles_to_mindmap(self, mindmap_view):
        """Apply connector (edge) styles to all edges in the mind map (per-layer)."""
        if not hasattr(mindmap_view, "edge_items"):
            return

        if self.current_layer == "canvas":
            return

        assert self.style_config is not None

        for edge_item in mindmap_view.edge_items:
            if not hasattr(edge_item, "update_style"):
                continue

            # Get TARGET node depth to determine which connector style to use
            # Edge style is determined by the child node's layer (edge belongs to target)
            target_node = edge_item.target_item
            if not hasattr(target_node, "depth"):
                continue

            # Get connector config from role-based style
            from cogist.domain.styles.extended_styles import NodeRole

            target_depth = target_node.depth
            role_map = {0: NodeRole.ROOT, 1: NodeRole.PRIMARY, 2: NodeRole.SECONDARY}
            role = role_map.get(target_depth, NodeRole.TERTIARY)

            # Get connector config from role style
            assert (
                role in self.style_config.role_styles
            ), f"Role {role} should exist in style_config.role_styles"
            role_style = self.style_config.role_styles[role]

            # Build complete connector style dict with all fields
            connector_style = {
                "connector_shape": role_style.connector_shape,
                "connector_style": role_style.connector_style,
                "line_width": role_style.line_width,
                "connector_color_index": role_style.connector_color_index,
                "connector_brightness": role_style.connector_brightness,
                "connector_opacity": role_style.connector_opacity,
            }

            edge_item.update_style(connector_style)

            # Trigger repaint (paint() will read latest config directly)
            edge_item.update()
