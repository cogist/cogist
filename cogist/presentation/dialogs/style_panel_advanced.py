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

        # Store style parameters by layer
        self.current_layer = "canvas"
        self.layer_styles = {
            "canvas": self._get_default_canvas_style(),
            "root": self._get_default_layer_style("root"),
            "level_1": self._get_default_layer_style("level_1"),
            "level_2": self._get_default_layer_style("level_2"),
            "level_3_plus": self._get_default_layer_style("level_3_plus"),
            "critical": self._get_default_layer_style("critical"),
            "minor": self._get_default_layer_style("minor"),
        }

        # Connector style (shared across all node layers)
        self.connector_style = self._get_default_connector_style()

        # Spacing configuration - derived from style_config if available
        if style_config:
            self.spacing_config = {
                "parent_child": getattr(style_config, 'parent_child_spacing', 20),
                "sibling": getattr(style_config, 'sibling_spacing', 15),
            }
        else:
            self.spacing_config = {
                "parent_child": 20,
                "sibling": 15,
            }

        # Initialize UI with modular components
        self._init_ui()

        # Connect signals
        self._connect_signals()

        # Set initial visibility based on default layer (canvas)
        self._set_initial_visibility()

        # Load initial layer style
        self._load_current_layer_style()

    def _init_ui(self):
        """Initialize UI with modular components."""
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        # Create content widget
        content_widget = QWidget()
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
        self.node_style_section.shadow_enabled_changed.connect(self._on_shadow_enabled_changed)

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
        is_canvas = (layer_name == "canvas")
        is_priority = (layer_name in ["critical", "minor"])

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
        """Handle spacing configuration change."""
        # Update internal spacing config
        self.spacing_config.update(spacing)

        # Apply all styles to mindmap (including spacing)
        self._apply_styles_to_mindmap()

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

    def _on_shadow_changed(self, shadow: dict):
        """Handle shadow style changes."""
        if self.current_layer != "canvas":
            # Update layer_styles directly with the received shadow
            self.layer_styles[self.current_layer].update(shadow)
            self._apply_styles_to_mindmap()

    def _on_border_style_changed(self, style: dict):
        """Handle border style changes."""
        if self.current_layer != "canvas":
            # Update layer_styles directly with the received style
            self.layer_styles[self.current_layer].update(style)
            self._apply_styles_to_mindmap()

    def _on_connector_style_changed(self, style: dict):
        """Handle connector style changes."""
        # Save connector style
        self.connector_style.update(style)
        # Apply all styles to mindmap
        self._apply_styles_to_mindmap()

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
        if self.current_layer == "canvas":
            # Load canvas style
            canvas_style = self.layer_styles.get("canvas", {})
            if "bg_color" in canvas_style:
                self.canvas_section.set_color(canvas_style["bg_color"])
            # Hide shadow section for canvas
            self.shadow_section.setVisible(False)
        else:
            # Load node style
            layer_style = self.layer_styles.get(self.current_layer, {})
            if layer_style:
                self.node_style_section.set_style(layer_style)
                # Sync shadow section visibility with shadow_enabled state
                shadow_enabled = layer_style.get("shadow_enabled", False)
                self.shadow_section.setVisible(shadow_enabled)

                # Load shadow configuration if available
                shadow_config = {
                    "enabled": shadow_enabled,
                    "offset_x": layer_style.get("shadow_offset_x", 2),
                    "offset_y": layer_style.get("shadow_offset_y", 2),
                    "blur": layer_style.get("shadow_blur", 4),
                    "color": layer_style.get("shadow_color", "#000000"),
                }
                self.shadow_section.set_shadow(shadow_config)

            # Load border style
            self.border_section.set_style(layer_style)

            # Load spacing configuration (shared across all non-canvas layers)
            self.spacing_section.set_spacing(self.spacing_config)

        # Load connector style (always loaded)
        self.connector_section.set_style(self.connector_style)

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
                self.layer_styles[self.current_layer].update({
                    "shadow_enabled": shadow_config.get("enabled", False),
                    "shadow_offset_x": shadow_config.get("offset_x", 2),
                    "shadow_offset_y": shadow_config.get("offset_y", 2),
                    "shadow_blur": shadow_config.get("blur", 4),
                    "shadow_color": shadow_config.get("color", "#000000"),
                })

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

            # Apply connector styles
            self._apply_connector_styles_to_mindmap(mindmap_view)

            # Apply spacing configuration
            if hasattr(mindmap_view, 'style_config'):
                mindmap_view.style_config.parent_child_spacing = self.spacing_config.get('parent_child', 80.0)
                mindmap_view.style_config.sibling_spacing = self.spacing_config.get('sibling', 60.0)

            # Refresh layout to apply all changes
            if hasattr(mindmap_view, '_refresh_layout'):
                mindmap_view._refresh_layout(skip_measurement=False)

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
            style.resolved_template = Template(name="Custom", description="", role_styles={})

        role_styles = style.resolved_template.role_styles or {}

        # Convert each layer to RoleBasedStyle + update ColorScheme
        for layer_name, role in layer_to_role.items():
            layer_data = self.layer_styles.get(layer_name, {})
            if not layer_data:
                continue

            # Build RoleBasedStyle
            role_style = self._convert_layer_to_role_style(layer_data)
            role_styles[role] = role_style

            # Update template
            style.resolved_template.role_styles = role_styles

            # Update color scheme
            if not style.resolved_color_scheme:
                style.resolved_color_scheme = ColorScheme(name="Custom", description="", node_colors={})

            # Set node color
            if "bg_color" in layer_data:
                style.resolved_color_scheme.node_colors[role] = layer_data["bg_color"]

            # Set text color
            if "text_color" in layer_data:
                if not style.resolved_color_scheme.text_colors:
                    style.resolved_color_scheme.text_colors = {}
                style.resolved_color_scheme.text_colors[role] = layer_data["text_color"]

            # Set border color
            if "border_color" in layer_data:
                if not style.resolved_color_scheme.border_colors:
                    style.resolved_color_scheme.border_colors = {}
                style.resolved_color_scheme.border_colors[role] = layer_data["border_color"]

        # Update canvas background color
        if "canvas" in self.layer_styles:
            canvas_color = self.layer_styles["canvas"].get("bg_color", "#FFFFFF")
            style.canvas_bg_color = canvas_color
            if style.resolved_color_scheme:
                style.resolved_color_scheme.canvas_bg_color = canvas_color

        # Update connector (edge) styles
        if style.resolved_color_scheme:
            style.resolved_color_scheme.edge_color = self.connector_style.get("connector_color", "#666666")

        # Update all existing node items with new style
        if hasattr(mindmap_view, 'node_items'):
            for _node_id, node_item in mindmap_view.node_items.items():
                if hasattr(node_item, 'update_style'):
                    node_item.update_style(style)

        # Note: Layout refresh is handled by _apply_styles_to_mindmap()

    def _apply_connector_styles_to_mindmap(self, mindmap_view):
        """Apply connector (edge) styles to all edges in the mind map."""
        if not hasattr(mindmap_view, 'edge_items'):
            return

        for edge_item in mindmap_view.edge_items:
            if hasattr(edge_item, 'update_style'):
                edge_item.update_style(self.connector_style)

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

        # Assert that critical fields exist - fail fast if data is incomplete
        assert "shape" in layer_data and layer_data["shape"] is not None, \
            f"layer_data missing 'shape' field: {layer_data}"
        assert "radius" in layer_data, \
            f"layer_data missing 'radius' field: {layer_data}"
        assert "border_style" in layer_data, \
            f"layer_data missing 'border_style' field: {layer_data}"
        assert "border_width" in layer_data, \
            f"layer_data missing 'border_width' field: {layer_data}"

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
            padding_w=layer_data.get("padding_w", 12),
            padding_h=layer_data.get("padding_h", 8),
            font_size=layer_data.get("font_size", 14),
            font_weight=layer_data.get("font_weight", "Normal"),
            font_style="Italic" if layer_data.get("font_italic", False) else "Normal",
            font_family=layer_data.get("font_family", "Arial"),
            font_underline=layer_data.get("font_underline", False),
            font_strikeout=layer_data.get("font_strikeout", False),
        )

        return style

    # === Default Style Methods ===

    def _get_default_canvas_style(self):
        """Get default canvas style."""
        return {
            "bg_color": "#FFFFFF",
        }

    def _get_default_layer_style(self, layer_type):
        """Get default style for a layer."""
        style = {
            "shape": "rounded_rect",
            "bg_color": "#2196F3",
            "text_color": "#FFFFFF",
            "font_family": "Arial",
            "font_size": 22,
            "font_weight": "Bold",
            "font_italic": False,
            "font_underline": False,
            "font_strikeout": False,
            "shadow_enabled": False,
            "border_style": "solid",
            "border_width": 2,
            "border_color": "#1976D2",
            "padding_w": 20,
            "padding_h": 16,
            "radius": 10,
        }

        # Adjust based on layer type
        if layer_type == "root":
            style.update({
                "bg_color": "#2196F3",
                "text_color": "#FFFFFF",
                "font_size": 22,
                "font_weight": "Bold",
            })
        elif layer_type == "level_1":
            style.update({
                "bg_color": "#4CAF50",
                "text_color": "#FFFFFF",
                "font_size": 18,
                "font_weight": "Normal",
            })
        elif layer_type == "level_2":
            style.update({
                "bg_color": "#FF9800",
                "text_color": "#FFFFFF",
                "font_size": 16,
                "font_weight": "Normal",
            })
        elif layer_type == "level_3_plus":
            style.update({
                "bg_color": "#9E9E9E",
                "text_color": "#FFFFFF",
                "font_size": 14,
                "font_weight": "Normal",
            })
        elif layer_type == "critical":
            style.update({
                "bg_color": "#D32F2F",
                "text_color": "#FFFFFF",
                "font_size": 24,
                "font_weight": "ExtraBold",
                "border_width": 4,
                "border_color": "#B71C1C",
            })
        elif layer_type == "minor":
            style.update({
                "bg_color": "#BDBDBD",
                "text_color": "#FFFFFF",
                "font_size": 18,
                "font_weight": "Light",
                "border_width": 1,
            })

        return style

    def _get_default_connector_style(self):
        """Get default connector (edge) style."""
        return {
            "connector_type": "bezier",
            "connector_style": "solid",
            "line_width": 2,
            "connector_color": "#666666",
        }
