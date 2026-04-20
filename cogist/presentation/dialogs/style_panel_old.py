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
    QGridLayout,
    QGroupBox,
    QLabel,
    QMenu,
    QPushButton,
    QScrollArea,
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

        # Load UI with current layer styles (without triggering preview)
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
                text-align: left;
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
                text-align: left;
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

        # Corner radius (right after shape)
        radius_label = QLabel("Radius:")
        radius_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        radius_label.setMinimumWidth(label_width)
        node_grid.addWidget(radius_label, 1, 0)
        self.radius_spin = QSpinBox()
        self.radius_spin.setFixedHeight(widget_height)
        self.radius_spin.setRange(0, 30)
        self.radius_spin.setValue(10)
        self.radius_spin.setAlignment(Qt.AlignLeft)
        self.radius_spin.valueChanged.connect(self._update_preview)
        node_grid.addWidget(self.radius_spin, 1, 1)

        # Background color
        bg_label = QLabel("Background:")
        bg_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        bg_label.setMinimumWidth(label_width)
        node_grid.addWidget(bg_label, 2, 0)
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setFixedHeight(widget_height)
        self.bg_color_btn.setStyleSheet(
            "background-color: #2196F3; border: 1px solid #ccc; border-radius: 6px;"
        )
        self.bg_color_btn.clicked.connect(lambda: self._pick_color("bg_color"))
        node_grid.addWidget(self.bg_color_btn, 2, 1)

        # Text color
        text_label = QLabel("Text Color:")
        text_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        text_label.setMinimumWidth(label_width)
        node_grid.addWidget(text_label, 3, 0)
        self.text_color_btn = QPushButton()
        self.text_color_btn.setFixedHeight(widget_height)
        self.text_color_btn.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid #ccc; border-radius: 6px;"
        )
        self.text_color_btn.clicked.connect(lambda: self._pick_color("text_color"))
        node_grid.addWidget(self.text_color_btn, 3, 1)

        # Padding (right after text color)
        padding_w_label = QLabel("Padding W:")
        padding_w_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        padding_w_label.setMinimumWidth(label_width)
        node_grid.addWidget(padding_w_label, 4, 0)
        self.padding_w_spin = QSpinBox()
        self.padding_w_spin.setFixedHeight(widget_height)
        self.padding_w_spin.setRange(0, 50)
        self.padding_w_spin.setValue(20)
        self.padding_w_spin.setAlignment(Qt.AlignLeft)
        self.padding_w_spin.valueChanged.connect(self._update_preview)
        node_grid.addWidget(self.padding_w_spin, 4, 1)

        padding_h_label = QLabel("Padding H:")
        padding_h_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        padding_h_label.setMinimumWidth(label_width)
        node_grid.addWidget(padding_h_label, 5, 0)
        self.padding_h_spin = QSpinBox()
        self.padding_h_spin.setFixedHeight(widget_height)
        self.padding_h_spin.setRange(0, 50)
        self.padding_h_spin.setValue(16)
        self.padding_h_spin.setAlignment(Qt.AlignLeft)
        self.padding_h_spin.valueChanged.connect(self._update_preview)
        node_grid.addWidget(self.padding_h_spin, 5, 1)

        # Font family
        font_family_label = QLabel("Font:")
        font_family_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        font_family_label.setMinimumWidth(label_width)
        node_grid.addWidget(font_family_label, 6, 0)
        self.font_family_combo = QPushButton(self._get_localized_font_name("Arial"))
        self.font_family_combo.setFixedHeight(widget_height)
        self.font_family_combo.setStyleSheet("""
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
        """)
        # Directly open font dialog on click
        self.font_family_combo.clicked.connect(self._show_font_menu)
        node_grid.addWidget(self.font_family_combo, 6, 1)

        # Font size
        font_size_label = QLabel("Font Size:")
        font_size_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        font_size_label.setMinimumWidth(label_width)
        node_grid.addWidget(font_size_label, 7, 0)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setFixedHeight(widget_height)
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.setValue(22)
        self.font_size_spin.setAlignment(Qt.AlignLeft)
        self.font_size_spin.valueChanged.connect(self._update_preview)
        node_grid.addWidget(self.font_size_spin, 7, 1)

        # Font weight
        font_weight_label = QLabel("Weight:")
        font_weight_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        font_weight_label.setMinimumWidth(label_width)
        node_grid.addWidget(font_weight_label, 8, 0)
        self.font_weight_combo = QPushButton("Bold")
        self.font_weight_combo.setFixedHeight(widget_height)
        self.font_weight_combo.setStyleSheet("""
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
        node_grid.addWidget(self.font_weight_combo, 8, 1)

        # Font style checkboxes (Italic, Underline, Strikeout)
        font_style_label = QLabel("Font Style:")
        font_style_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        font_style_label.setMinimumWidth(label_width)
        node_grid.addWidget(font_style_label, 9, 0)

        # Create a vertical layout for the three checkboxes
        style_layout = QVBoxLayout()
        style_layout.setSpacing(4)
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
        node_grid.addWidget(style_container, 9, 1)

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
                text-align: left;
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
        self.border_width_spin.setAlignment(Qt.AlignLeft)
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
                text-align: left;
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
                text-align: left;
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
        self.connector_width_spin.setAlignment(Qt.AlignLeft)
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

        # Show/hide radius control based on shape
        is_rounded = (value == "Rounded Rect")
        self.radius_spin.setVisible(is_rounded)
        # Also hide/show the radius label (find it in the grid)
        layout = self.node_style_group.layout()
        if layout:
            for i in range(layout.rowCount()):
                item = layout.itemAtPosition(i, 0)
                if item and isinstance(item.widget(), QLabel) and item.widget().text() == "Radius:":
                    item.widget().setVisible(is_rounded)
                    break

        self._update_preview()

    def _get_localized_font_name(self, font_family: str) -> str:
        """Get localized font name for display.

        Uses platform-specific APIs to get the localized font name:
        - macOS: Core Text via PyObjC
        - Windows: ctypes with GDI
        - Linux: fontconfig
        Falls back to English name if localized name not available.
        """
        import platform
        system = platform.system()

        try:
            if system == "Darwin":  # macOS
                # Try to use Core Text via PyObjC
                try:
                    from CoreText import (  # type: ignore
                        CTFontCopyDisplayName,
                        CTFontCreateWithName,
                    )

                    print(f"DEBUG: Trying to get localized name for: {font_family}")

                    # Create a CTFontRef
                    ct_font = CTFontCreateWithName(font_family, 12.0, None)
                    if ct_font:
                        # Get display name (localized)
                        display_name = CTFontCopyDisplayName(ct_font)
                        if display_name:
                            result = str(display_name)
                            print(f"DEBUG: Display name: {result}")
                            return result
                        else:
                            print("DEBUG: No display name found")
                    else:
                        print("DEBUG: Failed to create CTFont")
                except ImportError as e:
                    print(f"DEBUG: PyObjC not available: {e}")
                except Exception as e:
                    print(f"DEBUG: Error getting localized name: {e}")

            elif system == "Windows":
                # Try to use ctypes with GDI
                try:
                    import ctypes
                    from ctypes import wintypes

                    # Load gdi32
                    gdi32 = ctypes.windll.gdi32

                    # Create DC
                    hdc = gdi32.CreateDCW("DISPLAY", None, None, None)

                    # Create LOGFONT structure
                    class LOGFONTW(ctypes.Structure):
                        _fields_ = [
                            ("lfHeight", wintypes.LONG),
                            ("lfWidth", wintypes.LONG),
                            ("lfEscapement", wintypes.LONG),
                            ("lfOrientation", wintypes.LONG),
                            ("lfWeight", wintypes.LONG),
                            ("lfItalic", wintypes.BYTE),
                            ("lfUnderline", wintypes.BYTE),
                            ("lfStrikeOut", wintypes.BYTE),
                            ("lfCharSet", wintypes.BYTE),
                            ("lfOutPrecision", wintypes.BYTE),
                            ("lfClipPrecision", wintypes.BYTE),
                            ("lfQuality", wintypes.BYTE),
                            ("lfPitchAndFamily", wintypes.BYTE),
                            ("lfFaceName", wintypes.WCHAR * 32),
                        ]

                    logfont = LOGFONTW()
                    logfont.lfHeight = 0
                    logfont.lfFaceName = font_family

                    # Create font
                    hfont = gdi32.CreateFontIndirectW(ctypes.byref(logfont))

                    # Select font into DC
                    old_font = gdi32.SelectObject(hdc, hfont)

                    # Get font name (this is simplified, full implementation would be more complex)
                    # For now, just return the family name as-is
                    gdi32.SelectObject(hdc, old_font)
                    gdi32.DeleteObject(hfont)
                    gdi32.DeleteDC(hdc)

                except Exception:
                    pass  # Fall through to default

            elif system == "Linux":
                # Try to use fontconfig
                try:
                    import subprocess
                    result = subprocess.run(
                        ["fc-match", "-f", "%{family}", font_family],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        return result.stdout.strip()
                except Exception:
                    pass  # Fall through to default

        except Exception as e:
            print(f"DEBUG: Unexpected error: {e}")

        # Fallback: return the original font family name
        return font_family

    def _show_font_menu(self):
        """Show font family selection dialog with localized names."""
        from PySide6.QtGui import QFont, QFontDatabase
        from PySide6.QtWidgets import (
            QDialog,
            QListWidget,
            QVBoxLayout,
        )

        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Font")
        dialog.setFixedSize(350, 450)

        # Layout
        layout = QVBoxLayout(dialog)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Font list
        font_list = QListWidget()
        font_list.setFont(QFont("Arial", 15))
        layout.addWidget(font_list)

        # Get all available fonts
        font_db = QFontDatabase()
        families = font_db.families()

        # Filter out bitmap/system fonts that cause warnings
        filtered_families = []
        for family in families:
            # Skip bitmap fonts and system fonts
            if any(keyword in family.lower() for keyword in ['bitmap', 'dingbats', 'symbol', 'icon']):
                continue
            # Skip if font has no styles
            if not font_db.styles(family):
                continue
            filtered_families.append(family)

        families = filtered_families

        # Deduplicate fonts by base name (remove duplicates like "Times New Roman", "Times New Roman Bold", etc.)
        seen_names = set()
        unique_families = []
        for family in families:
            # Normalize: remove common suffixes to get base font name
            base_name = family.split('(')[0].strip()  # Remove parenthetical info
            # Check if we've seen a similar name
            is_duplicate = False
            for seen in seen_names:
                # If one contains the other, they're likely variants of the same font
                if base_name.lower() in seen.lower() or seen.lower() in base_name.lower():
                    is_duplicate = True
                    break
            if not is_duplicate:
                seen_names.add(base_name)
                unique_families.append(family)

        families = unique_families

        current_family = self.layer_styles[self.current_layer].get("font_family", "Arial")

        # Build font list with localized names
        font_name_map = {}  # Maps display name -> actual font family

        for family in families:
            # Get localized name
            localized_name = self._get_localized_font_name(family)
            font_name_map[localized_name] = family

            from PySide6.QtWidgets import QListWidgetItem
            item = QListWidgetItem(localized_name)
            item.setFont(QFont(family))  # Use actual font for rendering
            font_list.addItem(item)

            if family == current_family:
                font_list.setCurrentItem(item)

        # Double-click to select
        def on_item_double_clicked(item):
            display_name = item.text()
            actual_family = font_name_map.get(display_name, display_name)
            self._set_font_family(actual_family)
            dialog.accept()

        font_list.itemDoubleClicked.connect(on_item_double_clicked)

        # Position dialog near the font button
        # Dialog's right edge aligns with button's left edge
        button_pos = self.font_family_combo.mapToGlobal(self.font_family_combo.rect().topLeft())
        dialog_x = button_pos.x() - dialog.width() - 10  # 10px gap
        dialog_y = button_pos.y() - 48  # Move up ~1.5 button heights
        dialog.move(dialog_x, dialog_y)

        # Click outside to close
        dialog.setMouseTracking(True)
        def on_mouse_press(event):
            if event.button() == Qt.LeftButton:
                dialog.reject()
        dialog.mousePressEvent = on_mouse_press

        # ESC to close
        dialog.keyPressEvent = lambda event: dialog.reject() if event.key() == Qt.Key_Escape else QDialog.keyPressEvent(dialog, event)

        # Show dialog
        dialog.exec()

    def _set_font_family(self, family):
        """Set font family and update preview."""
        self.layer_styles[self.current_layer]["font_family"] = family
        self.font_family_combo.setText(self._get_localized_font_name(family))

        # Update font weight options based on selected font
        self._update_font_weight_options(family)

        self._update_preview()

    def _update_font_weight_options(self, font_family: str):
        """Update font weight menu based on available weights for the font.

        Args:
            font_family: The font family name to query
        """
        from PySide6.QtGui import QFontDatabase

        font_db = QFontDatabase()
        styles = font_db.styles(font_family)

        if not styles:
            # Fallback to default weights if no styles found
            styles = ["Light", "Normal", "Bold", "ExtraBold"]

        # Filter out italic/oblique styles - these are not weights
        weight_styles = [s for s in styles if "italic" not in s.lower() and "oblique" not in s.lower()]

        # Define logical order for common weight names
        weight_priority = {
            "Thin": 0,
            "Hairline": 1,
            "Extra Light": 2,
            "ExtraLight": 2,
            "Ultra Light": 2,
            "UltraLight": 2,
            "Light": 3,
            "Regular": 4,
            "Normal": 4,
            "Medium": 5,
            "Semi Bold": 6,
            "SemiBold": 6,
            "Demi Bold": 6,
            "DemiBold": 6,
            "Bold": 7,
            "Extra Bold": 8,
            "ExtraBold": 8,
            "Ultra Bold": 8,
            "UltraBold": 8,
            "Black": 9,
            "Heavy": 9,
        }

        # Sort styles by weight priority
        sorted_styles = sorted(
            weight_styles,
            key=lambda s: weight_priority.get(s, 100)
        )

        # Rebuild the menu with all available styles
        self.font_weight_menu.clear()
        for style in sorted_styles:
            action = self.font_weight_menu.addAction(style)
            action.triggered.connect(lambda _, opt=style: self._set_font_weight(opt))

        # Update current selection if it's still valid
        current_weight = self.layer_styles[self.current_layer].get("font_weight", "Normal")
        if current_weight not in sorted_styles:
            # Select first available weight or closest match
            current_weight = sorted_styles[0] if sorted_styles else "Normal"
            self.layer_styles[self.current_layer]["font_weight"] = current_weight

        self.font_weight_combo.setText(current_weight)
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

        For tapered lines (bezier/orthogonal): start_width = value, end_width = value - 4
        For straight lines: start_width = end_width = value
        """
        is_straight = (self.connector_style.get("connector_type") == "straight")

        if is_straight:
            # Equal width for straight lines
            self.connector_style["start_width"] = float(value)
            self.connector_style["end_width"] = float(value)
        else:
            # Tapered width for bezier/orthogonal: thick at source (parent), thin at target (child)
            self.connector_style["start_width"] = float(value)
            self.connector_style["end_width"] = max(1.0, float(value - 4))

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
        # Block signals on all widgets that trigger preview updates
        widgets_to_block = [
            self.radius_spin,
            self.font_size_spin,
            self.padding_w_spin,
            self.padding_h_spin,
            self.border_width_spin,
            self.connector_width_spin,
            self.font_italic_check,
            self.font_underline_check,
            self.font_strikeout_check,
        ]

        # Save old signal states
        old_states = [w.blockSignals(True) for w in widgets_to_block]

        try:
            if self.current_layer == "canvas":
                # Load canvas style
                bg_color = self.layer_styles["canvas"].get("bg_color", "#FFFFFF")
                self.canvas_bg_btn.setStyleSheet(
                    f"background-color: {bg_color}; border: 1px solid #ccc; border-radius: 6px;"
                )
            else:
                # Load node layer style
                style = self.layer_styles[self.current_layer]

                # Shape
                shape_map = {
                    "rect": "Rectangle",
                    "rounded_rect": "Rounded Rect",
                    "circle": "Circle",
                }
                current_shape = shape_map.get(style.get("shape", "rounded_rect"), "Rounded Rect")
                self.shape_combo.setText(current_shape)

                # Show/hide radius control based on shape
                is_rounded = (current_shape == "Rounded Rect")
                self.radius_spin.setVisible(is_rounded)
                # Also hide/show the radius label
                layout = self.node_style_group.layout()
                if layout:
                    for i in range(layout.rowCount()):
                        item = layout.itemAtPosition(i, 0)
                        if item and isinstance(item.widget(), QLabel) and item.widget().text() == "Radius:":
                            item.widget().setVisible(is_rounded)
                            break

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
                font_family = style.get("font_family", "Arial")
                self.font_family_combo.setText(self._get_localized_font_name(font_family))
                self.font_size_spin.setValue(style.get("font_size", 22))

                # Update font weight options based on current font
                self._update_font_weight_options(font_family)
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
                ui_width = int(start_width)

                # Clamp to valid range
                ui_width = max(1, min(10, ui_width))
                self.connector_width_spin.setValue(ui_width)
        finally:
            # Restore signal states
            for widget, old_state in zip(widgets_to_block, old_states, strict=False):
                widget.blockSignals(old_state)

    def _update_preview(self):
        """Update preview by applying styles to the mind map."""
        self._save_current_layer_style()

        # Use global app context to get mindmap view
        from cogist.application.services import get_app_context
        app_context = get_app_context()
        mindmap_view = app_context.get_mindmap_view()

        if not mindmap_view:
            return

        # Apply canvas background color
        if "canvas" in self.layer_styles:
            canvas_bg = self.layer_styles["canvas"].get("bg_color", "#FFFFFF")
            from PySide6.QtGui import QBrush, QColor
            mindmap_view.scene.setBackgroundBrush(QBrush(QColor(canvas_bg)))

        # Apply node styles - convert layer_styles to MindMapStyle format
        self._apply_node_styles_to_mindmap(mindmap_view)

        # Apply connector (edge) styles
        self._apply_connector_styles_to_mindmap(mindmap_view)

    def _apply_node_styles_to_mindmap(self, mindmap_view):
        """Apply node layer styles to the mind map view.

        This updates the style_config and triggers re-layout.
        """
        from cogist.domain.styles import (
            ColorScheme,
            MindMapStyle,
            NodeRole,
            SpacingConfig,
            SpacingLevel,
            Template,
        )

        # Create a new style config based on current layer styles
        style = MindMapStyle()

        # For now, we'll create a simple template from the layer styles
        # In the future, this should select from predefined templates

        # Convert layer styles to role-based styles
        root_data = self.layer_styles.get("root", {})
        level1_data = self.layer_styles.get("level_1", {})
        level2_data = self.layer_styles.get("level_2", {})
        level3_data = self.layer_styles.get("level_3_plus", {})

        # Create role-based styles (without colors - colors come from color scheme)
        role_styles = {
            NodeRole.ROOT: self._convert_layer_to_role_style(root_data),
            NodeRole.PRIMARY: self._convert_layer_to_role_style(level1_data),
            NodeRole.SECONDARY: self._convert_layer_to_role_style(level2_data),
            NodeRole.TERTIARY: self._convert_layer_to_role_style(level3_data),
        }

        # Create a temporary template
        template = Template(
            name="Custom",
            description="Custom template from style panel",
            role_styles=role_styles,
            spacing=SpacingConfig(
                parent_child_spacing=SpacingLevel.NORMAL,
                sibling_spacing=SpacingLevel.NORMAL,
            ),
        )

        # Create a color scheme from layer styles
        node_colors = {
            NodeRole.ROOT: root_data.get("bg_color", "#2196F3"),
            NodeRole.PRIMARY: level1_data.get("bg_color", "#4CAF50"),
            NodeRole.SECONDARY: level2_data.get("bg_color", "#FF9800"),
            NodeRole.TERTIARY: level3_data.get("bg_color", "#9E9E9E"),
        }

        text_colors = {}
        if root_data.get("text_color"):
            text_colors[NodeRole.ROOT] = root_data["text_color"]
        if level1_data.get("text_color"):
            text_colors[NodeRole.PRIMARY] = level1_data["text_color"]
        if level2_data.get("text_color"):
            text_colors[NodeRole.SECONDARY] = level2_data["text_color"]
        if level3_data.get("text_color"):
            text_colors[NodeRole.TERTIARY] = level3_data["text_color"]

        color_scheme = ColorScheme(
            name="Custom",
            description="Custom color scheme from style panel",
            node_colors=node_colors,
            text_colors=text_colors if text_colors else None,
        )

        # Set template and color scheme names
        style.template_name = "custom"
        style.color_scheme_name = "custom"

        # Store resolved references directly (since we don't have a registry yet)
        style.resolved_template = template
        style.resolved_color_scheme = color_scheme

        # Update canvas background color
        if "canvas" in self.layer_styles:
            style.canvas_bg_color = self.layer_styles["canvas"].get("bg_color", "#FFFFFF")
            color_scheme.canvas_bg_color = style.canvas_bg_color

        # Update connector (edge) styles from panel's connector_style
        # Note: EdgeConfig structure is different now, need to update accordingly
        # For now, keep simple edge color
        style.edge.default_style.line_width = self.connector_style.get("start_width", 2.0)

        # TODO: Update edge color in color scheme
        # style.edge_color = self.connector_style.get("connector_color", "#666666")

        # Update mindmap view's style config
        mindmap_view.style_config = style

        # Update all existing node items with new style
        if hasattr(mindmap_view, 'node_items'):
            for _node_id, node_item in mindmap_view.node_items.items():
                if hasattr(node_item, 'update_style'):
                    node_item.update_style(style)

        # Trigger re-layout by calling refresh_layout
        # This will re-measure nodes with new styles and reposition them
        if hasattr(mindmap_view, '_refresh_layout'):
            mindmap_view._refresh_layout()

    def _apply_connector_styles_to_mindmap(self, mindmap_view):
        """Apply connector (edge) styles to all edges in the mind map."""
        # Get edge items from mindmap view
        if not hasattr(mindmap_view, 'edge_items'):
            return

        # Update all edge items with current connector style
        for edge_item in mindmap_view.edge_items:
            if hasattr(edge_item, 'update_style'):
                edge_item.update_style(self.connector_style)

    def _convert_layer_to_role_style(self, layer_data: dict):
        """Convert layer style dictionary to RoleBasedStyle object (without colors)."""
        from cogist.domain.styles import (
            BackgroundStyle,
            BorderStyle,
            NodeRole,
            NodeShape,
            RoleBasedStyle,
        )

        # Determine role from context (we'll set it later)
        # For now, use a placeholder
        role = NodeRole.TERTIARY

        return RoleBasedStyle(
            role=role,
            shape=NodeShape(
                shape_type="basic",
                basic_shape=layer_data.get("shape", "rounded_rect"),
                border_radius=layer_data.get("radius", 8),
            ),
            background=BackgroundStyle(
                bg_type="solid",
            ),
            border=BorderStyle(
                border_type="simple",
                border_width=layer_data.get("border_width", 2),
                border_radius=layer_data.get("radius", 8),
                border_style=layer_data.get("border_style", "solid").lower(),
            ),
            padding_w=layer_data.get("padding_w", 12),
            padding_h=layer_data.get("padding_h", 8),
            font_size=layer_data.get("font_size", 14),
            font_weight=layer_data.get("font_weight", "Normal"),
            font_style="Italic" if layer_data.get("font_italic", False) else "Normal",
            font_family=layer_data.get("font_family", "Arial"),
        )

    def _convert_layer_to_node_style(self, layer_data: dict):
        """Convert layer style dictionary to NodeStyleConfig object.

        DEPRECATED: This method is kept for backward compatibility only.
        Use _convert_layer_to_role_style instead.
        """
        from cogist.domain.styles import NodeStyleConfig

        return NodeStyleConfig(
            shape=layer_data.get("shape", "rounded_rect"),
            bg_color=layer_data.get("bg_color"),
            text_color=layer_data.get("text_color"),
            border_color=layer_data.get("border_color"),
            font_family=layer_data.get("font_family", "Arial"),
            font_size=layer_data.get("font_size", 16),
            font_weight=layer_data.get("font_weight", "Normal"),
            font_italic=layer_data.get("font_italic", False),
            font_underline=layer_data.get("font_underline", False),
            font_strikeout=layer_data.get("font_strikeout", False),
            padding_width=layer_data.get("padding_w", 10),
            padding_height=layer_data.get("padding_h", 8),
            border_radius=layer_data.get("radius", 8),
            border_style=layer_data.get("border_style", "solid").lower(),
            border_width=layer_data.get("border_width", 2),
        )
