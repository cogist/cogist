"""Border style section widget.

Provides controls for customizing node border appearance.
Implements lazy initialization for better performance.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QMenu,
    QSlider,
    QSpinBox,
)

from cogist.presentation.widgets import ToggleSwitch

from .collapsible_panel import CollapsiblePanel
from .menu_button import MenuButton


class BorderSection(CollapsiblePanel):
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

        # Get LABEL_WIDTH from parent (AdvancedStyleTab) if available, otherwise use class default
        self._label_width = getattr(parent, 'LABEL_WIDTH', self.LABEL_WIDTH) if parent else self.LABEL_WIDTH

        # State
        self._initialized = False
        self.current_style = {
            "enabled": True,
            "border_style": "solid",
            "border_width": 2,
            "border_color_index": 0,
            "brightness": 1.0,
            "opacity": 255,
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
        layout.setContentsMargins(self.GROUP_MARGIN, 6, self.GROUP_MARGIN, 6)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)

        row = 0

        # Border enabled - Toggle Switch (right-aligned)
        enabled_label = QLabel("Enabled:")
        enabled_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        enabled_label.setFixedWidth(self._label_width)
        layout.addWidget(enabled_label, row, 0)

        self.enabled_toggle = ToggleSwitch()
        self.enabled_toggle.set_checked(self.current_style.get("enabled", True))
        self.enabled_toggle.toggled.connect(self._on_enabled_changed)
        layout.addWidget(self.enabled_toggle, row, 1, alignment=Qt.AlignRight | Qt.AlignVCenter)
        row += 1

        # Border style
        style_label = QLabel("Style:")
        style_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        style_label.setFixedWidth(self._label_width)
        layout.addWidget(style_label, row, 0)

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

        self.border_width_spin = QSpinBox()
        self.border_width_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.border_width_spin.setRange(0, 10)
        self.border_width_spin.setValue(self.current_style["border_width"])
        self.border_width_spin.setAlignment(Qt.AlignLeft)
        self.border_width_spin.valueChanged.connect(self._on_width_changed)
        layout.addWidget(self.border_width_spin, row, 1)
        row += 1

        # Border color (placeholder - will be implemented later)
        color_label = QLabel("Color:")
        color_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        color_label.setFixedWidth(self._label_width)
        layout.addWidget(color_label, row, 0)

        self.color_btn = MenuButton("Color 1", self.WIDGET_HEIGHT)
        self.color_btn.setStyleSheet(self._button_style())
        self.color_btn.clicked.connect(self._on_color_clicked)
        layout.addWidget(self.color_btn, row, 1)
        row += 1

        # Brightness slider
        brightness_label = QLabel("Brightness:")
        brightness_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        brightness_label.setFixedWidth(self._label_width)
        layout.addWidget(brightness_label, row, 0)

        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(50, 150)  # 0.5-1.5
        self.brightness_slider.setValue(
            int(self.current_style.get("brightness", 1.0) * 100)
        )
        self.brightness_slider.setFixedHeight(self.WIDGET_HEIGHT)
        self.brightness_slider.valueChanged.connect(self._on_brightness_changed)
        layout.addWidget(self.brightness_slider, row, 1, alignment=Qt.AlignVCenter)
        row += 1

        # Opacity slider
        opacity_label = QLabel("Opacity:")
        opacity_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        opacity_label.setFixedWidth(self._label_width)
        layout.addWidget(opacity_label, row, 0)

        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(0, 255)
        self.opacity_slider.setValue(self.current_style.get("opacity", 255))
        self.opacity_slider.setFixedHeight(self.WIDGET_HEIGHT)
        self.opacity_slider.valueChanged.connect(self._on_opacity_changed)
        layout.addWidget(self.opacity_slider, row, 1, alignment=Qt.AlignVCenter)

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
        self.current_style["enabled"] = checked
        self._emit_style_changed()

    def _on_color_clicked(self):
        """Handle border color button click (placeholder)."""
        # TODO: Implement color picker dialog
        pass

    def _on_brightness_changed(self, value: int):
        """Handle border brightness change."""
        self.current_style["brightness"] = value / 100.0
        self._emit_style_changed()

    def _on_opacity_changed(self, value: int):
        """Handle border opacity change."""
        self.current_style["opacity"] = value
        self._emit_style_changed()

    def _emit_style_changed(self):
        """Emit style changed signal with only border-related fields."""
        # Only emit border-related fields to avoid overwriting other style properties
        border_only_style = {
            "border_style": self.current_style["border_style"],
            "border_width": self.current_style["border_width"],
        }
        self.style_changed.emit(border_only_style)

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
