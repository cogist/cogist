"""
Style Panel - Advanced Mode for Template Creation

A dockable panel for real-time style debugging and template creation.
Allows developers to tweak style parameters by layer and see immediate results.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class StylePanel(QWidget):
    """Advanced style panel for template creation with layer-based editing."""

    # Panel dimensions
    PANEL_WIDTH = 260
    LABEL_WIDTH = 75
    WIDGET_WIDTH = 133  # Calculated: 260 - 12*2 - 1*2 - 10*2 - 75 - 6 = 133
    WIDGET_HEIGHT = 32
    PANEL_MARGIN = 12  # Left/right margins for panel edges
    GROUP_MARGIN = 10  # Left/right margins inside group boxes

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set initial width (fixed, non-resizable)
        self.setMinimumWidth(self.PANEL_WIDTH)
        self.setMaximumWidth(self.PANEL_WIDTH)

        # Create main widget
        self.main_widget = QWidget()

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

        # Apply custom styles
        self._apply_styles()

        self._init_ui()
        
        # Set initial visibility based on default layer (canvas)
        self.canvas_group.setVisible(True)
        self.node_style_group.setVisible(False)
        self.border_group.setVisible(False)
        self.connector_group.setVisible(False)
        
        self._load_current_layer_style()

    def _apply_styles(self):
        """Apply custom QSS styles to the panel."""
        self.setStyleSheet("""
            StylePanel {
                background-color: #F5F5F5;
            }
            QGroupBox {
                background-color: #FFFFFF;
                border: 1px solid #C8C8C8;
                border-radius: 8px;
                margin-top: 24px;
                padding-top: 12px;
                padding-bottom: 12px;
                margin-bottom: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 12px;
                background-color: transparent;
                font-weight: bold;
                font-size: 13px;
            }
            QGroupBox QPushButton,
            QGroupBox QSpinBox,
            QGroupBox QComboBox,
            QGroupBox QLineEdit,
            QGroupBox QCheckBox {
                border: 1px solid #C8C8C8;
                border-radius: 6px;
                background-color: #FFFFFF;
            }
            QGroupBox QPushButton:hover,
            QGroupBox QSpinBox:hover,
            QGroupBox QComboBox:hover {
                border-color: #A0A0A0;
            }
            QLabel {
                background-color: transparent;
            }
            QPushButton#bg_color_btn, QPushButton#text_color_btn, 
            QPushButton#border_color_btn, QPushButton#connector_color_btn {
                border: 1px solid #C8C8C8;
            }
        """)

    def _get_default_canvas_style(self):
        """Get default canvas style."""
        return {
            "bg_color": "#FFFFFF",
        }

    def _get_default_layer_style(self, layer_type):
        """Get default style for a layer."""
        # Base defaults
        style = {
            # Shape
            "shape": "rounded_rect",  # rect, rounded_rect, circle
            
            # Background
            "bg_color": "#2196F3",
            
            # Text
            "text_color": "#FFFFFF",
            "font_family": "Arial",
            "font_size": 22,
            "font_weight": "Bold",
            "font_italic": False,
            "font_underline": False,
            
            # Border
            "border_style": "solid",  # solid, dashed, dotted, dash_dot
            "border_width": 2,
            "border_color": "#1976D2",
            
            # Padding
            "padding_w": 20,
            "padding_h": 16,
            
            # Corner radius
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
            "connector_type": "bezier",  # straight, orthogonal, bezier
            "connector_style": "solid",  # solid, dashed, dotted
            "start_width": 6.0,  # Width at source node
            "end_width": 2.0,    # Width at target node (6 - 4 = 2)
            "connector_color": "#666666",
        }

    def _init_ui(self):
        """Initialize the user interface."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        content_widget = QWidget()
        content_widget.setMinimumWidth(self.PANEL_WIDTH)
        content_widget.setMaximumWidth(self.PANEL_WIDTH)
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(10)

        label_width = self.LABEL_WIDTH
        widget_height = self.WIDGET_HEIGHT

        # === Layer Selection ===
        layer_group = QGroupBox("Layer Selection")
        layer_grid = QGridLayout()
        layer_grid.setSpacing(6)
        layer_grid.setContentsMargins(self.GROUP_MARGIN, 16, self.GROUP_MARGIN, 16)
        layer_grid.setColumnStretch(0, 0)
        layer_grid.setColumnStretch(1, 1)
        
        layer_label = QLabel("Layer:")
        layer_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layer_label.setMinimumWidth(label_width)
        layer_grid.addWidget(layer_label, 0, 0)

        self.layer_combo = QPushButton("Canvas")
        self.layer_combo.setFixedHeight(widget_height)
        self.layer_combo.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #C8C8C8;
                border-radius: 6px;
                padding: 4px 24px 4px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
                border-color: #A0A0A0;
            }
        """)
        self.layer_menu = QMenu()
        self.layer_menu.aboutToShow.connect(
            lambda: self._adjust_menu_width(self.layer_menu, self.layer_combo)
        )
        layer_options = [
            "Canvas",
            "---",
            "Root",
            "Level 1",
            "Level 2",
            "Level 3+",
            "---",
            "Critical",
            "Minor",
        ]
        for option in layer_options:
            if option == "---":
                self.layer_menu.addSeparator()
            else:
                action = self.layer_menu.addAction(option)
                action.triggered.connect(lambda _, opt=option: self._set_layer(opt))
        self.layer_combo.setMenu(self.layer_menu)
        layer_grid.addWidget(self.layer_combo, 0, 1)
        layer_group.setLayout(layer_grid)
        layout.addWidget(layer_group)

        # === Canvas Background (only visible for canvas layer) ===
        self.canvas_group = QGroupBox("Canvas Background")
        canvas_grid = QGridLayout()
        canvas_grid.setSpacing(6)
        canvas_grid.setContentsMargins(self.GROUP_MARGIN, 16, self.GROUP_MARGIN, 16)
        canvas_grid.setColumnStretch(0, 0)
        canvas_grid.setColumnStretch(1, 1)
        
        canvas_bg_label = QLabel("Background:")
        canvas_bg_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        canvas_bg_label.setMinimumWidth(label_width)
        canvas_grid.addWidget(canvas_bg_label, 0, 0)
        
        self.canvas_bg_btn = QPushButton()
        self.canvas_bg_btn.setFixedHeight(widget_height)
        self.canvas_bg_btn.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid #ccc; border-radius: 6px;"
        )
        self.canvas_bg_btn.clicked.connect(lambda: self._pick_color("canvas_bg"))
        canvas_grid.addWidget(self.canvas_bg_btn, 0, 1)
        
        self.canvas_group.setLayout(canvas_grid)
        layout.addWidget(self.canvas_group)

        # === Node Style ===
        self.node_style_group = QGroupBox("Node Style")
        node_grid = QGridLayout()
        node_grid.setSpacing(6)
        node_grid.setContentsMargins(self.GROUP_MARGIN, 16, self.GROUP_MARGIN, 16)
        node_grid.setColumnStretch(0, 0)
        node_grid.setColumnStretch(1, 1)

        # Shape (first item)
        shape_label = QLabel("Shape:")
        shape_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        shape_label.setMinimumWidth(label_width)
        node_grid.addWidget(shape_label, 0, 0)
        
        self.shape_combo = QPushButton("Rounded Rect")
        self.shape_combo.setFixedHeight(widget_height)
        self.shape_combo.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #C8C8C8;
                border-radius: 6px;
                padding: 4px 24px 4px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
                border-color: #A0A0A0;
            }
        """)
        self.shape_menu = QMenu()
        self.shape_menu.aboutToShow.connect(
            lambda: self._adjust_menu_width(self.shape_menu, self.shape_combo)
        )
        shape_options = ["Rectangle", "Rounded Rect", "Circle"]
        for option in shape_options:
            action = self.shape_menu.addAction(option)
            action.triggered.connect(lambda _, opt=option: self._set_shape(opt))
        self.shape_combo.setMenu(self.shape_menu)
        node_grid.addWidget(self.shape_combo, 0, 1)

        # Background color
        bg_label = QLabel("Background:")
        bg_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        bg_label.setMinimumWidth(label_width)
        node_grid.addWidget(bg_label, 1, 0)
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setFixedHeight(widget_height)
        self.bg_color_btn.setStyleSheet(
            "background-color: #2196F3; border: 1px solid #ccc; border-radius: 6px;"
        )
        self.bg_color_btn.clicked.connect(lambda: self._pick_color("bg_color"))
        node_grid.addWidget(self.bg_color_btn, 1, 1)

        # Text color
        text_label = QLabel("Text Color:")
        text_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        text_label.setMinimumWidth(label_width)
        node_grid.addWidget(text_label, 2, 0)
        self.text_color_btn = QPushButton()
        self.text_color_btn.setFixedHeight(widget_height)
        self.text_color_btn.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid #ccc; border-radius: 6px;"
        )
        self.text_color_btn.clicked.connect(lambda: self._pick_color("text_color"))
        node_grid.addWidget(self.text_color_btn, 2, 1)

        # Font family
        font_family_label = QLabel("Font:")
        font_family_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        font_family_label.setMinimumWidth(label_width)
        node_grid.addWidget(font_family_label, 3, 0)
        self.font_family_combo = QPushButton("Arial")
        self.font_family_combo.setFixedHeight(widget_height)
        self.font_family_combo.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #C8C8C8;
                border-radius: 6px;
                padding: 4px 24px 4px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
                border-color: #A0A0A0;
            }
        """)
        self.font_family_menu = QMenu()
        self.font_family_menu.aboutToShow.connect(
            lambda: self._adjust_menu_width(self.font_family_menu, self.font_family_combo)
        )
        font_families = ["Arial", "Helvetica", "Times New Roman", "Courier New", "Georgia", "Verdana"]
        for family in font_families:
            action = self.font_family_menu.addAction(family)
            action.triggered.connect(lambda _, f=family: self._set_font_family(f))
        self.font_family_combo.setMenu(self.font_family_menu)
        node_grid.addWidget(self.font_family_combo, 3, 1)

        # Font size
        font_size_label = QLabel("Font Size:")
        font_size_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        font_size_label.setMinimumWidth(label_width)
        node_grid.addWidget(font_size_label, 4, 0)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setFixedHeight(widget_height)
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.setValue(22)
        self.font_size_spin.setAlignment(Qt.AlignCenter)
        self.font_size_spin.valueChanged.connect(self._update_preview)
        node_grid.addWidget(self.font_size_spin, 4, 1)

        # Font weight
        font_weight_label = QLabel("Weight:")
        font_weight_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        font_weight_label.setMinimumWidth(label_width)
        node_grid.addWidget(font_weight_label, 5, 0)
        self.font_weight_combo = QPushButton("Bold")
        self.font_weight_combo.setFixedHeight(widget_height)
        self.font_weight_combo.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #C8C8C8;
                border-radius: 6px;
                padding: 4px 24px 4px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
                border-color: #A0A0A0;
            }
        """)
        self.font_weight_menu = QMenu()
        self.font_weight_menu.aboutToShow.connect(
            lambda: self._adjust_menu_width(self.font_weight_menu, self.font_weight_combo)
        )
        weight_options = ["Light", "Normal", "Bold", "ExtraBold"]
        for option in weight_options:
            action = self.font_weight_menu.addAction(option)
            action.triggered.connect(lambda _, opt=option: self._set_font_weight(opt))
        self.font_weight_combo.setMenu(self.font_weight_menu)
        node_grid.addWidget(self.font_weight_combo, 5, 1)

        # Font style checkboxes (Italic, Underline, Strikeout)
        font_style_label = QLabel("Style:")
        font_style_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        font_style_label.setMinimumWidth(label_width)
        node_grid.addWidget(font_style_label, 6, 0)
        
        # Create a horizontal layout for the three checkboxes
        style_layout = QHBoxLayout()
        style_layout.setSpacing(8)
        style_layout.setContentsMargins(0, 0, 0, 0)
        
        self.font_italic_check = QCheckBox("Italic")
        self.font_italic_check.setStyleSheet("QCheckBox { background: transparent; }")
        self.font_italic_check.toggled.connect(self._update_preview)
        style_layout.addWidget(self.font_italic_check)
        
        self.font_underline_check = QCheckBox("Underline")
        self.font_underline_check.setStyleSheet("QCheckBox { background: transparent; }")
        self.font_underline_check.toggled.connect(self._update_preview)
        style_layout.addWidget(self.font_underline_check)
        
        self.font_strikeout_check = QCheckBox("Strikeout")
        self.font_strikeout_check.setStyleSheet("QCheckBox { background: transparent; }")
        self.font_strikeout_check.toggled.connect(self._update_preview)
        style_layout.addWidget(self.font_strikeout_check)
        
        style_layout.addStretch()
        
        # Create a container widget for the checkboxes
        style_container = QWidget()
        style_container.setLayout(style_layout)
        node_grid.addWidget(style_container, 6, 1)

        # Padding
        padding_w_label = QLabel("Padding W:")
        padding_w_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        padding_w_label.setMinimumWidth(label_width)
        node_grid.addWidget(padding_w_label, 7, 0)
        self.padding_w_spin = QSpinBox()
        self.padding_w_spin.setFixedHeight(widget_height)
        self.padding_w_spin.setRange(0, 50)
        self.padding_w_spin.setValue(20)
        self.padding_w_spin.setAlignment(Qt.AlignCenter)
        self.padding_w_spin.valueChanged.connect(self._update_preview)
        node_grid.addWidget(self.padding_w_spin, 7, 1)

        padding_h_label = QLabel("Padding H:")
        padding_h_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        padding_h_label.setMinimumWidth(label_width)
        node_grid.addWidget(padding_h_label, 8, 0)
        self.padding_h_spin = QSpinBox()
        self.padding_h_spin.setFixedHeight(widget_height)
        self.padding_h_spin.setRange(0, 50)
        self.padding_h_spin.setValue(16)
        self.padding_h_spin.setAlignment(Qt.AlignCenter)
        self.padding_h_spin.valueChanged.connect(self._update_preview)
        node_grid.addWidget(self.padding_h_spin, 8, 1)

        # Corner radius
        radius_label = QLabel("Radius:")
        radius_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        radius_label.setMinimumWidth(label_width)
        node_grid.addWidget(radius_label, 9, 0)
        self.radius_spin = QSpinBox()
        self.radius_spin.setFixedHeight(widget_height)
        self.radius_spin.setRange(0, 30)
        self.radius_spin.setValue(10)
        self.radius_spin.setAlignment(Qt.AlignCenter)
        self.radius_spin.valueChanged.connect(self._update_preview)
        node_grid.addWidget(self.radius_spin, 9, 1)

        self.node_style_group.setLayout(node_grid)
        layout.addWidget(self.node_style_group)

        # === Border Style ===
        self.border_group = QGroupBox("Border Style")
        border_grid = QGridLayout()
        border_grid.setSpacing(6)
        border_grid.setContentsMargins(self.GROUP_MARGIN, 16, self.GROUP_MARGIN, 16)
        border_grid.setColumnStretch(0, 0)
        border_grid.setColumnStretch(1, 1)

        # Border style (solid/dashed/etc)
        border_style_label = QLabel("Style:")
        border_style_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        border_style_label.setMinimumWidth(label_width)
        border_grid.addWidget(border_style_label, 0, 0)
        self.border_style_combo = QPushButton("Solid")
        self.border_style_combo.setFixedHeight(widget_height)
        self.border_style_combo.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #C8C8C8;
                border-radius: 6px;
                padding: 4px 24px 4px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
                border-color: #A0A0A0;
            }
        """)
        self.border_style_menu = QMenu()
        self.border_style_menu.aboutToShow.connect(
            lambda: self._adjust_menu_width(self.border_style_menu, self.border_style_combo)
        )
        border_styles = ["Solid", "Dashed", "Dotted", "Dash-Dot"]
        for style in border_styles:
            action = self.border_style_menu.addAction(style)
            action.triggered.connect(lambda _, s=style: self._set_border_style(s))
        self.border_style_combo.setMenu(self.border_style_menu)
        border_grid.addWidget(self.border_style_combo, 0, 1)

        # Border width
        border_width_label = QLabel("Width:")
        border_width_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        border_width_label.setMinimumWidth(label_width)
        border_grid.addWidget(border_width_label, 1, 0)
        self.border_width_spin = QSpinBox()
        self.border_width_spin.setFixedHeight(widget_height)
        self.border_width_spin.setRange(0, 10)
        self.border_width_spin.setValue(2)
        self.border_width_spin.setAlignment(Qt.AlignCenter)
        self.border_width_spin.valueChanged.connect(self._update_preview)
        border_grid.addWidget(self.border_width_spin, 1, 1)

        # Border color
        border_color_label = QLabel("Color:")
        border_color_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        border_color_label.setMinimumWidth(label_width)
        border_grid.addWidget(border_color_label, 2, 0)
        self.border_color_btn = QPushButton()
        self.border_color_btn.setFixedHeight(widget_height)
        self.border_color_btn.setStyleSheet(
            "background-color: #1976D2; border: 1px solid #ccc; border-radius: 6px;"
        )
        self.border_color_btn.clicked.connect(lambda: self._pick_color("border_color"))
        border_grid.addWidget(self.border_color_btn, 2, 1)

        self.border_group.setLayout(border_grid)
        layout.addWidget(self.border_group)

        # === Connector Style ===
        self.connector_group = QGroupBox("Connector Style")
        connector_grid = QGridLayout()
        connector_grid.setSpacing(6)
        connector_grid.setContentsMargins(self.GROUP_MARGIN, 16, self.GROUP_MARGIN, 16)
        connector_grid.setColumnStretch(0, 0)
        connector_grid.setColumnStretch(1, 1)

        # Connector type
        connector_type_label = QLabel("Type:")
        connector_type_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        connector_type_label.setMinimumWidth(label_width)
        connector_grid.addWidget(connector_type_label, 0, 0)
        self.connector_type_combo = QPushButton("Bezier")
        self.connector_type_combo.setFixedHeight(widget_height)
        self.connector_type_combo.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #C8C8C8;
                border-radius: 6px;
                padding: 4px 24px 4px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
                border-color: #A0A0A0;
            }
        """)
        self.connector_type_menu = QMenu()
        self.connector_type_menu.aboutToShow.connect(
            lambda: self._adjust_menu_width(self.connector_type_menu, self.connector_type_combo)
        )
        connector_types = ["Straight", "Orthogonal", "Bezier"]
        for ctype in connector_types:
            action = self.connector_type_menu.addAction(ctype)
            action.triggered.connect(lambda _, t=ctype: self._set_connector_type(t))
        self.connector_type_combo.setMenu(self.connector_type_menu)
        connector_grid.addWidget(self.connector_type_combo, 0, 1)

        # Connector style
        connector_style_label = QLabel("Style:")
        connector_style_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        connector_style_label.setMinimumWidth(label_width)
        connector_grid.addWidget(connector_style_label, 1, 0)
        self.connector_style_combo = QPushButton("Solid")
        self.connector_style_combo.setFixedHeight(widget_height)
        self.connector_style_combo.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #C8C8C8;
                border-radius: 6px;
                padding: 4px 24px 4px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
                border-color: #A0A0A0;
            }
        """)
        self.connector_style_menu = QMenu()
        self.connector_style_menu.aboutToShow.connect(
            lambda: self._adjust_menu_width(self.connector_style_menu, self.connector_style_combo)
        )
        connector_styles = ["Solid", "Dashed", "Dotted"]
        for cstyle in connector_styles:
            action = self.connector_style_menu.addAction(cstyle)
            action.triggered.connect(lambda _, s=cstyle: self._set_connector_style(s))
        self.connector_style_combo.setMenu(self.connector_style_menu)
        connector_grid.addWidget(self.connector_style_combo, 1, 1)

        # Connector width
        connector_width_label = QLabel("Width:")
        connector_width_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        connector_width_label.setMinimumWidth(label_width)
        connector_grid.addWidget(connector_width_label, 2, 0)
        self.connector_width_spin = QSpinBox()
        self.connector_width_spin.setFixedHeight(widget_height)
        self.connector_width_spin.setRange(1, 10)
        self.connector_width_spin.setValue(2)
        self.connector_width_spin.setAlignment(Qt.AlignCenter)
        self.connector_width_spin.valueChanged.connect(self._set_connector_width)
        connector_grid.addWidget(self.connector_width_spin, 2, 1)

        # Connector color
        connector_color_label = QLabel("Color:")
        connector_color_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        connector_color_label.setMinimumWidth(label_width)
        connector_grid.addWidget(connector_color_label, 3, 0)
        self.connector_color_btn = QPushButton()
        self.connector_color_btn.setFixedHeight(widget_height)
        self.connector_color_btn.setStyleSheet(
            "background-color: #666666; border: 1px solid #ccc; border-radius: 6px;"
        )
        self.connector_color_btn.clicked.connect(lambda: self._pick_color("connector_color"))
        connector_grid.addWidget(self.connector_color_btn, 3, 1)

        self.connector_group.setLayout(connector_grid)
        layout.addWidget(self.connector_group)

        layout.addStretch()

        scroll.setWidget(content_widget)

        main_layout = QVBoxLayout(self.main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(self.main_widget)

    def _adjust_menu_width(self, menu: QMenu, button: QPushButton):
        """Adjust the menu width to match the button width."""
        menu.setFixedWidth(button.width())

    def _set_layer(self, value: str):
        """Set the current layer and update UI visibility."""
        # Save current layer style before switching
        self._save_current_layer_style()
        
        # Update layer name
        self.layer_combo.setText(value)
        
        # Map display name to internal name
        layer_map = {
            "Canvas": "canvas",
            "Root": "root",
            "Level 1": "level_1",
            "Level 2": "level_2",
            "Level 3+": "level_3_plus",
            "Critical": "critical",
            "Minor": "minor",
        }
        self.current_layer = layer_map.get(value, "canvas")
        
        # Show/hide sections based on layer type
        is_canvas = (self.current_layer == "canvas")
        is_priority = (self.current_layer in ["critical", "minor"])
        
        self.canvas_group.setVisible(is_canvas)
        self.node_style_group.setVisible(not is_canvas)
        self.border_group.setVisible(not is_canvas)
        # Connector style: hide for canvas and priority layers
        self.connector_group.setVisible(not is_canvas and not is_priority)
        
        # Load style for selected layer
        self._load_current_layer_style()
        
        print(f"Switched to layer: {self.current_layer}")

    def _set_shape(self, value: str):
        """Set node shape."""
        self.shape_combo.setText(value)
        shape_map = {
            "Rectangle": "rect",
            "Rounded Rect": "rounded_rect",
            "Circle": "circle",
        }
        self.layer_styles[self.current_layer]["shape"] = shape_map.get(value, "rounded_rect")
        self._update_preview()

    def _set_font_family(self, value: str):
        """Set font family."""
        self.font_family_combo.setText(value)
        self.layer_styles[self.current_layer]["font_family"] = value
        self._update_preview()

    def _set_font_weight(self, value: str):
        """Set font weight."""
        self.font_weight_combo.setText(value)
        self.layer_styles[self.current_layer]["font_weight"] = value
        self._update_preview()

    def _set_border_style(self, value: str):
        """Set border style."""
        self.border_style_combo.setText(value)
        style_map = {
            "Solid": "solid",
            "Dashed": "dashed",
            "Dotted": "dotted",
            "Dash-Dot": "dash_dot",
        }
        self.layer_styles[self.current_layer]["border_style"] = style_map.get(value, "solid")
        self._update_preview()

    def _set_connector_type(self, value: str):
        """Set connector type."""
        self.connector_type_combo.setText(value)
        type_map = {
            "Straight": "straight",
            "Orthogonal": "orthogonal",
            "Bezier": "bezier",
        }
        new_type = type_map.get(value, "bezier")
        old_type = self.connector_style.get("connector_type", "bezier")
        self.connector_style["connector_type"] = new_type
        
        # Recalculate widths when switching between straight and tapered
        if new_type != old_type:
            current_ui_width = self.connector_width_spin.value()
            self._set_connector_width(current_ui_width)
        
        self._update_preview()

    def _set_connector_style(self, value: str):
        """Set connector line style."""
        self.connector_style_combo.setText(value)
        style_map = {
            "Solid": "solid",
            "Dashed": "dashed",
            "Dotted": "dotted",
        }
        self.connector_style["connector_style"] = style_map.get(value, "solid")
        self._update_preview()

    def _set_connector_width(self, value: int):
        """Set connector width with mapping logic.
        
        For tapered lines (bezier/orthogonal): end_width = start_width + 4
        For straight lines: start_width = end_width = value
        """
        is_straight = (self.connector_style.get("connector_type") == "straight")
        
        if is_straight:
            # Equal width for straight lines
            self.connector_style["start_width"] = float(value)
            self.connector_style["end_width"] = float(value)
        else:
            # Tapered width for bezier/orthogonal
            self.connector_style["start_width"] = float(value)
            self.connector_style["end_width"] = float(value + 4)
        
        self._update_preview()

    def _pick_color(self, param_name):
        """Open color picker dialog."""
        if param_name == "canvas_bg":
            current_color = self.layer_styles["canvas"].get("bg_color", "#FFFFFF")
        elif param_name == "connector_color":
            current_color = self.connector_style.get("connector_color", "#666666")
        else:
            current_color = self.layer_styles[self.current_layer].get(param_name, "#000000")
        
        # Enable alpha channel support
        color = QColorDialog.getColor(current_color, self, options=QColorDialog.ShowAlphaChannel)

        if color.isValid():
            # Use ARGB format to preserve alpha channel
            hex_color = color.name(QColor.HexArgb)
            
            if param_name == "canvas_bg":
                self.layer_styles["canvas"]["bg_color"] = hex_color
                self.canvas_bg_btn.setStyleSheet(
                    f"background-color: {hex_color}; border: 1px solid #ccc; border-radius: 6px;"
                )
            elif param_name == "connector_color":
                self.connector_style["connector_color"] = hex_color
                self.connector_color_btn.setStyleSheet(
                    f"background-color: {hex_color}; border: 1px solid #ccc; border-radius: 6px;"
                )
            else:
                self.layer_styles[self.current_layer][param_name] = hex_color
                if param_name == "bg_color":
                    self.bg_color_btn.setStyleSheet(
                        f"background-color: {hex_color}; border: 1px solid #ccc; border-radius: 6px;"
                    )
                elif param_name == "text_color":
                    self.text_color_btn.setStyleSheet(
                        f"background-color: {hex_color}; border: 1px solid #ccc; border-radius: 6px;"
                    )
                elif param_name == "border_color":
                    self.border_color_btn.setStyleSheet(
                        f"background-color: {hex_color}; border: 1px solid #ccc; border-radius: 6px;"
                    )

            self._update_preview()

    def _save_current_layer_style(self):
        """Save current UI state to layer style."""
        if self.current_layer == "canvas":
            return
        
        self.layer_styles[self.current_layer].update({
            "font_size": self.font_size_spin.value(),
            "padding_w": self.padding_w_spin.value(),
            "padding_h": self.padding_h_spin.value(),
            "radius": self.radius_spin.value(),
            "border_width": self.border_width_spin.value(),
            # Font style checkboxes
            "font_italic": self.font_italic_check.isChecked(),
            "font_underline": self.font_underline_check.isChecked(),
            "font_strikeout": self.font_strikeout_check.isChecked(),
        })

    def _load_current_layer_style(self):
        """Load style from current layer to UI."""
        if self.current_layer == "canvas":
            # Load canvas style
            bg_color = self.layer_styles["canvas"].get("bg_color", "#FFFFFF")
            self.canvas_bg_btn.setStyleSheet(
                f"background-color: {bg_color}; border: 1px solid #ccc; border-radius: 6px;"
            )
            return
        
        # Load node layer style
        style = self.layer_styles[self.current_layer]
        
        # Shape
        shape_map = {
            "rect": "Rectangle",
            "rounded_rect": "Rounded Rect",
            "circle": "Circle",
        }
        self.shape_combo.setText(shape_map.get(style.get("shape", "rounded_rect"), "Rounded Rect"))
        
        # Colors
        bg_color = style.get("bg_color", "#2196F3")
        text_color = style.get("text_color", "#FFFFFF")
        border_color = style.get("border_color", "#1976D2")
        
        self.bg_color_btn.setStyleSheet(
            f"background-color: {bg_color}; border: 1px solid #ccc; border-radius: 6px;"
        )
        self.text_color_btn.setStyleSheet(
            f"background-color: {text_color}; border: 1px solid #ccc; border-radius: 6px;"
        )
        self.border_color_btn.setStyleSheet(
            f"background-color: {border_color}; border: 1px solid #ccc; border-radius: 6px;"
        )
        
        # Font
        self.font_family_combo.setText(style.get("font_family", "Arial"))
        self.font_size_spin.setValue(style.get("font_size", 22))
        self.font_weight_combo.setText(style.get("font_weight", "Bold"))
        
        # Font style checkboxes
        self.font_italic_check.setChecked(style.get("font_italic", False))
        self.font_underline_check.setChecked(style.get("font_underline", False))
        self.font_strikeout_check.setChecked(style.get("font_strikeout", False))
        
        # Padding and radius
        self.padding_w_spin.setValue(style.get("padding_w", 20))
        self.padding_h_spin.setValue(style.get("padding_h", 16))
        self.radius_spin.setValue(style.get("radius", 10))
        
        # Border
        border_style_map = {
            "solid": "Solid",
            "dashed": "Dashed",
            "dotted": "Dotted",
            "dash_dot": "Dash-Dot",
        }
        self.border_style_combo.setText(
            border_style_map.get(style.get("border_style", "solid"), "Solid")
        )
        self.border_width_spin.setValue(style.get("border_width", 2))
        
        # Connector style
        self.connector_color_btn.setStyleSheet(
            f"background-color: {self.connector_style.get('connector_color', '#666666')}; border: 1px solid #ccc; border-radius: 6px;"
        )
        connector_type_map = {
            "straight": "Straight",
            "orthogonal": "Orthogonal",
            "bezier": "Bezier",
        }
        self.connector_type_combo.setText(
            connector_type_map.get(self.connector_style.get("connector_type", "bezier"), "Bezier")
        )
        connector_style_map = {
            "solid": "Solid",
            "dashed": "Dashed",
            "dotted": "Dotted",
        }
        self.connector_style_combo.setText(
            connector_style_map.get(self.connector_style.get("connector_style", "solid"), "Solid")
        )
        
        # Connector width: reverse mapping from start_width
        start_width = self.connector_style.get("start_width", 6.0)
        is_straight = (self.connector_style.get("connector_type") == "straight")
        
        if is_straight:
            # For straight lines, UI value = start_width
            ui_width = int(start_width)
        else:
            # For tapered lines, UI value = start_width (end_width = start_width + 4)
            ui_width = int(start_width)
        
        # Clamp to valid range
        ui_width = max(1, min(10, ui_width))
        self.connector_width_spin.setValue(ui_width)

    def _update_preview(self):
        """Update preview by applying styles to the mind map."""
        self._save_current_layer_style()
        
        # Notify parent window to apply styles
        parent = self.parent()
        if parent and hasattr(parent, 'mindmap_view'):
            from typing import TYPE_CHECKING
            if TYPE_CHECKING:
                from main import MainWindow
            main_window = parent  # type: ignore
            mindmap_view = main_window.mindmap_view  # type: ignore
            
            # Apply canvas background color
            if "canvas" in self.layer_styles:
                canvas_bg = self.layer_styles["canvas"].get("bg_color", "#FFFFFF")
                print(f"[DEBUG] Applying canvas bg: {canvas_bg}")
                from PySide6.QtGui import QBrush, QColor
                color = QColor(canvas_bg)
                print(f"[DEBUG] QColor valid: {color.isValid()}, alpha: {color.alpha()}")
                mindmap_view.scene.setBackgroundBrush(QBrush(color))
                print(f"[DEBUG] Background brush applied")
            
            # TODO: Apply node styles and trigger layout refresh
            # This requires integrating with MindMapService
            print(f"Style updated for {self.current_layer}")
