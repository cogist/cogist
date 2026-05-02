"""Connector (edge) style section widget.

Provides controls for customizing edge appearance between nodes.
Implements lazy initialization for better performance.
"""

from PySide6.QtCore import QPoint, QSize, Qt, Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QMenu,
    QPushButton,
)

from cogist.presentation.widgets import (
    ColorPoolPopup,
    VisualPreviewButton,
    generate_bezier_preview,
    generate_bezier_uniform_preview,
    generate_orthogonal_preview,
    generate_rounded_orthogonal_preview,
    generate_sharp_first_rounded_preview,
    generate_straight_preview,
)

from .collapsible_panel import CollapsiblePanel
from .menu_button import MenuButton
from .spinbox import SpinBox


class ConnectorSection(CollapsiblePanel):
    """Connector style settings with lazy initialization.

    Signals:
        style_changed(dict): Emitted when connector style changes
    """

    style_changed = Signal(dict)

    # UI constants (fallback value, will use parent's LABEL_WIDTH if available)
    LABEL_WIDTH = 90
    WIDGET_HEIGHT = 32
    GROUP_MARGIN = 10

    def __init__(self, parent=None):
        super().__init__("Connector Style", collapsed=True, parent=parent)

        # Get LABEL_WIDTH from parent (AdvancedStyleTab) if available, otherwise use class default
        self._label_width = getattr(parent, 'LABEL_WIDTH', self.LABEL_WIDTH) if parent else self.LABEL_WIDTH

        # Store reference to AdvancedStyleTab for accessing style_config
        self._advanced_tab = parent

        # State
        self._initialized = False
        self.current_style = {
            "connector_shape": "bezier",
            "connector_style": "solid",
            "line_width": 2,
            "connector_color_index": 0,
            "connector_brightness": 1.0,
            "connector_opacity": 255,
        }

        # Connect toggle signal for lazy initialization
        self.toggled.connect(self._on_toggled)

    def _on_toggled(self, checked: bool):
        """Handle expand/collapse events."""
        if checked and not self._initialized:
            self._init_content()
            self._initialized = True

    def _init_content(self):
        """Initialize content on first expand (lazy initialization)."""
        layout = QGridLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(self.GROUP_MARGIN, 6, self.GROUP_MARGIN, 16)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)

        # Connector shape selector - using reusable VisualPreviewButton
        shape_label = QLabel("Shape:")
        shape_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        shape_label.setFixedWidth(self._label_width)
        layout.addWidget(shape_label, 0, 0)

        # Create visual options for popup
        connector_shape_options = [
            ("bezier", generate_bezier_preview, QSize(140, 30)),
            ("bezier_uniform", generate_bezier_uniform_preview, QSize(140, 30)),
            ("straight", generate_straight_preview, QSize(140, 30)),
            ("orthogonal", generate_orthogonal_preview, QSize(140, 30)),
            ("rounded_orthogonal", generate_rounded_orthogonal_preview, QSize(140, 30)),
            (
                "sharp_first_rounded",
                generate_sharp_first_rounded_preview,
                QSize(140, 30),
            ),
        ]

        # Create reusable visual preview button
        self.connector_shape_btn = VisualPreviewButton(
            options=connector_shape_options,
            initial_value=self.current_style.get("connector_shape", "bezier"),
            preview_size=QSize(140, 30),
            button_height=self.WIDGET_HEIGHT,
        )
        self.connector_shape_btn.value_changed.connect(self._on_connector_shape_changed)
        layout.addWidget(self.connector_shape_btn, 0, 1)

        # Connector style
        style_label = QLabel("Style:")
        style_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        style_label.setFixedWidth(self._label_width)
        layout.addWidget(style_label, 1, 0)

        # Get initial connector style from current_style
        connector_style_map = {
            "solid": "Solid",
            "dashed": "Dashed",
            "dotted": "Dotted",
        }
        initial_connector_style = connector_style_map.get(
            self.current_style.get("connector_style", "solid"), "Solid"
        )

        self.connector_style_menu = QMenu()
        connector_styles = ["Solid", "Dashed", "Dotted", "Dash-Dot"]
        for cstyle in connector_styles:
            action = self.connector_style_menu.addAction(cstyle)
            action.triggered.connect(lambda _, s=cstyle: self._set_connector_style(s))

        # Use reusable MenuButton instead of QPushButton
        self.connector_style_combo = MenuButton(
            initial_connector_style, self.WIDGET_HEIGHT
        )
        self.connector_style_combo.setStyleSheet(self._button_style())
        self.connector_style_combo.set_menu(self.connector_style_menu)
        layout.addWidget(self.connector_style_combo, 1, 1)

        # Connector width
        width_label = QLabel("Width:")
        width_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        width_label.setFixedWidth(self._label_width)
        layout.addWidget(width_label, 2, 0)

        self.connector_width_spin = SpinBox()
        self.connector_width_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.connector_width_spin.setRange(1, 10)
        self.connector_width_spin.setValue(self.current_style["line_width"])
        self.connector_width_spin.setAlignment(Qt.AlignLeft)
        self.connector_width_spin.valueChanged.connect(self._on_width_changed)
        layout.addWidget(self.connector_width_spin, 2, 1)

        # Connector color - simple QPushButton (no text, shows color only)
        color_label = QLabel("Color:")
        color_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        color_label.setFixedWidth(self._label_width)
        layout.addWidget(color_label, 3, 0)

        self.connector_color_btn = QPushButton()
        self.connector_color_btn.setFixedHeight(self.WIDGET_HEIGHT)
        self.connector_color_btn.clicked.connect(self._on_color_clicked)
        layout.addWidget(self.connector_color_btn, 3, 1)
        # Button stylesheet is set by set_style() - no text, no hardcoded colors

        # Connector brightness
        brightness_label = QLabel("Brightness:")
        brightness_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        brightness_label.setFixedWidth(self._label_width)
        layout.addWidget(brightness_label, 4, 0)

        self.connector_brightness_spin = SpinBox()
        self.connector_brightness_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.connector_brightness_spin.setRange(50, 150)  # 0.5-1.5
        self.connector_brightness_spin.setValue(int(self.current_style["connector_brightness"] * 100))
        self.connector_brightness_spin.valueChanged.connect(self._on_brightness_changed)
        layout.addWidget(self.connector_brightness_spin, 4, 1)

        # Connector opacity
        opacity_label = QLabel("Opacity:")
        opacity_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        opacity_label.setFixedWidth(self._label_width)
        layout.addWidget(opacity_label, 5, 0)

        self.connector_opacity_spin = SpinBox()
        self.connector_opacity_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.connector_opacity_spin.setRange(0, 255)
        self.connector_opacity_spin.setValue(self.current_style["connector_opacity"])
        self.connector_opacity_spin.valueChanged.connect(self._on_opacity_changed)
        layout.addWidget(self.connector_opacity_spin, 5, 1)

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

    def _on_connector_shape_changed(self, value: str):
        """Handle connector shape selection change."""
        self.current_style["connector_shape"] = value
        self._emit_style_changed()

    def _set_connector_style(self, value: str):
        """Set connector line style."""
        self.connector_style_combo.setText(value)
        style_map = {
            "Solid": "solid",
            "Dashed": "dashed",
            "Dotted": "dotted",
            "Dash-Dot": "dash_dot",
        }
        self.current_style["connector_style"] = style_map.get(value, "solid")
        self._emit_style_changed()

    def _on_width_changed(self, value: int):
        """Handle connector width change."""
        self.current_style["line_width"] = value
        self._emit_style_changed()

    def _on_color_clicked(self):
        """Handle connector color button click."""
        parent = self._advanced_tab if hasattr(self, '_advanced_tab') else None

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
                self._on_connector_color_pool_selected
            )

        # Show popup at button position with smart boundary detection
        button_pos = self.connector_color_btn.mapToGlobal(QPoint(0, self.connector_color_btn.height()))
        button_width = self.connector_color_btn.width()
        self._color_pool_popup.show_at(button_pos, button_width)

    def _on_brightness_changed(self, value: int):
        """Handle connector brightness change."""
        self.current_style["connector_brightness"] = value / 100.0
        self._emit_style_changed()

    def _on_opacity_changed(self, value: int):
        """Handle connector opacity change."""
        self.current_style["connector_opacity"] = value
        self._emit_style_changed()

    def _emit_style_changed(self):
        """Emit style changed signal."""
        self.style_changed.emit(self.current_style.copy())

    def _on_connector_color_pool_selected(self, color_index: int):
        """Handle connector color selection from pool selector popup.

        Args:
            color_index: The selected color index (0-7)
        """
        # Update connector_color_index in current_style
        self.current_style["connector_color_index"] = color_index

        # Update button display color
        parent = self._advanced_tab if hasattr(self, '_advanced_tab') else None
        if parent and hasattr(parent, "style_config") and parent.style_config:
            color_pool = parent.style_config.color_pool
            if color_index < len(color_pool):
                selected_color = color_pool[color_index]
                # Don't set text - let button show only color
                if hasattr(self, "connector_color_btn"):
                    self.connector_color_btn.setStyleSheet(
                        f"background-color: {selected_color}; "
                        "border: 1px solid #C8C8C8; "
                        "border-radius: 6px; "
                        "padding: 4px 24px 4px 12px; "
                        "font-size: 13px; "
                        "text-align: left;"
                    )

        # Emit style changed signal
        self._emit_style_changed()

    def get_style(self) -> dict:
        """Get current connector style."""
        return self.current_style.copy()

    def set_style(self, style: dict):
        """Set connector style programmatically."""
        self.current_style.update(style)

        if self._initialized:
            if "connector_shape" in style:
                self.connector_shape_btn.set_value(style["connector_shape"])

            if "connector_style" in style:
                style_map = {
                    "solid": "Solid",
                    "dashed": "Dashed",
                    "dotted": "Dotted",
                }
                self.connector_style_combo.setText(
                    style_map.get(style["connector_style"], "Solid")
                )

            if "line_width" in style:
                self.connector_width_spin.setValue(style["line_width"])

            # Update connector color button display
            if "connector_color_index" in style:
                parent = self._advanced_tab if hasattr(self, '_advanced_tab') else None
                if parent and hasattr(parent, "style_config") and parent.style_config:
                    color_pool = parent.style_config.color_pool
                    color_index = style["connector_color_index"]
                    if color_index < len(color_pool):
                        selected_color = color_pool[color_index]
                        # Don't set text - let button show only color
                        if hasattr(self, "connector_color_btn"):
                            self.connector_color_btn.setStyleSheet(
                                f"background-color: {selected_color}; "
                                "border: 1px solid #C8C8C8; "
                                "border-radius: 6px; "
                                "padding: 4px 24px 4px 12px; "
                                "font-size: 13px; "
                                "text-align: left;"
                            )
