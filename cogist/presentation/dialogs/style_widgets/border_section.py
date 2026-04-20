"""Border style section widget.

Provides controls for customizing node border appearance.
Implements lazy initialization for better performance.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGridLayout, QLabel, QMenu, QPushButton, QSpinBox

from .collapsible_panel import CollapsiblePanel


class BorderSection(CollapsiblePanel):
    """Border style settings with lazy initialization.

    Signals:
        style_changed(dict): Emitted when border style changes
    """

    style_changed = Signal(dict)

    # UI constants
    LABEL_WIDTH = 75
    WIDGET_HEIGHT = 32
    GROUP_MARGIN = 10

    def __init__(self, parent=None):
        super().__init__("Border Style", collapsed=True, parent=parent)

        # State
        self._initialized = False
        self.current_style = {
            "border_style": "solid",
            "border_width": 2,
            "border_color": "#1976D2",
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

        # Border style
        style_label = QLabel("Style:")
        style_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        style_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(style_label, 0, 0)

        self.border_style_combo = QPushButton("Solid")
        self.border_style_combo.setFixedHeight(self.WIDGET_HEIGHT)
        self.border_style_combo.setStyleSheet(self._button_style())

        self.border_style_menu = QMenu()
        self.border_style_menu.aboutToShow.connect(
            lambda: self.border_style_menu.setFixedWidth(self.border_style_combo.width())
        )

        border_styles = ["Solid", "Dashed", "Dotted", "Dash-Dot"]
        for style in border_styles:
            action = self.border_style_menu.addAction(style)
            action.triggered.connect(lambda _, s=style: self._set_border_style(s))

        self.border_style_combo.setMenu(self.border_style_menu)
        layout.addWidget(self.border_style_combo, 0, 1)

        # Border width
        width_label = QLabel("Width:")
        width_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        width_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(width_label, 1, 0)

        self.border_width_spin = QSpinBox()
        self.border_width_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.border_width_spin.setRange(0, 10)
        self.border_width_spin.setValue(self.current_style["border_width"])
        self.border_width_spin.setAlignment(Qt.AlignLeft)
        self.border_width_spin.valueChanged.connect(self._on_width_changed)
        layout.addWidget(self.border_width_spin, 1, 1)

        # Border color
        color_label = QLabel("Color:")
        color_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        color_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(color_label, 2, 0)

        self.border_color_btn = QPushButton()
        self.border_color_btn.setFixedHeight(self.WIDGET_HEIGHT)
        self.border_color_btn.setStyleSheet(
            f"background-color: {self.current_style['border_color']}; "
            "border: 1px solid #ccc; border-radius: 6px;"
        )
        self.border_color_btn.clicked.connect(self._pick_color)
        layout.addWidget(self.border_color_btn, 2, 1)

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

    def _pick_color(self):
        """Open color picker dialog."""
        from PySide6.QtWidgets import QColorDialog

        current = QColor(self.current_style["border_color"])
        color_dialog = QColorDialog(current, self)
        color_dialog.setWindowTitle("Select Border Color")

        # Position dialog to the right of the color button
        button_pos = self.border_color_btn.mapToGlobal(self.border_color_btn.rect().topLeft())
        button_width = self.border_color_btn.width()
        dialog_x = button_pos.x() + button_width + 4  # 4px gap to the right
        dialog_y = button_pos.y()  # Align top edges

        # Show dialog first, then move it (to avoid Qt's automatic positioning)
        color_dialog.show()
        color_dialog.move(dialog_x, dialog_y)

        if color_dialog.exec():
            color = color_dialog.currentColor()
            if color.isValid():
                self.current_style["border_color"] = color.name()
                self.border_color_btn.setStyleSheet(
                    f"background-color: {self.current_style['border_color']}; "
                    "border: 1px solid #ccc; border-radius: 6px;"
                )
                self._emit_style_changed()

    def _emit_style_changed(self):
        """Emit style changed signal."""
        self.style_changed.emit(self.current_style.copy())

    def get_style(self) -> dict:
        """Get current border style."""
        return self.current_style.copy()

    def set_style(self, style: dict):
        """Set border style programmatically."""
        self.current_style.update(style)

        if self._initialized:
            if "border_style" in style:
                style_map = {
                    "solid": "Solid",
                    "dashed": "Dashed",
                    "dotted": "Dotted",
                    "dash_dot": "Dash-Dot",
                }
                self.border_style_combo.setText(style_map.get(style["border_style"], "Solid"))

            if "border_width" in style:
                self.border_width_spin.setValue(style["border_width"])

            if "border_color" in style:
                self.border_color_btn.setStyleSheet(
                    f"background-color: {style['border_color']}; "
                    "border: 1px solid #ccc; border-radius: 6px;"
                )
