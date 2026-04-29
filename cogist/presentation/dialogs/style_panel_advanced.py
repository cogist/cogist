"""
Style Panel - Advanced Mode for Template Creation (Refactored)

A dockable panel for real-time style debugging and template creation.
Uses modular components with lazy initialization for better performance.

Refactored version: Uses component-based architecture from style_widgets/
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from .style_widgets import (
    BorderSection,
    ColorSchemeSection,
    ConnectorSection,
    LayerSelector,
    NodeStyleSection,
    ShadowSection,
    SpacingSection,
)


class AdvancedStyleTab(QWidget):
    """Advanced mode tab using modular components with lazy initialization.

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

        This method reads from style_config.resolved_template and resolved_color_scheme,
        ensuring panel always uses the authoritative data source.

        Args:
            layer_name: Layer name (canvas, root, level_1, level_2, level_3_plus, etc.)

        Returns:
            Dictionary with all style fields for the layer
        """
        assert self.style_config is not None, "style_config must be set"

        if layer_name == "canvas":
            return {"bg_color": self.style_config.canvas_bg_color}

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

        template = self.style_config.resolved_template
        color_scheme = self.style_config.resolved_color_scheme

        if not template or role not in template.role_styles:
            raise ValueError(f"No style data for role {role} in template")

        role_style = template.role_styles[role]

        # Build complete layer data from global style config
        layer_data = {
            # Shape
            "shape": role_style.shape.basic_shape,
            "radius": role_style.shape.border_radius,
            # Colors - role_configs contains all roles
            "bg_color": color_scheme.role_configs[role].bg_color,
            # text_color from role config or auto contrast
            "text_color": (
                color_scheme.role_configs[role].text_color
                if color_scheme.role_configs[role].text_color
                else self._auto_contrast(color_scheme.role_configs[role].bg_color)
            ),
            # border_color from role config (None if not set)
            "border_color": color_scheme.role_configs[role].border_color,
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
            "shadow_color": role_style.shadow_color or "#000000",
            # Border
            "border_style": role_style.border.border_style,
            "border_width": role_style.border.border_width,
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
            # Spacing - read from role-based configuration
            "parent_child_spacing": self._get_level_spacing_for_layer(layer_name),
            "sibling_spacing": self._get_sibling_spacing_for_layer(layer_name),
            # Rainbow branch (only for level_1)
            "use_rainbow": color_scheme.use_rainbow_branches
            if layer_name == "level_1"
            else False,
            "rainbow_pool": color_scheme.branch_colors
            if layer_name == "level_1"
            else [],
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

        # Try role-based spacing first (new architecture)
        role = self._get_current_layer_role()
        if (
            role
            and self.style_config.resolved_template
            and role in self.style_config.resolved_template.role_styles
        ):
            return self.style_config.resolved_template.role_styles[
                role
            ].parent_child_spacing

        # Default value
        return 80.0

    def _get_sibling_spacing_for_layer(self, layer_name: str) -> float:
        """Get sibling spacing for a layer from role-based configuration."""
        assert self.style_config is not None
        if layer_name == "root":
            return 0

        # Try role-based spacing first (new architecture)
        role = self._get_current_layer_role()
        if (
            role
            and self.style_config.resolved_template
            and role in self.style_config.resolved_template.role_styles
        ):
            return self.style_config.resolved_template.role_styles[role].sibling_spacing

        # Default value
        return 60.0

    def _get_connector_type_for_layer(self, layer_name: str) -> str:
        """Get connector type for a layer from role-based configuration."""
        assert self.style_config is not None

        # Get from role-based config
        role = self._get_current_layer_role()
        if (
            role
            and self.style_config.resolved_template
            and role in self.style_config.resolved_template.role_styles
        ):
            return self.style_config.resolved_template.role_styles[role].connector_shape

        # Default value
        return "bezier"

    def _get_connector_style_for_layer(self, layer_name: str) -> str:
        """Get connector style for a layer from role-based configuration."""
        assert self.style_config is not None

        # Get from role-based config
        role = self._get_current_layer_role()
        if (
            role
            and self.style_config.resolved_template
            and role in self.style_config.resolved_template.role_styles
        ):
            return self.style_config.resolved_template.role_styles[role].connector_style

        # Default value
        return "solid"

    def _get_connector_width_for_layer(self, layer_name: str) -> float:
        """Get connector width for a layer from role-based configuration."""
        assert self.style_config is not None

        # Get from role-based config
        role = self._get_current_layer_role()
        if (
            role
            and self.style_config.resolved_template
            and role in self.style_config.resolved_template.role_styles
        ):
            return self.style_config.resolved_template.role_styles[role].line_width

        # Default value
        return 2.0

    def _get_connector_color_for_layer(self, layer_name: str) -> str:
        """Get connector color for a layer from role-based configuration."""
        assert self.style_config is not None

        # Get from role-based config
        role = self._get_current_layer_role()
        if (
            role
            and self.style_config.resolved_template
            and role in self.style_config.resolved_template.role_styles
        ):
            role_style = self.style_config.resolved_template.role_styles[role]
            # Connector color comes from ColorScheme if not overridden
            if role_style.connector_color:
                return role_style.connector_color
            # Fall back to edge color from color scheme
            if self.style_config.resolved_color_scheme:
                return self.style_config.resolved_color_scheme.edge_color

        # Default value
        return "#666666"

    def _update_role_style_in_config(self, layer_name: str, updates: dict):
        """Update specific fields of a role's style in global style_config.

        Args:
            layer_name: Layer name (root, level_1, etc.)
            updates: Dictionary of fields to update
        """
        assert self.style_config is not None

        if layer_name == "canvas":
            # Handle canvas background color separately
            if "bg_color" in updates:
                self.style_config.canvas_bg_color = updates["bg_color"]
                if self.style_config.resolved_color_scheme:
                    self.style_config.resolved_color_scheme.canvas_bg_color = updates[
                        "bg_color"
                    ]
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

        template = self.style_config.resolved_template
        color_scheme = self.style_config.resolved_color_scheme

        if not template or role not in template.role_styles:
            return

        role_style = template.role_styles[role]

        # Apply updates to role_style and color_scheme
        for key, value in updates.items():
            if key == "shape":
                # Handle shape type update
                if hasattr(role_style, "shape"):
                    role_style.shape.basic_shape = value
            elif key == "radius":
                # Handle border radius update
                if hasattr(role_style, "shape"):
                    role_style.shape.border_radius = value
            elif key == "bg_color":
                # Background color goes to color_scheme
                if color_scheme:
                    color_scheme.role_configs[role].bg_color = value
            elif key == "text_color":
                # Text color goes to color_scheme
                if color_scheme:
                    color_scheme.role_configs[role].text_color = value
            elif key == "border_color":
                # Border color goes to color_scheme
                if color_scheme:
                    color_scheme.role_configs[role].border_color = value
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
        self.color_scheme_section = ColorSchemeSection()
        self.spacing_section = SpacingSection()
        self.node_style_section = NodeStyleSection()
        self.shadow_section = ShadowSection()
        self.border_section = BorderSection()
        self.connector_section = ConnectorSection()

        layout.addWidget(self.layer_selector)
        layout.addWidget(self.color_scheme_section)
        layout.addWidget(self.spacing_section)
        layout.addWidget(self.node_style_section)
        layout.addWidget(self.shadow_section)
        layout.addWidget(self.border_section)
        layout.addWidget(self.connector_section)
        layout.addStretch()

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
            AdvancedStyleTab {
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

        # Color scheme
        self.color_scheme_section.color_changed.connect(self._on_color_scheme_changed)

        # Spacing configuration
        self.spacing_section.spacing_changed.connect(self._on_spacing_changed)

        # Node style
        self.node_style_section.style_changed.connect(self._on_node_style_changed)
        self.node_style_section.shadow_enabled_changed.connect(
            self._on_shadow_enabled_changed
        )

        # Shadow style
        self.shadow_section.shadow_changed.connect(self._on_shadow_changed)

        # Border style
        self.border_section.style_changed.connect(self._on_border_style_changed)

        # Connector style
        self.connector_section.style_changed.connect(self._on_connector_style_changed)

    def _on_layer_changed(self, layer_name: str):
        """Handle layer selection change."""
        # No need to save - styles are already saved directly to global config
        # Update current layer
        self.current_layer = layer_name

        # Show/hide sections based on layer type
        is_canvas = layer_name == "canvas"
        is_priority = layer_name in ["critical", "minor"]

        # Spacing: only show for non-canvas layers (not a global setting)
        self.spacing_section.setVisible(not is_canvas)

        # Node/Border/Connector: only show for non-canvas layers
        self.node_style_section.setVisible(not is_canvas)
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
        assert self.style_config is not None

        # Get current role
        role = self._get_current_layer_role()
        if not role:
            # Canvas layer - handle canvas_bg separately
            if "canvas_bg" in colors:
                # Update both style_config and resolved_color_scheme
                self.style_config.canvas_bg_color = colors["canvas_bg"]
                if self.style_config.resolved_color_scheme:
                    self.style_config.resolved_color_scheme.canvas_bg_color = colors[
                        "canvas_bg"
                    ]
                self._apply_styles_to_mindmap()
            return

        # Get color_scheme
        if not self.style_config.resolved_color_scheme:
            return

        color_scheme = self.style_config.resolved_color_scheme

        # Handle rainbow branches first (before command system, as it's a global setting)
        if "use_rainbow" in colors:
            color_scheme.use_rainbow_branches = colors["use_rainbow"]

        if "rainbow_pool" in colors:
            color_scheme.branch_colors = colors["rainbow_pool"]

        # Use command system if available
        if self.command_history:
            from cogist.application.commands import ChangeStyleCommand
            from cogist.application.commands.change_style_command import StyleChange

            style_updates = {}

            # Build style updates based on changed colors
            if "bg_color" in colors:
                style_updates["bg_color"] = colors["bg_color"]
            if "text_color" in colors:
                style_updates["text_color"] = colors["text_color"]
            if "border_color" in colors:
                style_updates["border_color"] = colors["border_color"]
            if "connector_color" in colors:
                style_updates["connector_color"] = colors["connector_color"]

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
        else:
            # Fallback: direct update without undo/redo
            # Handle node background color
            if "bg_color" in colors:
                color_scheme.role_configs[role].bg_color = colors["bg_color"]

            # Handle text/foreground color
            if "text_color" in colors:
                color_scheme.role_configs[role].text_color = colors["text_color"]

            # Handle border color
            if "border_color" in colors:
                color_scheme.role_configs[role].border_color = colors["border_color"]

            # Handle connector color
            if (
                "connector_color" in colors
                and self.style_config.resolved_template
                and role in self.style_config.resolved_template.role_styles
            ):
                role_style = self.style_config.resolved_template.role_styles[role]
                role_style.connector_color = colors["connector_color"]

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
                and self.style_config.resolved_template
                and role in self.style_config.resolved_template.role_styles
            ):
                # Direct update to role-based config
                role_style = self.style_config.resolved_template.role_styles[role]
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
                if (
                    self.style_config.resolved_template
                    and role in self.style_config.resolved_template.role_styles
                ):
                    role_style = self.style_config.resolved_template.role_styles[role]
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

            self._apply_styles_to_mindmap(force_rebuild=affects_dimensions)

    def _on_shadow_enabled_changed(self, enabled: bool):
        """Handle font shadow enabled state change."""
        self.shadow_section.setVisible(enabled)
        if enabled:
            self.shadow_section.setCollapsed(False)

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

            self._apply_styles_to_mindmap()

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
            if "connector_color" in style:
                connector_updates["connector_color"] = style["connector_color"]

            # Use command system if available
            if (
                self._updating_from_undo_redo
                and connector_updates
                and self.style_config.resolved_template
                and role in self.style_config.resolved_template.role_styles
            ):
                # Direct update to role-based config without creating a command
                role_style = self.style_config.resolved_template.role_styles[role]

                if "connector_shape" in style:
                    role_style.connector_shape = style["connector_shape"]
                if "connector_style" in style:
                    role_style.connector_style = style["connector_style"]
                if "line_width" in style:
                    role_style.line_width = style["line_width"]
                if "connector_color" in style:
                    role_style.connector_color = style["connector_color"]
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
                if (
                    self.style_config.resolved_template
                    and role in self.style_config.resolved_template.role_styles
                ):
                    role_style = self.style_config.resolved_template.role_styles[role]

                    if "connector_shape" in style:
                        role_style.connector_shape = style["connector_shape"]
                    if "connector_style" in style:
                        role_style.connector_style = style["connector_style"]
                    if "line_width" in style:
                        role_style.line_width = style["line_width"]
                    if "connector_color" in style:
                        role_style.connector_color = style["connector_color"]

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
        # Shadow section is controlled by shadow_enabled checkbox
        self.shadow_section.setVisible(False)
        self.border_section.setVisible(False)
        self.connector_section.setVisible(False)

    def _load_current_layer_style(self):
        """Load style for current layer into UI components."""
        # Get style data directly from global style_config
        layer_data = self._get_layer_data(self.current_layer)

        # Notify color_scheme_section of current layer role for proper UI visibility
        self.color_scheme_section.set_role(self.current_layer)

        if self.current_layer == "canvas":
            # Load canvas style into color_scheme_section
            if "bg_color" in layer_data:
                self.color_scheme_section.set_colors(
                    {"canvas_bg": layer_data["bg_color"]}
                )
            # Hide shadow section for canvas
            self.shadow_section.setVisible(False)
        else:
            # Load colors into color_scheme_section
            color_data = {}
            if "bg_color" in layer_data:
                color_data["bg_color"] = layer_data["bg_color"]
            if "text_color" in layer_data:
                color_data["text_color"] = layer_data["text_color"]
            if "border_color" in layer_data:
                color_data["border_color"] = layer_data["border_color"]
            if "connector_color" in layer_data:
                color_data["connector_color"] = layer_data["connector_color"]

            # Note: use_rainbow is a global ColorScheme property, not per-layer
            # It should NOT be updated when switching layers
            # Only update rainbow pool for level_1 (for display purposes)
            if self.current_layer == "level_1" and "rainbow_pool" in layer_data:
                color_data["rainbow_pool"] = layer_data["rainbow_pool"]

            if color_data:
                self.color_scheme_section.set_colors(color_data)

            # Load node style (without colors - they're now in color_scheme_section)
            self.node_style_section.set_style(layer_data)
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

            # Load border style
            self.border_section.set_style(layer_data)

            # Load spacing configuration (per-layer)
            spacing_config = {
                "parent_child": layer_data["parent_child_spacing"],
                "sibling": layer_data["sibling_spacing"],
            }
            self.spacing_section.set_spacing(spacing_config)

            # Root layer specific: hide sibling spacing control (elegant way)
            self.spacing_section.set_hide_sibling(self.current_layer == "root")

        # Load connector style (per-layer, only for non-canvas)
        if self.current_layer != "canvas":
            connector_style = {
                "connector_shape": layer_data["connector_type"],
                "connector_style": layer_data["connector_style"],
                "line_width": layer_data["connector_width"],
                "connector_color": layer_data["connector_color"],
            }
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

        except Exception:
            # Error already shown in UI, no need to print to console
            pass

    def _apply_node_styles_to_mindmap(self, mindmap_view):
        """Apply node layer styles using RoleBasedStyle architecture."""
        from cogist.domain.styles import ColorScheme, NodeRole, Template

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

        # Initialize role_styles dict if template doesn't have it
        if not style.resolved_template:
            style.resolved_template = Template(
                name="Custom", description="", role_styles={}
            )

        # Convert each layer to RoleBasedStyle + update ColorScheme
        for layer_name, role in layer_to_role.items():
            # Skip priority layers (critical/minor) - they use tertiary styles
            if layer_name in ["critical", "minor"]:
                continue

            # Get layer data directly from global style_config
            layer_data = self._get_layer_data(layer_name)

            # CRITICAL: Do NOT recreate RoleBasedStyle objects!
            # Panel already updated the global config directly via _update_role_style_in_config.
            # Recreating would overwrite the changes with old values.
            # Only update color scheme here.

            # Update color scheme
            if not style.resolved_color_scheme:
                style.resolved_color_scheme = ColorScheme(
                    name="Custom", description=""
                )

            # Set node color
            if "bg_color" in layer_data:
                style.resolved_color_scheme.role_configs[role].bg_color = layer_data["bg_color"]

            # Set text color
            if "text_color" in layer_data:
                style.resolved_color_scheme.role_configs[role].text_color = layer_data["text_color"]

            # Set border color (only if not None)
            if "border_color" in layer_data and layer_data["border_color"] is not None:
                style.resolved_color_scheme.role_configs[role].border_color = layer_data[
                    "border_color"
                ]

        # Update canvas background color
        canvas_data = self._get_layer_data("canvas")
        if "bg_color" in canvas_data:
            canvas_color = canvas_data["bg_color"]
            style.canvas_bg_color = canvas_color
            if style.resolved_color_scheme:
                style.resolved_color_scheme.canvas_bg_color = canvas_color

            # CRITICAL: Update the scene background immediately
            from PySide6.QtGui import QBrush, QColor

            if hasattr(mindmap_view, "scene"):
                mindmap_view.scene.setBackgroundBrush(QBrush(QColor(canvas_color)))

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

            # Get SOURCE node depth to determine which connector style to use
            # The edge style is determined by the parent node's layer
            source_node = edge_item.source_item
            if not hasattr(source_node, "depth"):
                continue

            # Get connector config from role-based style
            from cogist.domain.styles.extended_styles import NodeRole

            source_depth = source_node.depth
            role_map = {0: NodeRole.ROOT, 1: NodeRole.PRIMARY, 2: NodeRole.SECONDARY}
            role = role_map.get(source_depth, NodeRole.TERTIARY)

            connector_shape = "bezier"  # Default
            if (
                self.style_config.resolved_template
                and role in self.style_config.resolved_template.role_styles
            ):
                role_style = self.style_config.resolved_template.role_styles[role]
                connector_shape = role_style.connector_shape

            # Build connector style dict (only shape is needed for update_style)
            connector_style = {
                "connector_shape": connector_shape,
            }

            edge_item.update_style(connector_style)

            # Trigger repaint (paint() will read latest config directly)
            edge_item.update()
