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

    def __init__(self, style_config=None, parent=None):
        super().__init__(parent)

        # Set initial width (fixed, non-resizable)
        self.setMinimumWidth(self.PANEL_WIDTH)
        self.setMaximumWidth(self.PANEL_WIDTH)

        # Store reference to global style configuration
        self.style_config = style_config
        if not self.style_config:
            raise ValueError("style_config is required - panel must have access to global style data")

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
            # Colors
            "bg_color": color_scheme.node_colors.get(role, "#FFFFFF"),
            "text_color": (
                color_scheme.text_colors.get(role)
                if color_scheme.text_colors and role in color_scheme.text_colors
                else self._auto_contrast(color_scheme.node_colors.get(role, "#FFFFFF"))
            ),
            "border_color": (
                color_scheme.border_colors.get(role)
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
            # Connector
            "connector_type": "bezier",
            "connector_style": "solid",
            "connector_width": 2,
            "connector_color": color_scheme.edge_color,
            # Spacing - read from per-depth configuration
            "parent_child_spacing": self._get_level_spacing_for_layer(layer_name),
            "sibling_spacing": self._get_sibling_spacing_for_layer(layer_name),
        }

        return layer_data

    def _get_level_spacing_for_layer(self, layer_name: str) -> float:
        """Get parent-child spacing for a layer from per-depth configuration."""
        depth_map = {"root": 0, "level_1": 1, "level_2": 2, "level_3_plus": 3}
        depth = depth_map.get(layer_name, 2)

        if hasattr(self.style_config, 'level_spacing_by_depth'):
            return self.style_config.level_spacing_by_depth.get(depth, self.style_config.parent_child_spacing)
        return self.style_config.parent_child_spacing

    def _get_sibling_spacing_for_layer(self, layer_name: str) -> float:
        """Get sibling spacing for a layer from per-depth configuration."""
        if layer_name == "root":
            return 0

        depth_map = {"level_1": 0, "level_2": 1, "level_3_plus": 2}
        depth = depth_map.get(layer_name, 2)

        if hasattr(self.style_config, 'sibling_spacing_by_depth'):
            return self.style_config.sibling_spacing_by_depth.get(depth, self.style_config.sibling_spacing)
        return self.style_config.sibling_spacing

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
        layout.setSpacing(1)

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
        # Save current layer style before switching
        self._save_current_layer_style()

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
        self.layer_styles["canvas"]["bg_color"] = color
        self._apply_styles_to_mindmap()

    def _on_spacing_changed(self, spacing: dict):
        """Handle spacing configuration change for the current layer."""
        if self.current_layer != "canvas":
            # Update only the fields that changed in layer_styles
            self.layer_styles[self.current_layer].update(spacing)

            # Directly update mindmap_view.style_config to ensure layout refresh picks it up
            try:
                from cogist.application.services.app_context import get_app_context
                app_context = get_app_context()
                if app_context:
                    mindmap_view = app_context.get_mindmap_view()
                    if mindmap_view and hasattr(mindmap_view, "style_config"):
                        # Map layers to depths for spacing application
                        depth_map = {
                            "root": 0,
                            "level_1": 1,
                            "level_2": 2,
                            "level_3_plus": 3,
                        }
                        depth = depth_map[self.current_layer]

                        if "parent_child" in spacing:
                            # Initialize dictionary if not exists
                            if not hasattr(mindmap_view.style_config, 'level_spacing_by_depth'):
                                mindmap_view.style_config.level_spacing_by_depth = {}
                            # Update ONLY the specific depth's level spacing (true isolation)
                            mindmap_view.style_config.level_spacing_by_depth[depth] = spacing["parent_child"]

                        if "sibling" in spacing:
                            # Initialize dictionary if not exists
                            if not hasattr(mindmap_view.style_config, 'sibling_spacing_by_depth'):
                                mindmap_view.style_config.sibling_spacing_by_depth = {}
                            # Update ONLY the specific depth's sibling spacing (true isolation)
                            # Root layer has no siblings, but we still store it for completeness
                            mindmap_view.style_config.sibling_spacing_by_depth[depth] = spacing["sibling"]

                        # Trigger layout refresh
                        if hasattr(mindmap_view, "_refresh_layout"):
                            mindmap_view._refresh_layout(skip_measurement=True)
            except Exception as e:
                print(f"Error applying spacing: {e}")

    def _on_node_style_changed(self, style: dict):
        """Handle node style changes."""
        if self.current_layer != "canvas":
            # Update layer_styles directly with the received style
            self.layer_styles[self.current_layer].update(style)
            self._apply_styles_to_mindmap()

    def _on_shadow_enabled_changed(self, enabled: bool):
        """Handle font shadow enabled state change."""
        self.shadow_section.setVisible(enabled)
        if enabled:
            self.shadow_section.setCollapsed(False)

        # Update layer_styles and apply
        if self.current_layer != "canvas":
            self.layer_styles[self.current_layer]["shadow_enabled"] = enabled
            self._apply_styles_to_mindmap()

    def _on_shadow_changed(self, shadow: dict):
        """Handle shadow style changes."""
        if self.current_layer != "canvas":
            print(f"DEBUG _on_shadow_changed: received shadow = {shadow}")
            print(
                f"DEBUG _on_shadow_changed: before update - layer_styles[{self.current_layer}]['shadow_enabled'] = {self.layer_styles[self.current_layer]['shadow_enabled']}"
            )

            # Update only the fields that changed, preserve existing values for others
            # This ensures we don't accidentally reset shadow_enabled to False
            layer_data = self.layer_styles[self.current_layer]

            # Update shadow parameters from the received dict
            if "offset_x" in shadow:
                layer_data["shadow_offset_x"] = shadow["offset_x"]
            if "offset_y" in shadow:
                layer_data["shadow_offset_y"] = shadow["offset_y"]
            if "blur" in shadow:
                layer_data["shadow_blur"] = shadow["blur"]
            if "color" in shadow:
                layer_data["shadow_color"] = shadow["color"]
            if "enabled" in shadow:
                layer_data["shadow_enabled"] = shadow["enabled"]

            print(
                f"DEBUG _on_shadow_changed: after update - layer_styles[{self.current_layer}]['shadow_enabled'] = {layer_data['shadow_enabled']}"
            )
            print(
                f"DEBUG _on_shadow_changed: after update - layer_styles[{self.current_layer}]['shadow_offset_x'] = {layer_data['shadow_offset_x']}"
            )

            self._apply_styles_to_mindmap()

    def _on_border_style_changed(self, style: dict):
        """Handle border style changes."""
        if self.current_layer != "canvas":
            # Update layer_styles directly with the received style
            self.layer_styles[self.current_layer].update(style)
            self._apply_styles_to_mindmap()

    def _on_connector_style_changed(self, style: dict):
        """Handle connector style changes for the current layer."""
        if self.current_layer != "canvas":
            self.layer_styles[self.current_layer].update(style)
            self._apply_styles_to_mindmap()

    def _initialize_layer_styles_from_config(self, style_config):
        """Initialize layer_styles from style_config's resolved_template and resolved_color_scheme.

        This ensures ALL fields are populated with actual values from the loaded file,
        not just defaults. This is CRITICAL for data integrity.

        Args:
            style_config: MindMapStyle instance with resolved_template and resolved_color_scheme
        """
        if not style_config.resolved_template or not style_config.resolved_color_scheme:
            # No resolved data, keep defaults
            return

        template = style_config.resolved_template
        color_scheme = style_config.resolved_color_scheme

        # Map NodeRole to layer names
        role_to_layer = {
            "root": "root",
            "primary": "level_1",
            "secondary": "level_2",
            "tertiary": "level_3_plus",
        }

        # Initialize each layer from template role_styles
        for role_str, layer_name in role_to_layer.items():
            from cogist.domain.styles import NodeRole

            role = NodeRole(role_str)

            if role not in template.role_styles:
                continue

            role_style = template.role_styles[role]

            # Build complete layer_data dict with ALL fields
            layer_data = {
                # Shape
                "shape": role_style.shape.basic_shape,
                "radius": role_style.shape.border_radius,
                # Colors (from color_scheme) - ensure ALL colors are populated
                "bg_color": color_scheme.node_colors[
                    role
                ],  # node_colors always has all roles
                "text_color": (
                    color_scheme.text_colors[role]
                    if color_scheme.text_colors and role in color_scheme.text_colors
                    else self._auto_contrast(color_scheme.node_colors[role])
                ),
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
                # Shadow (complete configuration)
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
                # Connector (per-layer)
                "connector_type": "bezier",
                "connector_style": "solid",
                "connector_width": 2,
                "connector_color": color_scheme.edge_color,
                # Spacing (per-layer) - Initialize from style_config
                "parent_child_spacing": style_config.parent_child_spacing,
                "sibling_spacing": 0 if layer_name == "root" else style_config.sibling_spacing,
            }

            # Update layer_styles - this replaces the default completely
            self.layer_styles[layer_name] = layer_data

        # Update canvas background
        self.layer_styles["canvas"]["bg_color"] = color_scheme.canvas_bg_color

        print(
            f"✓ Initialized layer_styles from style_config ({len(template.role_styles)} roles)"
        )

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
                "connector_type": layer_data["connector_type"],
                "connector_style": layer_data["connector_style"],
                "line_width": layer_data["connector_width"],
                "connector_color": layer_data["connector_color"],
            }
            self.connector_section.set_style(connector_style)

    def _save_current_layer_style(self):
        """Save current UI state to layer_styles dict."""
        if self.current_layer == "canvas":
            # Save canvas style
            self.layer_styles["canvas"]["bg_color"] = self.canvas_section.get_color()
        else:
            # Save node style
            node_style = self.node_style_section.get_style()
            self.layer_styles[self.current_layer].update(node_style)

            # Save border style
            border_style = self.border_section.get_style()
            self.layer_styles[self.current_layer].update(border_style)

            # Save shadow configuration
            shadow_config = self.shadow_section.get_shadow()
            if shadow_config:
                # Direct access - shadow_config always has complete fields
                self.layer_styles[self.current_layer]["shadow_enabled"] = shadow_config[
                    "enabled"
                ]
                self.layer_styles[self.current_layer]["shadow_offset_x"] = (
                    shadow_config["offset_x"]
                )
                self.layer_styles[self.current_layer]["shadow_offset_y"] = (
                    shadow_config["offset_y"]
                )
                self.layer_styles[self.current_layer]["shadow_blur"] = shadow_config[
                    "blur"
                ]
                self.layer_styles[self.current_layer]["shadow_color"] = shadow_config[
                    "color"
                ]

            # Save spacing configuration (per-layer)
            self.layer_styles[self.current_layer]["parent_child_spacing"] = self.spacing_section.parent_child_spin.value()
            if self.current_layer != "root":
                self.layer_styles[self.current_layer]["sibling_spacing"] = self.spacing_section.sibling_spin.value()
            else:
                self.layer_styles[self.current_layer]["sibling_spacing"] = 0

            # Save connector style (per-layer)
            if hasattr(self.connector_section, 'connector_type_combo'):
                type_map_inv = {"Straight": "straight", "Orthogonal": "orthogonal", "Bezier": "bezier"}
                self.layer_styles[self.current_layer]["connector_type"] = type_map_inv[
                    self.connector_section.connector_type_combo.text()
                ]
            if hasattr(self.connector_section, 'connector_style_combo'):
                style_map_inv = {"Solid": "solid", "Dashed": "dashed", "Dotted": "dotted"}
                self.layer_styles[self.current_layer]["connector_style"] = style_map_inv[
                    self.connector_section.connector_style_combo.text()
                ]
            if hasattr(self.connector_section, 'connector_width_spin'):
                self.layer_styles[self.current_layer]["connector_width"] = self.connector_section.connector_width_spin.value()
            if hasattr(self.connector_section, 'current_style'):
                self.layer_styles[self.current_layer]["connector_color"] = self.connector_section.current_style["connector_color"]

    def _apply_styles_to_mindmap(self):
        """Unified method to apply all styles to mindmap_view.

        This method:
        1. Gets mindmap_view from app_context
        2. Applies all styles (node, connector, spacing) to style_config
        3. Refreshes the layout
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
            if hasattr(mindmap_view, "style_config") and self.current_layer != "canvas":
                layer_style = self.layer_styles[self.current_layer]

                # Map layers to depths
                depth_map = {
                    "root": 0,
                    "level_1": 1,
                    "level_2": 2,
                    "level_3_plus": 3,
                }
                depth = depth_map[self.current_layer]

                # Initialize dictionaries if not exist
                if not hasattr(mindmap_view.style_config, 'level_spacing_by_depth'):
                    mindmap_view.style_config.level_spacing_by_depth = {}
                if not hasattr(mindmap_view.style_config, 'sibling_spacing_by_depth'):
                    mindmap_view.style_config.sibling_spacing_by_depth = {}

                # Update ONLY the specific depth's spacing (true per-layer isolation)
                mindmap_view.style_config.level_spacing_by_depth[depth] = layer_style["parent_child_spacing"]
                mindmap_view.style_config.sibling_spacing_by_depth[depth] = layer_style["sibling_spacing"]

            # Refresh layout to apply all changes
            # CRITICAL: Skip measurement when applying style changes
            # because nodes will recalculate their own sizes based on new styles
            if hasattr(mindmap_view, "_refresh_layout"):
                mindmap_view._refresh_layout(skip_measurement=True)

        except Exception as e:
            print(f"Error applying styles: {e}")

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

        role_styles = style.resolved_template.role_styles or {}

        # Convert each layer to RoleBasedStyle + update ColorScheme
        for layer_name, role in layer_to_role.items():
            layer_data = self.layer_styles[layer_name]

            # Build RoleBasedStyle
            role_style = self._convert_layer_to_role_style(layer_data)
            role_styles[role] = role_style

            # Update template
            style.resolved_template.role_styles = role_styles

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
        if "canvas" in self.layer_styles:
            canvas_color = self.layer_styles["canvas"]["bg_color"]
            style.canvas_bg_color = canvas_color
            if style.resolved_color_scheme:
                style.resolved_color_scheme.canvas_bg_color = canvas_color

        # Update connector (edge) styles (per-layer)
        if style.resolved_color_scheme and self.current_layer != "canvas":
            layer_style = self.layer_styles[self.current_layer]
            style.resolved_color_scheme.edge_color = layer_style["connector_color"]

        # Update all existing node items with new style
        if hasattr(mindmap_view, "node_items"):
            for _node_id, node_item in mindmap_view.node_items.items():
                if hasattr(node_item, "update_style"):
                    node_item.update_style(style)

        # Note: Layout refresh is handled by _apply_styles_to_mindmap()

    def _apply_connector_styles_to_mindmap(self, mindmap_view):
        """Apply connector (edge) styles to all edges in the mind map (per-layer)."""
        if not hasattr(mindmap_view, "edge_items") or self.current_layer == "canvas":
            return

        # Get connector style from current layer
        layer_style = self.layer_styles[self.current_layer]
        connector_style = {
            "connector_type": layer_style["connector_type"],
            "connector_style": layer_style["connector_style"],
            "line_width": layer_style["connector_width"],
            "connector_color": layer_style["connector_color"],
        }

        for edge_item in mindmap_view.edge_items:
            if hasattr(edge_item, "update_style"):
                edge_item.update_style(connector_style)

    def _convert_layer_to_role_style(self, layer_data: dict):
        """Convert layer style dictionary to RoleBasedStyle object.

        Raises:
            AssertionError: If required fields are missing from layer_data
        """
        from cogist.domain.styles import (
            BackgroundStyle,
            BorderStyle,
            NodeRole,
            NodeShape,
            RoleBasedStyle,
        )

        role = NodeRole.TERTIARY  # Default

        # Assert that ALL critical fields exist - fail fast if data is incomplete
        # Shape fields
        assert "shape" in layer_data and layer_data["shape"] is not None, (
            f"layer_data missing 'shape' field: {layer_data}"
        )
        assert "radius" in layer_data, (
            f"layer_data missing 'radius' field: {layer_data}"
        )

        # Border fields
        assert "border_style" in layer_data, (
            f"layer_data missing 'border_style' field: {layer_data}"
        )
        assert "border_width" in layer_data, (
            f"layer_data missing 'border_width' field: {layer_data}"
        )

        # Font fields
        assert "font_family" in layer_data, (
            f"layer_data missing 'font_family' field: {layer_data}"
        )
        assert "font_size" in layer_data, (
            f"layer_data missing 'font_size' field: {layer_data}"
        )
        assert "font_weight" in layer_data, (
            f"layer_data missing 'font_weight' field: {layer_data}"
        )
        assert "font_italic" in layer_data, (
            f"layer_data missing 'font_italic' field: {layer_data}"
        )
        assert "font_underline" in layer_data, (
            f"layer_data missing 'font_underline' field: {layer_data}"
        )
        assert "font_strikeout" in layer_data, (
            f"layer_data missing 'font_strikeout' field: {layer_data}"
        )

        # Padding fields
        assert "padding_w" in layer_data, (
            f"layer_data missing 'padding_w' field: {layer_data}"
        )
        assert "padding_h" in layer_data, (
            f"layer_data missing 'padding_h' field: {layer_data}"
        )

        # Shadow fields (complete configuration)
        assert "shadow_enabled" in layer_data, (
            f"layer_data missing 'shadow_enabled' field: {layer_data}"
        )
        assert "shadow_offset_x" in layer_data, (
            f"layer_data missing 'shadow_offset_x' field: {layer_data}"
        )
        assert "shadow_offset_y" in layer_data, (
            f"layer_data missing 'shadow_offset_y' field: {layer_data}"
        )
        assert "shadow_blur" in layer_data, (
            f"layer_data missing 'shadow_blur' field: {layer_data}"
        )
        assert "shadow_color" in layer_data, (
            f"layer_data missing 'shadow_color' field: {layer_data}"
        )

        style = RoleBasedStyle(
            role=role,
            shape=NodeShape(
                basic_shape=layer_data["shape"],
                border_radius=layer_data["radius"],
            ),
            background=BackgroundStyle(
                bg_type="solid",
            ),
            border=BorderStyle(
                border_type="simple",
                border_style=layer_data["border_style"].lower(),
                border_width=layer_data["border_width"],
                border_radius=layer_data["radius"],
            ),
            padding_w=layer_data["padding_w"],
            padding_h=layer_data["padding_h"],
            font_size=layer_data["font_size"],
            font_weight=layer_data["font_weight"],
            font_style="Italic" if layer_data["font_italic"] else "Normal",
            font_family=layer_data["font_family"],
            font_underline=layer_data["font_underline"],
            font_strikeout=layer_data["font_strikeout"],
            shadow_enabled=layer_data["shadow_enabled"],
            shadow_offset_x=layer_data["shadow_offset_x"],
            shadow_offset_y=layer_data["shadow_offset_y"],
            shadow_blur=layer_data["shadow_blur"],
            shadow_color=layer_data["shadow_color"],
        )

        return style
