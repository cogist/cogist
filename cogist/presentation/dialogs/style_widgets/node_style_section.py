"""Node style section widget.

Provides controls for customizing node appearance including shape, colors,
padding, and font properties. Implements lazy initialization for better performance.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QMenu,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class NodeStyleSection(QGroupBox):
    """Node style settings with lazy initialization.
    
    Signals:
        style_changed(dict): Emitted when any node style property changes
    """
    
    style_changed = Signal(dict)
    
    # UI constants
    LABEL_WIDTH = 75
    WIDGET_HEIGHT = 32
    GROUP_MARGIN = 10
    
    def __init__(self, parent=None):
        super().__init__("Node Style", parent)
        
        # Make it collapsible
        self.setCheckable(True)
        self.setChecked(False)  # Default collapsed
        
        # State
        self._initialized = False
        self.current_style = self._get_default_style()
        
        # Connect toggle signal for lazy initialization
        self.toggled.connect(self._on_toggled)
    
    def _get_default_style(self) -> dict:
        """Get default node style."""
        return {
            "shape": "rounded_rect",
            "radius": 10,
            "bg_color": "#2196F3",
            "text_color": "#FFFFFF",
            "padding_w": 20,
            "padding_h": 16,
            "font_family": "Arial",
            "font_size": 14,
            "font_weight": "Normal",
            "font_italic": False,
            "font_underline": False,
            "font_strikeout": False,
        }
    
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
        
        row = 0
        
        # Shape selector
        shape_label = QLabel("Shape:")
        shape_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        shape_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(shape_label, row, 0)
        
        self.shape_combo = QPushButton("Rounded Rect")
        self.shape_combo.setFixedHeight(self.WIDGET_HEIGHT)
        self.shape_combo.setStyleSheet(self._button_style())
        
        self.shape_menu = QMenu()
        self.shape_menu.aboutToShow.connect(lambda: self.shape_menu.setFixedWidth(self.shape_combo.width()))
        
        shape_options = ["Rectangle", "Rounded Rect", "Circle"]
        for option in shape_options:
            action = self.shape_menu.addAction(option)
            action.triggered.connect(lambda _, opt=option: self._set_shape(opt))
        
        self.shape_combo.setMenu(self.shape_menu)
        layout.addWidget(self.shape_combo, row, 1)
        row += 1
        
        # Corner radius
        radius_label = QLabel("Radius:")
        radius_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        radius_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(radius_label, row, 0)
        
        self.radius_spin = QSpinBox()
        self.radius_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.radius_spin.setRange(0, 30)
        self.radius_spin.setValue(self.current_style["radius"])
        self.radius_spin.setAlignment(Qt.AlignLeft)
        self.radius_spin.valueChanged.connect(self._on_radius_changed)
        layout.addWidget(self.radius_spin, row, 1)
        row += 1
        
        # Background color
        bg_label = QLabel("Background:")
        bg_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        bg_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(bg_label, row, 0)
        
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setFixedHeight(self.WIDGET_HEIGHT)
        self.bg_color_btn.setStyleSheet(
            f"background-color: {self.current_style['bg_color']}; "
            "border: 1px solid #ccc; border-radius: 6px;"
        )
        self.bg_color_btn.clicked.connect(lambda: self._pick_color("bg_color"))
        layout.addWidget(self.bg_color_btn, row, 1)
        row += 1
        
        # Text color
        text_label = QLabel("Text Color:")
        text_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        text_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(text_label, row, 0)
        
        self.text_color_btn = QPushButton()
        self.text_color_btn.setFixedHeight(self.WIDGET_HEIGHT)
        self.text_color_btn.setStyleSheet(
            f"background-color: {self.current_style['text_color']}; "
            "border: 1px solid #ccc; border-radius: 6px;"
        )
        self.text_color_btn.clicked.connect(lambda: self._pick_color("text_color"))
        layout.addWidget(self.text_color_btn, row, 1)
        row += 1
        
        # Padding W
        padding_w_label = QLabel("Padding W:")
        padding_w_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        padding_w_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(padding_w_label, row, 0)
        
        self.padding_w_spin = QSpinBox()
        self.padding_w_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.padding_w_spin.setRange(0, 50)
        self.padding_w_spin.setValue(self.current_style["padding_w"])
        self.padding_w_spin.setAlignment(Qt.AlignLeft)
        self.padding_w_spin.valueChanged.connect(self._on_padding_changed)
        layout.addWidget(self.padding_w_spin, row, 1)
        row += 1
        
        # Padding H
        padding_h_label = QLabel("Padding H:")
        padding_h_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        padding_h_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(padding_h_label, row, 0)
        
        self.padding_h_spin = QSpinBox()
        self.padding_h_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.padding_h_spin.setRange(0, 50)
        self.padding_h_spin.setValue(self.current_style["padding_h"])
        self.padding_h_spin.setAlignment(Qt.AlignLeft)
        self.padding_h_spin.valueChanged.connect(self._on_padding_changed)
        layout.addWidget(self.padding_h_spin, row, 1)
        row += 1
        
        # Font family
        font_family_label = QLabel("Font:")
        font_family_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        font_family_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(font_family_label, row, 0)
        
        self.font_family_combo = QPushButton(self.current_style["font_family"])
        self.font_family_combo.setFixedHeight(self.WIDGET_HEIGHT)
        self.font_family_combo.setStyleSheet(self._button_style())
        self.font_family_combo.clicked.connect(self._show_font_dialog)
        layout.addWidget(self.font_family_combo, row, 1)
        row += 1
        
        # Font size
        font_size_label = QLabel("Font Size:")
        font_size_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        font_size_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(font_size_label, row, 0)
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setFixedHeight(self.WIDGET_HEIGHT)
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.setValue(self.current_style["font_size"])
        self.font_size_spin.setAlignment(Qt.AlignLeft)
        self.font_size_spin.valueChanged.connect(self._on_font_size_changed)
        layout.addWidget(self.font_size_spin, row, 1)
        row += 1
        
        # Font weight
        font_weight_label = QLabel("Weight:")
        font_weight_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        font_weight_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(font_weight_label, row, 0)
        
        self.font_weight_combo = QPushButton(self.current_style["font_weight"])
        self.font_weight_combo.setFixedHeight(self.WIDGET_HEIGHT)
        self.font_weight_combo.setStyleSheet(self._button_style())
        
        self.font_weight_menu = QMenu()
        self.font_weight_menu.aboutToShow.connect(
            lambda: self.font_weight_menu.setFixedWidth(self.font_weight_combo.width())
        )
        
        weight_options = ["Light", "Normal", "Bold", "ExtraBold"]
        for option in weight_options:
            action = self.font_weight_menu.addAction(option)
            action.triggered.connect(lambda _, opt=option: self._set_font_weight(opt))
        
        self.font_weight_combo.setMenu(self.font_weight_menu)
        layout.addWidget(self.font_weight_combo, row, 1)
        row += 1
        
        # Font style checkboxes
        font_style_label = QLabel("Font Style:")
        font_style_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        font_style_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(font_style_label, row, 0)
        
        style_layout = QVBoxLayout()
        style_layout.setSpacing(4)
        style_layout.setContentsMargins(0, 0, 0, 0)
        
        self.font_italic_check = QCheckBox("Italic")
        self.font_italic_check.setChecked(self.current_style["font_italic"])
        self.font_italic_check.setStyleSheet("QCheckBox { background: transparent; }")
        self.font_italic_check.toggled.connect(self._on_font_style_changed)
        style_layout.addWidget(self.font_italic_check)
        
        self.font_underline_check = QCheckBox("Underline")
        self.font_underline_check.setChecked(self.current_style["font_underline"])
        self.font_underline_check.setStyleSheet("QCheckBox { background: transparent; }")
        self.font_underline_check.toggled.connect(self._on_font_style_changed)
        style_layout.addWidget(self.font_underline_check)
        
        self.font_strikeout_check = QCheckBox("Strikeout")
        self.font_strikeout_check.setChecked(self.current_style["font_strikeout"])
        self.font_strikeout_check.setStyleSheet("QCheckBox { background: transparent; }")
        self.font_strikeout_check.toggled.connect(self._on_font_style_changed)
        style_layout.addWidget(self.font_strikeout_check)
        
        style_layout.addStretch()
        
        style_container = QWidget()
        style_container.setLayout(style_layout)
        layout.addWidget(style_container, row, 1)
        
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
    
    def _set_shape(self, value: str):
        """Set node shape."""
        self.shape_combo.setText(value)
        shape_map = {
            "Rectangle": "rect",
            "Rounded Rect": "rounded_rect",
            "Circle": "circle",
        }
        self.current_style["shape"] = shape_map.get(value, "rounded_rect")
        self._emit_style_changed()
    
    def _on_radius_changed(self, value: int):
        """Handle radius change."""
        self.current_style["radius"] = value
        self._emit_style_changed()
    
    def _pick_color(self, color_type: str):
        """Open color picker dialog."""
        from PySide6.QtWidgets import QColorDialog
        
        current_color = self.current_style.get(f"{color_type}", "#FFFFFF")
        current = QColor(current_color)
        color = QColorDialog.getColor(current, self, f"Select {color_type.replace('_', ' ').title()} Color")
        
        if color.isValid():
            color_name = color.name()
            self.current_style[color_type] = color_name
            
            # Update button appearance
            if color_type == "bg_color":
                self.bg_color_btn.setStyleSheet(
                    f"background-color: {color_name}; border: 1px solid #ccc; border-radius: 6px;"
                )
            elif color_type == "text_color":
                self.text_color_btn.setStyleSheet(
                    f"background-color: {color_name}; border: 1px solid #ccc; border-radius: 6px;"
                )
            
            self._emit_style_changed()
    
    def _on_padding_changed(self):
        """Handle padding changes."""
        self.current_style["padding_w"] = self.padding_w_spin.value()
        self.current_style["padding_h"] = self.padding_h_spin.value()
        self._emit_style_changed()
    
    def _show_font_dialog(self):
        """Show font selection dialog."""
        from PySide6.QtWidgets import QFontDialog
        from PySide6.QtGui import QFont
        
        current_font = QFont(self.current_style["font_family"], self.current_style["font_size"])
        font, ok = QFontDialog.getFont(current_font, self, "Select Font")
        
        if ok:
            self.current_style["font_family"] = font.family()
            self.current_style["font_size"] = font.pointSize()
            self.font_family_combo.setText(font.family())
            self.font_size_spin.setValue(font.pointSize())
            self._emit_style_changed()
    
    def _on_font_size_changed(self, value: int):
        """Handle font size change."""
        self.current_style["font_size"] = value
        self._emit_style_changed()
    
    def _set_font_weight(self, value: str):
        """Set font weight."""
        self.font_weight_combo.setText(value)
        self.current_style["font_weight"] = value
        self._emit_style_changed()
    
    def _on_font_style_changed(self):
        """Handle font style checkbox changes."""
        self.current_style["font_italic"] = self.font_italic_check.isChecked()
        self.current_style["font_underline"] = self.font_underline_check.isChecked()
        self.current_style["font_strikeout"] = self.font_strikeout_check.isChecked()
        self._emit_style_changed()
    
    def _emit_style_changed(self):
        """Emit style changed signal with current style dict."""
        self.style_changed.emit(self.current_style.copy())
    
    def get_style(self) -> dict:
        """Get current node style."""
        return self.current_style.copy()
    
    def set_style(self, style: dict):
        """Set node style programmatically.
        
        Args:
            style: Dictionary containing node style properties
        """
        self.current_style.update(style)
        
        # Update UI if initialized
        if self._initialized:
            if "shape" in style:
                shape_map = {
                    "rect": "Rectangle",
                    "rounded_rect": "Rounded Rect",
                    "circle": "Circle",
                }
                self.shape_combo.setText(shape_map.get(style["shape"], "Rounded Rect"))
            
            if "radius" in style:
                self.radius_spin.setValue(style["radius"])
            
            if "bg_color" in style:
                self.bg_color_btn.setStyleSheet(
                    f"background-color: {style['bg_color']}; border: 1px solid #ccc; border-radius: 6px;"
                )
            
            if "text_color" in style:
                self.text_color_btn.setStyleSheet(
                    f"background-color: {style['text_color']}; border: 1px solid #ccc; border-radius: 6px;"
                )
            
            if "padding_w" in style:
                self.padding_w_spin.setValue(style["padding_w"])
            if "padding_h" in style:
                self.padding_h_spin.setValue(style["padding_h"])
            
            if "font_family" in style:
                self.font_family_combo.setText(style["font_family"])
            if "font_size" in style:
                self.font_size_spin.setValue(style["font_size"])
            if "font_weight" in style:
                self.font_weight_combo.setText(style["font_weight"])
            
            if "font_italic" in style:
                self.font_italic_check.setChecked(style["font_italic"])
            if "font_underline" in style:
                self.font_underline_check.setChecked(style["font_underline"])
            if "font_strikeout" in style:
                self.font_strikeout_check.setChecked(style["font_strikeout"])
