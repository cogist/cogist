"""Border style section widget.

Provides controls for customizing node border appearance.
Implements lazy initialization for better performance.
"""

from qtpy.compat import isalive
from qtpy.QtCore import QPoint, Qt, Signal
from qtpy.QtWidgets import (
    QGridLayout,
    QLabel,
    QMenu,
    QPushButton,
)

from cogist.presentation.widgets import ColorPoolPopup, ToggleSwitch

from .collapsible_panel import CollapsiblePanel
from .color_dialog_undo import ColorDialogUndoMixin
from .color_picker import create_color_picker
from .dialog_utils import position_color_dialog
from .menu_button import MenuButton
from .spinbox import SpinBox


class BorderSection(ColorDialogUndoMixin, CollapsiblePanel):
    """Border style settings with lazy initialization.

    Signals:
        style_changed(dict): Emitted when border style changes
    """

    style_changed = Signal(dict)

    # UI constants (fallback value, will use parent's LABEL_WIDTH if available)
    LABEL_WIDTH = 90
    WIDGET_HEIGHT = 32
    GROUP_MARGIN = 10

    def __init__(self, parent=None):
        super().__init__("Border Style", collapsed=True, parent=parent)

        # Get LABEL_WIDTH from parent (StyleEditorTab) if available, otherwise use class default
        self._label_width = (
            getattr(parent, "LABEL_WIDTH", self.LABEL_WIDTH)
            if parent
            else self.LABEL_WIDTH
        )

        # Store reference to StyleEditorTab for accessing style_config
        # Note: parent() returns _content_widget, so we need to store the actual parent
        self._advanced_tab = parent

        # State
        self._initialized = False
        self.current_style: dict = {}  # Will be populated by set_style() from MindMapStyle
        self.is_root_mode = False  # True for root layer, False for level1/2/3+
        self.use_rainbow = False  # Rainbow branch mode state

        # Color picker (lazy creation)
        self._color_picker = None

        # Connect toggle signal for lazy initialization
        self.toggled.connect(self._on_toggled)

    def _on_toggled(self, checked: bool):
        """Handle expand/collapse events."""
        if checked and not self._initialized:
            self._init_content()
            self._initialized = True
            # Apply saved style to newly created controls
            if self.current_style:
                self.set_style(self.current_style)

    def set_root_mode(self, is_root: bool):
        """Set whether this section is in root mode.

        In root mode, border color uses a color picker for arbitrary colors.
        In normal mode, border color is selected from the color pool.
        """
        self.is_root_mode = is_root

    def _init_content(self):
        """Initialize content on first expand (lazy initialization)."""
        layout = QGridLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(self.GROUP_MARGIN, 6, self.GROUP_MARGIN, 16)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)

        row = 0

        # Border enabled - Toggle Switch (right-aligned)
        enabled_label = QLabel("Enabled:")
        enabled_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        enabled_label.setFixedWidth(self._label_width)
        layout.addWidget(enabled_label, row, 0)

        self.enabled_toggle = ToggleSwitch()
        # Use temporary default for UI initialization (will be updated by set_style)
        self.enabled_toggle.set_checked(True)
        self.enabled_toggle.toggled.connect(self._on_enabled_changed)
        layout.addWidget(
            self.enabled_toggle, row, 1, alignment=Qt.AlignRight | Qt.AlignVCenter
        )
        row += 1

        # Border style
        self.style_label = QLabel("Style:")
        self.style_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.style_label.setFixedWidth(self._label_width)
        layout.addWidget(self.style_label, row, 0)

        # Get initial border style from current_style
        border_style_map = {
            "solid": "Solid",
            "dashed": "Dashed",
            "dotted": "Dotted",
        }
        initial_border_style = border_style_map.get(
            self.current_style.get("border_style", "solid"), "Solid"
        )

        self.border_style_menu = QMenu()
        border_styles = ["Solid", "Dashed", "Dotted", "Dash-Dot"]
        for style in border_styles:
            action = self.border_style_menu.addAction(style)
            action.triggered.connect(lambda _, s=style: self._set_border_style(s))

        # Use reusable MenuButton instead of QPushButton
        self.border_style_combo = MenuButton(initial_border_style, self.WIDGET_HEIGHT)
        self.border_style_combo.setStyleSheet(self._button_style())
        self.border_style_combo.set_menu(self.border_style_menu)
        layout.addWidget(self.border_style_combo, row, 1)
        row += 1

        # Border width
        width_label = QLabel("Width:")
        width_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        width_label.setFixedWidth(self._label_width)
        layout.addWidget(width_label, row, 0)

        self.border_width_spin = SpinBox()
        self.border_width_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.border_width_spin.setRange(1, 10)
        # Use temporary default for UI initialization (will be updated by set_style)
        self.border_width_spin.setValue(2)
        self.border_width_spin.setAlignment(Qt.AlignLeft)
        self.border_width_spin.setFocusPolicy(Qt.StrongFocus)
        # Ensure keyboard tracking is enabled for continuous arrow key navigation
        self.border_width_spin.setKeyboardTracking(True)
        self.border_width_spin.valueChanged.connect(self._on_width_changed)
        layout.addWidget(self.border_width_spin, row, 1)
        row += 1

        # Border color - same as NodeStyleSection (simple QPushButton)
        self.color_label = QLabel("Color:")
        self.color_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.color_label.setFixedWidth(self._label_width)
        layout.addWidget(self.color_label, row, 0)

        self.color_btn = QPushButton()
        self.color_btn.setFixedHeight(self.WIDGET_HEIGHT)
        self.color_btn.clicked.connect(self._on_color_clicked)
        layout.addWidget(self.color_btn, row, 1)
        # Note: Button stylesheet is set by set_style() - no text, no hardcoded colors
        row += 1

        # Brightness spinbox
        brightness_label = QLabel("Brightness:")
        brightness_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        brightness_label.setFixedWidth(self._label_width)
        layout.addWidget(brightness_label, row, 0)

        self.brightness_spin = SpinBox()
        self.brightness_spin.setRange(50, 200)  # 50%-200% (0.5-2.0)
        self.brightness_spin.setSuffix("%")
        # Use temporary default for UI initialization (will be updated by set_style)
        self.brightness_spin.setValue(100)
        self.brightness_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.brightness_spin.valueChanged.connect(self._on_brightness_changed)
        layout.addWidget(self.brightness_spin, row, 1)
        row += 1

        # Opacity spinbox
        opacity_label = QLabel("Opacity:")
        opacity_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        opacity_label.setFixedWidth(self._label_width)
        layout.addWidget(opacity_label, row, 0)

        self.opacity_spin = SpinBox()
        self.opacity_spin.setRange(0, 100)
        self.opacity_spin.setSuffix("%")
        # Use temporary default for UI initialization (will be updated by set_style)
        self.opacity_spin.setValue(100)  # 100% = 255
        self.opacity_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.opacity_spin.valueChanged.connect(self._on_opacity_changed)
        layout.addWidget(self.opacity_spin, row, 1)

        # Note: _update_border_controls_visibility() will be called in set_style()
        # after current_style is populated with real data from template

        self.setLayout(layout)

    def _button_style(self) -> str:
        """Get standard button stylesheet."""
        return """
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #C8C8C8;
                border-radius: 6px;
                padding: 4px 24px 4px 12px;
                font-size: 13px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
                border-color: #A0A0A0;
            }
        """

    def _set_border_style(self, value: str):
        """Set border style."""
        self.border_style_combo.setText(value)
        style_map = {
            "Solid": "solid",
            "Dashed": "dashed",
            "Dotted": "dotted",
            "Dash-Dot": "dash_dot",
        }
        self.current_style["border_style"] = style_map.get(value, "solid")
        self._emit_style_changed()

    def _on_width_changed(self, value: int):
        """Handle border width change."""
        self.current_style["border_width"] = value
        self._emit_style_changed()

    def _on_enabled_changed(self, checked: bool):
        """Handle border enabled toggle change."""
        self.current_style["border_enabled"] = checked

        # Update visibility of all border controls
        self._update_border_controls_visibility()

        # Emit style changed event
        self._emit_style_changed()

    def _update_border_controls_visibility(self):
        """Show/hide border controls based on enabled state."""
        # Trust data integrity: border_enabled must exist in current_style
        assert self.current_style, "current_style should not be empty"
        enabled = self.current_style["border_enabled"]

        # Show/hide all controls except Enabled toggle and its label
        if hasattr(self, "style_label"):
            self.style_label.setVisible(enabled)
        if hasattr(self, "border_style_combo"):
            self.border_style_combo.setVisible(enabled)
        if hasattr(self, "border_width_spin"):
            # Find and hide/show width label
            layout = self._content_widget.layout()
            if layout:
                for i in range(layout.count()):
                    item = layout.itemAt(i)
                    widget = item.widget() if item else None
                    if (
                        widget
                        and isinstance(widget, QLabel)
                        and widget.text() == "Width:"
                    ):
                        widget.setVisible(enabled)
                        break
            self.border_width_spin.setVisible(enabled)
        if hasattr(self, "color_btn"):
            # Find and hide/show color label
            layout = self._content_widget.layout()
            if layout:
                for i in range(layout.count()):
                    item = layout.itemAt(i)
                    widget = item.widget() if item else None
                    if (
                        widget
                        and isinstance(widget, QLabel)
                        and widget.text() == "Color:"
                    ):
                        # In rainbow mode (non-root), always hide color controls
                        if not self.is_root_mode and self.use_rainbow:
                            widget.setVisible(False)
                        else:
                            widget.setVisible(enabled)
                        break
            # In rainbow mode (non-root), always hide color button
            if not self.is_root_mode and self.use_rainbow:
                self.color_btn.setVisible(False)
            else:
                self.color_btn.setVisible(enabled)
        if hasattr(self, "brightness_spin"):
            # Find and hide/show brightness label
            layout = self._content_widget.layout()
            if layout:
                for i in range(layout.count()):
                    item = layout.itemAt(i)
                    widget = item.widget() if item else None
                    if (
                        widget
                        and isinstance(widget, QLabel)
                        and widget.text() == "Brightness:"
                    ):
                        widget.setVisible(enabled)
                        break
            self.brightness_spin.setVisible(enabled)
        if hasattr(self, "opacity_spin"):
            # Find and hide/show opacity label
            layout = self._content_widget.layout()
            if layout:
                for i in range(layout.count()):
                    item = layout.itemAt(i)
                    widget = item.widget() if item else None
                    if (
                        widget
                        and isinstance(widget, QLabel)
                        and widget.text() == "Opacity:"
                    ):
                        widget.setVisible(enabled)
                        break
            self.opacity_spin.setVisible(enabled)

    def _on_color_clicked(self):
        """Handle border color button click."""
        # Use stored reference to StyleEditorTab instead of parent()
        parent = self._advanced_tab

        if not (parent and hasattr(parent, "style_config") and parent.style_config):
            return

        if self.is_root_mode:
            # Root mode: show color picker for special_colors["root_border"] (same as CanvasPanel)
            # Check if color picker still exists (may have been deleted by WA_DeleteOnClose)
            if self._color_picker is None or not isalive(self._color_picker):
                # Get the top-level window to ensure proper dialog lifecycle
                top_level = self.window() if self.window() else parent
                self._color_picker = create_color_picker(top_level)
                self._color_picker.color_selected.connect(
                    self._on_border_color_selected
                )
                # Ensure dialog closes when parent window closes
                self._color_picker.setAttribute(
                    Qt.WidgetAttribute.WA_DeleteOnClose, True
                )

            # Setup undo support using mixin
            self.setup_color_dialog_undo(
                color_picker=self._color_picker,
                layer="root",
                style_key="border_color",
                get_current_color=lambda: parent.style_config.special_colors["root_border"],
            )

            # Set current color (MUST call before show!)
            current_color = parent.style_config.special_colors["root_border"]
            self._color_picker.set_current_color(current_color)

            # Show color picker
            self._color_picker.show()
            self._color_picker.raise_()
            self._color_picker.activateWindow()

            # Position dialog
            position_color_dialog(self._color_picker, self.color_btn)
        else:
            # Normal mode (level 1/2/3+): show color pool selector dialog
            self._show_border_color_pool_selector()

    def _show_border_color_pool_selector(self):
        """Show color pool selector popup for level 1/2/3+ layers.

        Uses ColorPoolPopup component for consistent UX with smart positioning.
        """
        parent = self._advanced_tab
        if not (parent and hasattr(parent, "style_config") and parent.style_config):
            return

        color_pool = parent.style_config.color_pool
        if not color_pool or len(color_pool) < 8:
            print("Warning: color_pool not properly initialized")
            return

        # Create color pool popup (reusable component)
        if not hasattr(self, '_color_pool_popup') or self._color_pool_popup is None:
            self._color_pool_popup = ColorPoolPopup(
                color_pool=color_pool,
                parent=self,
            )
            self._color_pool_popup.color_selected.connect(
                self._on_border_color_pool_selected
            )

        # Show popup at button position with smart boundary detection
        button_pos = self.color_btn.mapToGlobal(QPoint(0, self.color_btn.height()))
        button_width = self.color_btn.width()
        self._color_pool_popup.show_at(button_pos, button_width)

    def _on_border_color_pool_selected(self, color_index: int):
        """Handle border color selection from pool selector popup.

        Args:
            color_index: The selected color index (0-7)
        """
        # Update border_color_index in current_style
        self.current_style["border_color_index"] = color_index

        # Update button display color
        parent = self._advanced_tab
        if parent and hasattr(parent, "style_config") and parent.style_config:
            color_pool = parent.style_config.color_pool
            if color_index < len(color_pool):
                selected_color = color_pool[color_index]
                # Don't set text - let button show only color
                if hasattr(self, "color_btn"):
                    self.color_btn.setStyleSheet(
                        f"background-color: {selected_color}; "
                        "border: 1px solid #C8C8C8; "
                        "border-radius: 6px; "
                        "padding: 4px 24px 4px 12px; "
                        "font-size: 13px; "
                        "text-align: left;"
                    )

        # Emit style changed
        self._emit_style_changed()

    def _get_final_color(self):
        """Get final root border color."""
        parent = self._advanced_tab
        if parent and hasattr(parent, 'style_config') and parent.style_config:
            return parent.style_config.special_colors["root_border"]
        return None

    def _on_border_color_selected(self, hex_color: str):
        """Handle border color selection from picker (root mode only - real-time preview)."""
        parent = self._advanced_tab

        if (
            parent
            and hasattr(parent, "style_config")
            and parent.style_config
            and self.is_root_mode
        ):
            # Real-time preview: update style_config for immediate UI feedback
            parent.style_config.special_colors["root_border"] = hex_color

            # CRITICAL: Update current_style to match CanvasPanel behavior
            self.current_style["border_color"] = hex_color

            # Update button color directly
            if hasattr(self, "color_btn"):
                self.color_btn.setStyleSheet(
                    f"background-color: {hex_color}; "
                    "border: 1px solid #C8C8C8; "
                    "border-radius: 6px; "
                    "padding: 4px 24px 4px 12px; "
                    "font-size: 13px; "
                    "text-align: left;"
                )

            # Emit style changed
            self._emit_style_changed()

    def _on_brightness_changed(self, value: int):
        """Handle border brightness change."""
        # Use border_brightness for role-based style (RoleStyle field name)
        self.current_style["border_brightness"] = value / 100.0
        self._emit_style_changed()

    def _on_opacity_changed(self, value: int):
        """Handle border opacity change."""
        # Convert from 0-100% to 0-255 for storage
        # Use border_opacity for role-based style (RoleStyle field name)
        self.current_style["border_opacity"] = int(value / 100 * 255)
        self._emit_style_changed()

    def _emit_style_changed(self):
        """Emit style changed signal with only border-related fields."""
        # Only emit border-related fields to avoid overwriting other style properties
        # Trust data integrity: all keys must exist in current_style
        border_only_style = {
            "border_enabled": self.current_style["border_enabled"],
            "border_style": self.current_style["border_style"],
            "border_width": self.current_style["border_width"],
            "border_color_index": self.current_style["border_color_index"],
            "border_brightness": self.current_style["border_brightness"],
            "border_opacity": self.current_style["border_opacity"],
        }
        self.style_changed.emit(border_only_style)

    def get_style(self) -> dict:
        """Get current border style."""
        return self.current_style.copy()

    def set_style(self, style: dict):
        """Set border style programmatically.

        Args:
            style: Dictionary containing border style properties from MindMapStyle
        """
        # Update rainbow mode state
        if "use_rainbow" in style:
            self.use_rainbow = style["use_rainbow"]

        # CRITICAL: Update current_style completely from MindMapStyle data
        # Do NOT use any default values - all data must come from style_config
        self.current_style.update(style)

        if self._initialized:
            # Update enabled toggle
            if "border_enabled" in style and hasattr(self, "enabled_toggle"):
                self.enabled_toggle.set_checked(style["border_enabled"])

            if "border_style" in style:
                style_map = {
                    "solid": "Solid",
                    "dashed": "Dashed",
                    "dotted": "Dotted",
                    "dash_dot": "Dash-Dot",
                }
                self.border_style_combo.setText(
                    style_map.get(style["border_style"], "Solid")
                )

            if "border_width" in style:
                self.border_width_spin.setValue(int(style["border_width"]))

            # Update brightness spinbox (support multiple field names)
            if "brightness" in style and hasattr(self, "brightness_spin"):
                self.brightness_spin.setValue(int(style["brightness"] * 100))
            elif "border_brightness" in style and hasattr(self, "brightness_spin"):
                self.brightness_spin.setValue(int(style["border_brightness"] * 100))

            # Update opacity spinbox (support multiple field names)
            if "opacity" in style and hasattr(self, "opacity_spin"):
                # Convert from 0-255 to 0-100% for display
                self.opacity_spin.setValue(int(style["opacity"] / 255 * 100))
            elif "border_opacity" in style and hasattr(self, "opacity_spin"):
                # Convert from 0-255 to 0-100% for display
                self.opacity_spin.setValue(int(style["border_opacity"] / 255 * 100))

            # Update color button display
            if "border_color" in style and hasattr(self, "color_btn"):
                # Use actual border_color value (for root node from special_colors)
                border_color = style["border_color"]
                self.color_btn.setStyleSheet(
                    f"background-color: {border_color}; "
                    "border: 1px solid #C8C8C8; "
                    "border-radius: 6px; "
                    "padding: 4px 24px 4px 12px; "
                    "font-size: 13px; "
                    "text-align: left;"
                )
            elif "border_color_index" in style and hasattr(self, "color_btn"):
                parent = self._advanced_tab
                if parent and hasattr(parent, "style_config") and parent.style_config:
                    color_pool = parent.style_config.color_pool
                    color_index = style["border_color_index"]
                    if color_index < len(color_pool):
                        selected_color = color_pool[color_index]
                        # Don't set text - let button show only color
                        self.color_btn.setStyleSheet(
                            f"background-color: {selected_color}; "
                            "border: 1px solid #C8C8C8; "
                            "border-radius: 6px; "
                            "padding: 4px 24px 4px 12px; "
                            "font-size: 13px; "
                            "text-align: left;"
                        )

            # Update controls visibility based on enabled state
            # Always update visibility when panel is initialized
            if self._initialized:
                self._update_border_controls_visibility()

            # Hide/show color controls based on rainbow mode (only for non-root layers)
            if not self.is_root_mode:
                if self.use_rainbow:
                    # Rainbow mode: hide color button
                    if hasattr(self, "color_label"):
                        self.color_label.setVisible(False)
                    if hasattr(self, "color_btn"):
                        self.color_btn.setVisible(False)
                else:
                    # Non-rainbow mode: show color controls
                    if hasattr(self, "color_label"):
                        self.color_label.setVisible(True)
                    if hasattr(self, "color_btn"):
                        self.color_btn.setVisible(True)
