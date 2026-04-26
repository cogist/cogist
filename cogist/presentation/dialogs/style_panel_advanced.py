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
    CanvasSection,
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
    - CanvasSection: Canvas background
    - NodeStyleSection: Node appearance
    - BorderSection: Border styling
    - ConnectorSection: Edge styling

    All components implement lazy initialization - they only create
    their internal widgets when expanded by the user.
    """

    # Panel dimensions
    PANEL_WIDTH = 260  # Original carefully designed width

    def __init__(self, style_config=None, config_manager=None, parent=None):
        super().__init__(parent)

        # Set initial width (fixed, non-resizable)
        self.setMinimumWidth(self.PANEL_WIDTH)
        self.setMaximumWidth(self.PANEL_WIDTH)

        # Store reference to global style configuration
        self.style_config = style_config
        if not self.style_config:
            raise ValueError("style_config is required - panel must have access to global style data")

        # Store reference to config manager
        self.config_manager = config_manager

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
            # Colors - node_colors is required and contains all roles
            "bg_color": color_scheme.node_colors[role],
            # text_colors is optional - auto contrast if not provided
            "text_color": (
                color_scheme.text_colors[role]
                if color_scheme.text_colors and role in color_scheme.text_colors
                else self._auto_contrast(color_scheme.node_colors[role])
            ),
            # border_colors is optional - None if not provided
            "border_color": (
                color_scheme.border_colors[role]
                if color_scheme.border_colors and role in color_scheme.border_colors
                else None
            ),
            # Font
            "font_family": role_style.font_family,
            "font_size": role_style.font_size,
            "font_weight": role_style.font_weight,
            "font_italic": role_style.font_style == "Italic",
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
            # Connector - read from per-depth configuration
            "connector_type": self._get_connector_type_for_layer(layer_name),
            "connector_style": self._get_connector_style_for_layer(layer_name),
            "connector_width": self._get_connector_width_for_layer(layer_name),
            "connector_color": self._get_connector_color_for_layer(layer_name),
            # Spacing - read from per-depth configuration
            "parent_child_spacing": self._get_level_spacing_for_layer(layer_name),
            "sibling_spacing": self._get_sibling_spacing_for_layer(layer_name),
        }

        return layer_data

    def _get_level_spacing_for_layer(self, layer_name: str) -> float:
        """Get parent-child spacing for a layer from per-depth configuration."""
        assert self.style_config is not None
        # Map layer names to depth; critical/minor use level_3_plus spacing (depth 3)
        depth_map = {
            "root": 0,
            "level_1": 1,
            "level_2": 2,
            "level_3_plus": 3,
            "critical": 3,  # Use same spacing as level_3_plus
            "minor": 3,     # Use same spacing as level_3_plus
        }
        depth = depth_map[layer_name]

        return self.style_config.level_spacing_by_depth[depth]

    def _get_sibling_spacing_for_layer(self, layer_name: str) -> float:
        """Get sibling spacing for a layer from per-depth configuration."""
        assert self.style_config is not None
        if layer_name == "root":
            return 0

        # Map layer to the depth of children (siblings are at child's depth)
        # critical/minor use level_3_plus spacing (depth 3)
        depth_map = {
            "level_1": 1,
            "level_2": 2,
            "level_3_plus": 3,
            "critical": 3,  # Use same spacing as level_3_plus
            "minor": 3,     # Use same spacing as level_3_plus
        }
        depth = depth_map[layer_name]

        return self.style_config.sibling_spacing_by_depth[depth]

    def _get_connector_type_for_layer(self, layer_name: str) -> str:
        """Get connector type for a layer from per-depth configuration."""
        assert self.style_config is not None
        # Layer controls the edge FROM that layer TO the next level
        # critical/minor use level_3_plus connector config (depth 3)
        depth_map = {
            "root": 0,
            "level_1": 1,
            "level_2": 2,
            "level_3_plus": 3,
            "critical": 3,
            "minor": 3,
        }
        depth = depth_map.get(layer_name, 2)

        if hasattr(self.style_config, 'connector_config_by_depth'):
            return self.style_config.connector_config_by_depth.get(depth, {}).get("connector_shape", "bezier")
        return "bezier"

    def _get_connector_style_for_layer(self, layer_name: str) -> str:
        """Get connector style for a layer from per-depth configuration."""
        assert self.style_config is not None
        # critical/minor use level_3_plus connector config (depth 3)
        depth_map = {
            "root": 0,
            "level_1": 1,
            "level_2": 2,
            "level_3_plus": 3,
            "critical": 3,
            "minor": 3,
        }
        depth = depth_map.get(layer_name, 2)

        if hasattr(self.style_config, 'connector_config_by_depth'):
            return self.style_config.connector_config_by_depth.get(depth, {}).get("connector_style", "solid")
        return "solid"

    def _get_connector_width_for_layer(self, layer_name: str) -> float:
        """Get connector width for a layer from per-depth configuration."""
        assert self.style_config is not None
        depth_map = {"root": 0, "level_1": 1, "level_2": 2, "level_3_plus": 3}
        depth = depth_map.get(layer_name, 2)

        if hasattr(self.style_config, 'connector_config_by_depth'):
            return self.style_config.connector_config_by_depth.get(depth, {}).get("line_width", 2.0)
        return 2.0

    def _get_connector_color_for_layer(self, layer_name: str) -> str:
        """Get connector color for a layer from per-depth configuration."""
        assert self.style_config is not None
        depth_map = {"root": 0, "level_1": 1, "level_2": 2, "level_3_plus": 3}
        depth = depth_map.get(layer_name, 2)

        if hasattr(self.style_config, 'connector_config_by_depth'):
            return self.style_config.connector_config_by_depth.get(depth, {}).get("color", "#666666")
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
                    self.style_config.resolved_color_scheme.canvas_bg_color = updates["bg_color"]
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
                if hasattr(role_style, 'shape'):
                    role_style.shape.basic_shape = value
            elif key == "radius":
                # Handle border radius update
                if hasattr(role_style, 'shape'):
                    role_style.shape.border_radius = value
            elif key == "bg_color":
                # Background color goes to color_scheme
                if color_scheme:
                    color_scheme.node_colors[role] = value
            elif key == "text_color":
                # Text color goes to color_scheme
                if color_scheme:
                    if not color_scheme.text_colors:
                        color_scheme.text_colors = {}
                    color_scheme.text_colors[role] = value
            elif key == "border_color":
                # Border color goes to color_scheme
                if color_scheme:
                    if not color_scheme.border_colors:
                        color_scheme.border_colors = {}
                    color_scheme.border_colors[role] = value
            elif key == "font_italic":
                # Map boolean font_italic to string font_style
                if hasattr(role_style, 'font_style'):
                    role_style.font_style = "Italic" if value else "Normal"
            elif key == "max_text_width":
                # Handle max text width update
                if hasattr(role_style, 'max_text_width'):
                    role_style.max_text_width = value
            elif hasattr(role_style, key):
                setattr(role_style, key, value)
            elif key.startswith("shadow_"):
                # Handle shadow attributes
                attr_name = key
                if hasattr(role_style, attr_name):
                    setattr(role_style, attr_name, value)
            elif key.startswith("border_") and hasattr(role_style, 'border'):
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
        self.canvas_section = CanvasSection()
        self.spacing_section = SpacingSection()
        self.node_style_section = NodeStyleSection()
        self.shadow_section = ShadowSection()
        self.border_section = BorderSection()
        self.connector_section = ConnectorSection()

        layout.addWidget(self.layer_selector)
        layout.addWidget(self.canvas_section)
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

        # Canvas background
        self.canvas_section.color_changed.connect(self._on_canvas_color_changed)

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

        # Canvas background: only show for canvas layer
        self.canvas_section.setVisible(is_canvas)
        self.canvas_section.setCollapsed(False)

        # Spacing: only show for non-canvas layers (not a global setting)
        self.spacing_section.setVisible(not is_canvas)

        # Node/Border/Connector: only show for non-canvas layers
        self.node_style_section.setVisible(not is_canvas)
        # Shadow section visibility is controlled by shadow_enabled state in _load_current_layer_style
        self.border_section.setVisible(not is_canvas)
        self.connector_section.setVisible(not is_canvas and not is_priority)

        # Load style for selected layer
        self._load_current_layer_style()

    def _on_canvas_color_changed(self, color: str):
        """Handle canvas background color change."""
        assert self.style_config is not None
        # Directly update global style_config
        self.style_config.canvas_bg_color = color
        if self.style_config.resolved_color_scheme:
            self.style_config.resolved_color_scheme.canvas_bg_color = color
        self._apply_styles_to_mindmap()

    def _on_spacing_changed(self, spacing: dict):
        """Handle spacing configuration change for the current layer."""
        assert self.style_config is not None
        if self.current_layer != "canvas":
            # Directly update our own style_config since we have direct access
            # Map layers to depths for spacing application
            # level_3_plus maps to depth 3 and affects all deeper levels (3, 4, 5, ...)
            depth_map = {
                "root": 0,
                "level_1": 1,
                "level_2": 2,
                "level_3_plus": 3,
            }
            depth = depth_map[self.current_layer]

            # Determine which depths to update (level_3_plus affects all depths >= 3)
            is_level_3_plus = self.current_layer == "level_3_plus"
            if is_level_3_plus:
                # Collect all depths >= 3 from existing config
                all_depths = set()
                all_depths.update(self.style_config.level_spacing_by_depth.keys())
                all_depths.update(self.style_config.sibling_spacing_by_depth.keys())
                # Also include depths from connector config
                if hasattr(self.style_config, 'connector_config_by_depth'):
                    all_depths.update(self.style_config.connector_config_by_depth.keys())
                depths_to_update = [d for d in all_depths if d >= 3]
                # If no depths >= 3 exist yet, just use depth 3
                if not depths_to_update:
                    depths_to_update = [3]
            else:
                depths_to_update = [depth]

            if "parent_child" in spacing:
                # Initialize dictionary if not exists
                if not hasattr(self.style_config, 'level_spacing_by_depth'):
                    self.style_config.level_spacing_by_depth = {}
                # Update spacing for all target depths (true layer isolation)
                for d in depths_to_update:
                    self.style_config.level_spacing_by_depth[d] = spacing["parent_child"]

            if "sibling" in spacing:
                # Initialize dictionary if not exists
                if not hasattr(self.style_config, 'sibling_spacing_by_depth'):
                    self.style_config.sibling_spacing_by_depth = {}
                # Update spacing for all target depths (true layer isolation)
                for d in depths_to_update:
                    self.style_config.sibling_spacing_by_depth[d] = spacing["sibling"]

            # Trigger layout refresh through _apply_styles_to_mindmap
            self._apply_styles_to_mindmap()

    def _on_node_style_changed(self, style: dict):
        """Handle node style changes."""
        if self.current_layer != "canvas":
            # Update global style_config directly
            self._update_role_style_in_config(self.current_layer, style)

            # Check if this change affects node dimensions (requires size recalculation)
            dimension_keys = {"max_text_width", "padding_w", "padding_h", "font_size", "font_family", "font_weight", "font_italic", "font_underline", "font_strikeout"}
            affects_dimensions = any(key in style for key in dimension_keys)

            self._apply_styles_to_mindmap(force_rebuild=affects_dimensions)

    def _on_shadow_enabled_changed(self, enabled: bool):
        """Handle font shadow enabled state change."""
        self.shadow_section.setVisible(enabled)
        if enabled:
            self.shadow_section.setCollapsed(False)

        # Update global style_config directly
        if self.current_layer != "canvas":
            self._update_role_style_in_config(self.current_layer, {"shadow_enabled": enabled})
            self._apply_styles_to_mindmap()

    def _on_shadow_changed(self, shadow: dict):
        """Handle shadow style changes."""
        if self.current_layer != "canvas":
            # Update global style_config directly
            self._update_role_style_in_config(self.current_layer, shadow)
            self._apply_styles_to_mindmap()

    def _on_border_style_changed(self, style: dict):
        """Handle border style changes."""
        if self.current_layer != "canvas":
            # Update global style_config directly
            self._update_role_style_in_config(self.current_layer, style)
            self._apply_styles_to_mindmap()

    def _on_connector_style_changed(self, style: dict):
        """Handle connector style changes for the current layer."""
        if self.current_layer != "canvas":
            assert self.style_config is not None

            # Map layer to depth (layer controls edge FROM that layer)
            # level_3_plus maps to depth 3 and affects all deeper levels (3, 4, 5, ...)
            depth_map = {"root": 0, "level_1": 1, "level_2": 2, "level_3_plus": 3}
            depth = depth_map.get(self.current_layer, 2)

            # Determine which depths to update (level_3_plus affects all depths >= 3)
            is_level_3_plus = self.current_layer == "level_3_plus"
            if is_level_3_plus:
                # Collect all depths >= 3 from existing config
                all_depths = set(self.style_config.connector_config_by_depth.keys())
                depths_to_update = [d for d in all_depths if d >= 3]
                if not depths_to_update:
                    depths_to_update = [3]
            else:
                depths_to_update = [depth]

            # Update connector config for all target depths
            for d in depths_to_update:
                connector_config = self.style_config.connector_config_by_depth.get(d, {})
                self.style_config.connector_config_by_depth[d] = connector_config

                # Update connector config
                if "connector_shape" in style:
                    connector_config["connector_shape"] = style["connector_shape"]
                if "connector_style" in style:
                    connector_config["connector_style"] = style["connector_style"]
                if "line_width" in style:
                    connector_config["line_width"] = style["line_width"]
                if "connector_color" in style:
                    connector_config["color"] = style["connector_color"]

                # Note: enable_gradient is automatically determined by connector_shape
                # No need to store it separately (bezier -> True, others -> False)

            self._apply_styles_to_mindmap()

    @staticmethod
    def _auto_contrast(bg_color: str) -> str:
        """Auto-select text color based on background brightness.

        Args:
            bg_color: Background color in hex format

        Returns:
            White (#FFFFFF) for dark backgrounds, black (#000000) for light
        """
        # Remove '#' if present
        bg_color = bg_color.lstrip("#")

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
        # Canvas layer is selected by default
        self.canvas_section.setVisible(True)
        self.canvas_section.setCollapsed(False)

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

        if self.current_layer == "canvas":
            # Load canvas style
            if "bg_color" in layer_data:
                self.canvas_section.set_color(layer_data["bg_color"])
            # Hide shadow section for canvas
            self.shadow_section.setVisible(False)
        else:
            # Load node style
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
            if hasattr(mindmap_view, "style_config") and self.current_layer != "canvas":
                assert self.style_config is not None

                # Map layers to depths
                depth_map = {
                    "root": 0,
                    "level_1": 1,
                    "level_2": 2,
                    "level_3_plus": 3,
                }
                depth = depth_map[self.current_layer]

                # Ensure dictionaries exist in mindmap_view.style_config
                if not hasattr(mindmap_view.style_config, 'level_spacing_by_depth'):
                    mindmap_view.style_config.level_spacing_by_depth = {}
                if not hasattr(mindmap_view.style_config, 'sibling_spacing_by_depth'):
                    mindmap_view.style_config.sibling_spacing_by_depth = {}

                # Copy spacing values from panel's style_config to mindmap_view's style_config
                if depth in self.style_config.level_spacing_by_depth:
                    mindmap_view.style_config.level_spacing_by_depth[depth] = self.style_config.level_spacing_by_depth[depth]

                if depth in self.style_config.sibling_spacing_by_depth:
                    mindmap_view.style_config.sibling_spacing_by_depth[depth] = self.style_config.sibling_spacing_by_depth[depth]

            # CRITICAL: If style affects dimensions, update all node items' template_style first
            if force_rebuild and hasattr(mindmap_view, 'node_items'):
                for node_item in mindmap_view.node_items.values():
                    if hasattr(node_item, 'update_style'):
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
                    name="Custom", description="", node_colors={}
                )

            # Set node color
            if "bg_color" in layer_data:
                style.resolved_color_scheme.node_colors[role] = layer_data["bg_color"]

            # Set text color
            if "text_color" in layer_data:
                if not style.resolved_color_scheme.text_colors:
                    style.resolved_color_scheme.text_colors = {}
                style.resolved_color_scheme.text_colors[role] = layer_data["text_color"]

            # Set border color (only if not None)
            if "border_color" in layer_data and layer_data["border_color"] is not None:
                if not style.resolved_color_scheme.border_colors:
                    style.resolved_color_scheme.border_colors = {}
                style.resolved_color_scheme.border_colors[role] = layer_data[
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
            if hasattr(mindmap_view, 'scene'):
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
            if not hasattr(source_node, 'depth'):
                continue

            depth = source_node.depth

            # Get connector config for this depth, fallback to max configured depth
            if depth in self.style_config.connector_config_by_depth:
                connector_config = self.style_config.connector_config_by_depth[depth]
            else:
                max_depth = max(self.style_config.connector_config_by_depth.keys())
                connector_config = self.style_config.connector_config_by_depth[max_depth]

            # Build connector style dict (only shape is needed for update_style)
            connector_style = {
                "connector_shape": connector_config["connector_shape"],
            }

            edge_item.update_style(connector_style)

            # Trigger repaint (paint() will read latest config directly)
            edge_item.update()

