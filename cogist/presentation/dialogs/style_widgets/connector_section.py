"""Connector (edge) style section widget.

Provides controls for customizing edge appearance between nodes.
Implements lazy initialization for better performance.
"""

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QMenu,
    QPushButton,
    QSpinBox,
)

from cogist.presentation.widgets import (
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


class ConnectorSection(CollapsiblePanel):
    """Connector style settings with lazy initialization.

    Signals:
        style_changed(dict): Emitted when connector style changes
    """

    style_changed = Signal(dict)

    # UI constants
    LABEL_WIDTH = 75
    WIDGET_HEIGHT = 32
    GROUP_MARGIN = 10

    def __init__(self, parent=None):
        super().__init__("Connector Style", collapsed=True, parent=parent)

        # State
        self._initialized = False
        self.current_style = {
            "connector_shape": "bezier",
            "connector_style": "solid",
            "line_width": 2,
            "connector_color": "#666666",
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
        layout.setContentsMargins(self.GROUP_MARGIN, 16, self.GROUP_MARGIN, 16)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)

        # Connector shape selector - using reusable VisualPreviewButton
        shape_label = QLabel("Shape:")
        shape_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        shape_label.setMinimumWidth(self.LABEL_WIDTH)
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
        style_label.setMinimumWidth(self.LABEL_WIDTH)
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
        width_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(width_label, 2, 0)

        self.connector_width_spin = QSpinBox()
        self.connector_width_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.connector_width_spin.setRange(1, 10)
        self.connector_width_spin.setValue(self.current_style["line_width"])
        self.connector_width_spin.setAlignment(Qt.AlignLeft)
        self.connector_width_spin.valueChanged.connect(self._on_width_changed)
        layout.addWidget(self.connector_width_spin, 2, 1)

        # Connector color
        color_label = QLabel("Color:")
        color_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        color_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(color_label, 3, 0)

        self.connector_color_btn = QPushButton()
        self.connector_color_btn.setFixedHeight(self.WIDGET_HEIGHT)
        self.connector_color_btn.setStyleSheet(
            f"background-color: {self.current_style['connector_color']}; "
            "border: 1px solid #ccc; border-radius: 6px;"
        )
        self.connector_color_btn.clicked.connect(self._pick_color)
        layout.addWidget(self.connector_color_btn, 3, 1)

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

    def _pick_color(self):
        """Open color picker dialog."""
        from PySide6.QtWidgets import QColorDialog

        current = QColor(self.current_style["connector_color"])
        color = QColorDialog.getColor(
            current, self, "Select Connector Color", QColorDialog.ShowAlphaChannel
        )

        if color.isValid():
            # Use name(QColor.HexArgb) to preserve alpha channel
            self.current_style["connector_color"] = color.name(QColor.HexArgb)
            self.connector_color_btn.setStyleSheet(
                f"background-color: {self.current_style['connector_color']}; "
                "border: 1px solid #ccc; border-radius: 6px;"
            )
            self._emit_style_changed()

    def _emit_style_changed(self):
        """Emit style changed signal."""
        self.style_changed.emit(self.current_style.copy())

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

            if "connector_color" in style:
                self.connector_color_btn.setStyleSheet(
                    f"background-color: {style['connector_color']}; "
                    "border: 1px solid #ccc; border-radius: 6px;"
                )
