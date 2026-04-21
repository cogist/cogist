"""Connector (edge) style section widget.

Provides controls for customizing edge appearance between nodes.
Implements lazy initialization for better performance.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGridLayout, QLabel, QMenu, QPushButton, QSpinBox

from .collapsible_panel import CollapsiblePanel


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
            "connector_type": "bezier",
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

        # Connector type
        type_label = QLabel("Type:")
        type_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        type_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(type_label, 0, 0)

        # Get initial connector shape from current_style
        connector_type_map = {
            "straight": "Straight",
            "orthogonal": "Orthogonal",
            "bezier": "Bezier",
        }
        initial_connector_type = connector_type_map.get(self.current_style.get("connector_shape", "bezier"), "Bezier")
        self.connector_type_combo = QPushButton(initial_connector_type)
        self.connector_type_combo.setFixedHeight(self.WIDGET_HEIGHT)
        self.connector_type_combo.setStyleSheet(self._button_style())

        self.connector_type_menu = QMenu()
        self.connector_type_menu.aboutToShow.connect(
            lambda: self.connector_type_menu.setFixedWidth(self.connector_type_combo.width())
        )

        connector_types = ["Straight", "Orthogonal", "Bezier"]
        for ctype in connector_types:
            action = self.connector_type_menu.addAction(ctype)
            action.triggered.connect(lambda _, t=ctype: self._set_connector_type(t))

        self.connector_type_combo.setMenu(self.connector_type_menu)
        layout.addWidget(self.connector_type_combo, 0, 1)

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
        initial_connector_style = connector_style_map.get(self.current_style.get("connector_style", "solid"), "Solid")
        self.connector_style_combo = QPushButton(initial_connector_style)
        self.connector_style_combo.setFixedHeight(self.WIDGET_HEIGHT)
        self.connector_style_combo.setStyleSheet(self._button_style())

        self.connector_style_menu = QMenu()
        self.connector_style_menu.aboutToShow.connect(
            lambda: self.connector_style_menu.setFixedWidth(self.connector_style_combo.width())
        )

        connector_styles = ["Solid", "Dashed", "Dotted", "Dash-Dot"]
        for cstyle in connector_styles:
            action = self.connector_style_menu.addAction(cstyle)
            action.triggered.connect(lambda _, s=cstyle: self._set_connector_style(s))

        self.connector_style_combo.setMenu(self.connector_style_menu)
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

    def _set_connector_type(self, value: str):
        """Set connector shape."""
        self.connector_type_combo.setText(value)
        type_map = {
            "Straight": "straight",
            "Orthogonal": "orthogonal",
            "Bezier": "bezier",
        }
        self.current_style["connector_shape"] = type_map.get(value, "bezier")
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
        color = QColorDialog.getColor(current, self, "Select Connector Color", QColorDialog.ShowAlphaChannel)

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
                type_map = {
                    "straight": "Straight",
                    "orthogonal": "Orthogonal",
                    "bezier": "Bezier",
                }
                self.connector_type_combo.setText(type_map.get(style["connector_shape"], "Bezier"))

            if "connector_style" in style:
                style_map = {
                    "solid": "Solid",
                    "dashed": "Dashed",
                    "dotted": "Dotted",
                }
                self.connector_style_combo.setText(style_map.get(style["connector_style"], "Solid"))

            if "line_width" in style:
                self.connector_width_spin.setValue(style["line_width"])

            if "connector_color" in style:
                self.connector_color_btn.setStyleSheet(
                    f"background-color: {style['connector_color']}; "
                    "border: 1px solid #ccc; border-radius: 6px;"
                )
