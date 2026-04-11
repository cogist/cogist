"""
Style Panel - Development Tool

A dockable panel for real-time style debugging and template creation.
Allows developers to tweak style parameters and see immediate results.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
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
    """Panel for debugging and testing node styles."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set initial width
        self.setMinimumWidth(250)
        self.setMaximumWidth(375)

        # Create main widget
        self.main_widget = QWidget()

        # Store current style parameters
        self.current_depth = 0
        self.style_params = {}

        # Apply custom styles
        self._apply_styles()

        self._init_ui()
        self._load_default_style()

    def _apply_styles(self):
        """Apply custom QSS styles to the panel."""
        # Set main widget background
        self.setStyleSheet("""
            /* Use class selector to avoid affecting child widgets */
            StylePanel {
                background-color: #F5F5F5;
            }
            /* Group box styling */
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
                background-color: #F5F5F5;
                font-weight: bold;
                font-size: 13px;
            }
            /* Use specific selectors instead of global QPushButton/QSpinBox */
            QGroupBox QPushButton,
            QGroupBox QSpinBox,
            QGroupBox QComboBox,
            QGroupBox QLineEdit {
                border: 1px solid #C8C8C8;
                border-radius: 6px;
                background-color: #FFFFFF;
            }
            QGroupBox QPushButton:hover,
            QGroupBox QSpinBox:hover,
            QGroupBox QComboBox:hover,
            QGroupBox QLineEdit:hover {
                border-color: #A0A0A0;
            }
            /* Remove background from labels */
            QLabel {
                background-color: transparent;
            }
            /* Exclude color picker buttons from general style */
            QPushButton#bg_color_btn, QPushButton#text_color_btn, QPushButton#edge_color_btn {
                border: 1px solid #C8C8C8;
            }
        """)

    def _init_ui(self):
        """Initialize the user interface."""
        # Create scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # Use system default scrollbar style (no custom QSS)

        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(10)

        # Fixed label width for all forms to align colons
        label_width = 90
        widget_height = 32  # Fixed height for all input widgets
        # Widgets will use layout to determine width automatically

        # Depth selector
        depth_group = QGroupBox("Layer Selection")
        depth_group.setFlat(False)
        depth_group.setStyleSheet("""
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
                background-color: #F5F5F5;
                font-weight: bold;
                font-size: 13px;
            }
            QGroupBox QLabel {
                background-color: transparent;
            }
        """)
        depth_grid = QGridLayout()
        depth_grid.setSpacing(6)
        depth_grid.setContentsMargins(10, 16, 10, 16)
        depth_grid.setColumnStretch(0, 0)  # Label column takes needed space
        depth_grid.setColumnStretch(1, 1)  # Widget column takes remaining space
        depth_label = QLabel("Depth:")
        depth_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        depth_label.setMinimumWidth(label_width)
        depth_grid.addWidget(depth_label, 0, 0)

        # Use QPushButton + QMenu for macOS compatibility
        self.depth_combo = QPushButton("Root (0)")
        self.depth_combo.setFixedHeight(widget_height)
        self.depth_combo.setStyleSheet("""
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
            QPushButton:pressed {
                background-color: #E0E0E0;
            }
            QPushButton::menu-indicator {
                subcontrol-position: center right;
                right: 8px;
                width: 8px;
                height: 8px;
            }
        """)
        self.depth_menu = QMenu()
        self.depth_menu.aboutToShow.connect(
            lambda: self._adjust_menu_width(self.depth_menu, self.depth_combo)
        )
        depth_options = [
            "Root (0)",
            "Level 1",
            "Level 2",
            "Level 3+",
            "Individual Node",
        ]
        for option in depth_options:
            action = self.depth_menu.addAction(option)
            action.triggered.connect(lambda _, opt=option: self._set_depth(opt))
        self.depth_combo.setMenu(self.depth_menu)
        depth_grid.addWidget(self.depth_combo, 0, 1)
        depth_group.setLayout(depth_grid)
        layout.addWidget(depth_group)

        # Importance selector (only visible when "Individual Node" is selected)
        self.importance_group = QGroupBox("Importance Level")
        self.importance_group.setVisible(False)  # Hidden by default
        importance_grid = QGridLayout()
        importance_grid.setSpacing(6)
        importance_grid.setContentsMargins(10, 16, 10, 16)
        importance_grid.setColumnStretch(0, 0)
        importance_grid.setColumnStretch(1, 1)

        imp_label = QLabel("Level:")
        imp_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        imp_label.setMinimumWidth(label_width)
        importance_grid.addWidget(imp_label, 0, 0)

        self.importance_combo = QPushButton("Normal")
        self.importance_combo.setFixedHeight(widget_height)
        self.importance_combo.setStyleSheet("""
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
            QPushButton:pressed {
                background-color: #E0E0E0;
            }
            QPushButton::menu-indicator {
                subcontrol-position: center right;
                right: 8px;
                width: 8px;
                height: 8px;
            }
        """)
        self.importance_menu = QMenu()
        self.importance_menu.aboutToShow.connect(
            lambda: self._adjust_menu_width(self.importance_menu, self.importance_combo)
        )
        importance_options = ["Important", "Normal", "Unimportant"]
        for option in importance_options:
            action = self.importance_menu.addAction(option)
            action.triggered.connect(lambda _, opt=option: self._set_importance(opt))
        self.importance_combo.setMenu(self.importance_menu)
        importance_grid.addWidget(self.importance_combo, 0, 1)

        self.importance_group.setLayout(importance_grid)
        layout.addWidget(self.importance_group)

        # Node style group
        node_group = QGroupBox("Node Style")
        node_group.setFlat(False)
        node_group.setStyleSheet("""
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
                background-color: #F5F5F5;
                font-weight: bold;
                font-size: 13px;
            }
            QGroupBox QLabel {
                background-color: transparent;
            }
        """)
        node_grid = QGridLayout()
        node_grid.setSpacing(6)
        node_grid.setContentsMargins(10, 16, 10, 16)
        node_grid.setColumnStretch(0, 0)  # Label column takes needed space
        node_grid.setColumnStretch(1, 1)  # Widget column takes remaining space

        # Background color
        bg_label = QLabel("Background:")
        bg_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        bg_label.setMinimumWidth(label_width)
        node_grid.addWidget(bg_label, 0, 0)
        self.bg_color_btn = QPushButton()
        self.bg_color_btn.setFixedHeight(widget_height)
        self.bg_color_btn.setStyleSheet(
            "background-color: #2196F3; border: 1px solid #ccc; border-radius: 6px;"
        )
        self.bg_color_btn.clicked.connect(lambda: self._pick_color("bg_color"))
        node_grid.addWidget(self.bg_color_btn, 0, 1)

        # Text color
        text_label = QLabel("Text:")
        text_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        text_label.setMinimumWidth(label_width)
        node_grid.addWidget(text_label, 1, 0)
        self.text_color_btn = QPushButton()
        self.text_color_btn.setFixedHeight(widget_height)
        self.text_color_btn.setStyleSheet(
            "background-color: #FFFFFF; border: 1px solid #ccc; border-radius: 6px;"
        )
        self.text_color_btn.clicked.connect(lambda: self._pick_color("text_color"))
        node_grid.addWidget(self.text_color_btn, 1, 1)

        # Font size
        font_size_label = QLabel("Font Size:")
        font_size_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        font_size_label.setMinimumWidth(label_width)
        node_grid.addWidget(font_size_label, 2, 0)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setFixedHeight(widget_height)
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.setValue(22)
        self.font_size_spin.setAlignment(Qt.AlignCenter)
        self.font_size_spin.setStyleSheet("""
            QSpinBox {
                background-color: #FFFFFF;
                border: 1px solid #C8C8C8;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 13px;
            }
            QSpinBox:hover {
                border-color: #A0A0A0;
            }
            QSpinBox:focus {
                border-color: #2196F3;
            }
        """)
        self.font_size_spin.valueChanged.connect(self._update_preview)
        node_grid.addWidget(self.font_size_spin, 2, 1)

        # Font weight
        font_weight_label = QLabel("Font Weight:")
        font_weight_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        font_weight_label.setMinimumWidth(label_width)
        node_grid.addWidget(font_weight_label, 3, 0)

        # Use QPushButton + QMenu for macOS compatibility
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
            QPushButton:pressed {
                background-color: #E0E0E0;
            }
            QPushButton::menu-indicator {
                subcontrol-position: center right;
                right: 8px;
                width: 8px;
                height: 8px;
            }
        """)
        self.font_weight_menu = QMenu()
        self.font_weight_menu.aboutToShow.connect(
            lambda: self._adjust_menu_width(
                self.font_weight_menu, self.font_weight_combo
            )
        )
        weight_options = ["Normal", "Bold"]
        for option in weight_options:
            action = self.font_weight_menu.addAction(option)
            action.triggered.connect(lambda _, opt=option: self._set_font_weight(opt))
        self.font_weight_combo.setMenu(self.font_weight_menu)
        node_grid.addWidget(self.font_weight_combo, 3, 1)

        # Padding width
        padding_w_label = QLabel("Padding W:")
        padding_w_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        padding_w_label.setMinimumWidth(label_width)
        node_grid.addWidget(padding_w_label, 4, 0)
        self.padding_w_spin = QSpinBox()
        self.padding_w_spin.setFixedHeight(widget_height)
        self.padding_w_spin.setRange(0, 50)
        self.padding_w_spin.setValue(20)
        self.padding_w_spin.setAlignment(Qt.AlignCenter)
        self.padding_w_spin.setStyleSheet("""
            QSpinBox {
                background-color: #FFFFFF;
                border: 1px solid #C8C8C8;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 13px;
            }
            QSpinBox:hover {
                border-color: #A0A0A0;
            }
            QSpinBox:focus {
                border-color: #2196F3;
            }
        """)
        self.padding_w_spin.valueChanged.connect(self._update_preview)
        node_grid.addWidget(self.padding_w_spin, 4, 1)

        # Padding height
        padding_h_label = QLabel("Padding H:")
        padding_h_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        padding_h_label.setMinimumWidth(label_width)
        node_grid.addWidget(padding_h_label, 5, 0)
        self.padding_h_spin = QSpinBox()
        self.padding_h_spin.setFixedHeight(widget_height)
        self.padding_h_spin.setRange(0, 50)
        self.padding_h_spin.setValue(16)
        self.padding_h_spin.setAlignment(Qt.AlignCenter)
        self.padding_h_spin.setStyleSheet("""
            QSpinBox {
                background-color: #FFFFFF;
                border: 1px solid #C8C8C8;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 13px;
            }
            QSpinBox:hover {
                border-color: #A0A0A0;
            }
            QSpinBox:focus {
                border-color: #2196F3;
            }
        """)
        self.padding_h_spin.valueChanged.connect(self._update_preview)
        node_grid.addWidget(self.padding_h_spin, 5, 1)

        # Border radius
        radius_label = QLabel("Border Radius:")
        radius_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        radius_label.setMinimumWidth(label_width)
        node_grid.addWidget(radius_label, 6, 0)
        self.radius_spin = QSpinBox()
        self.radius_spin.setFixedHeight(widget_height)
        self.radius_spin.setRange(0, 30)
        self.radius_spin.setValue(10)
        self.radius_spin.setAlignment(Qt.AlignCenter)
        self.radius_spin.setStyleSheet("""
            QSpinBox {
                background-color: #FFFFFF;
                border: 1px solid #C8C8C8;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 13px;
            }
            QSpinBox:hover {
                border-color: #A0A0A0;
            }
            QSpinBox:focus {
                border-color: #2196F3;
            }
        """)
        self.radius_spin.valueChanged.connect(self._update_preview)
        node_grid.addWidget(self.radius_spin, 6, 1)

        node_group.setLayout(node_grid)
        layout.addWidget(node_group)

        # Layout spacing group (only visible for depth levels, not for Individual Node)
        self.spacing_group = QGroupBox("Layout Spacing")
        self.spacing_group.setVisible(False)  # Hidden by default
        spacing_grid = QGridLayout()
        spacing_grid.setSpacing(6)
        spacing_grid.setContentsMargins(10, 16, 10, 16)
        spacing_grid.setColumnStretch(0, 0)
        spacing_grid.setColumnStretch(1, 1)

        # Horizontal spacing (level spacing)
        h_spacing_label = QLabel("Horizontal:")
        h_spacing_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        h_spacing_label.setMinimumWidth(label_width)
        spacing_grid.addWidget(h_spacing_label, 0, 0)
        self.h_spacing_spin = QSpinBox()
        self.h_spacing_spin.setFixedHeight(widget_height)
        self.h_spacing_spin.setRange(20, 200)
        self.h_spacing_spin.setValue(80)
        self.h_spacing_spin.setAlignment(Qt.AlignCenter)
        spacing_grid.addWidget(self.h_spacing_spin, 0, 1)

        # Vertical spacing (sibling spacing)
        v_spacing_label = QLabel("Vertical:")
        v_spacing_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        v_spacing_label.setMinimumWidth(label_width)
        spacing_grid.addWidget(v_spacing_label, 1, 0)
        self.v_spacing_spin = QSpinBox()
        self.v_spacing_spin.setFixedHeight(widget_height)
        self.v_spacing_spin.setRange(20, 200)
        self.v_spacing_spin.setValue(60)
        self.v_spacing_spin.setAlignment(Qt.AlignCenter)
        spacing_grid.addWidget(self.v_spacing_spin, 1, 1)

        self.spacing_group.setLayout(spacing_grid)
        layout.addWidget(self.spacing_group)

        # Edge style group
        edge_group = QGroupBox("Edge Style")
        edge_group.setFlat(False)
        edge_group.setStyleSheet("""
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
                background-color: #F5F5F5;
                font-weight: bold;
                font-size: 13px;
            }
            QGroupBox QLabel {
                background-color: transparent;
            }
        """)
        edge_grid = QGridLayout()
        edge_grid.setSpacing(6)
        edge_grid.setContentsMargins(10, 16, 10, 16)
        edge_grid.setColumnStretch(0, 0)  # Label column takes needed space
        edge_grid.setColumnStretch(1, 1)  # Widget column takes remaining space

        # Edge color
        edge_color_label = QLabel("Color:")
        edge_color_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        edge_color_label.setMinimumWidth(label_width)
        edge_grid.addWidget(edge_color_label, 0, 0)
        self.edge_color_btn = QPushButton()
        self.edge_color_btn.setFixedHeight(widget_height)
        self.edge_color_btn.setStyleSheet(
            "background-color: #2196F3; border: 1px solid #ccc; border-radius: 6px;"
        )
        self.edge_color_btn.clicked.connect(lambda: self._pick_color("edge_color"))
        edge_grid.addWidget(self.edge_color_btn, 0, 1)

        # Edge width
        edge_width_label = QLabel("Width:")
        edge_width_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        edge_width_label.setMinimumWidth(label_width)
        edge_grid.addWidget(edge_width_label, 1, 0)
        self.edge_width_spin = QSpinBox()
        self.edge_width_spin.setFixedHeight(widget_height)
        self.edge_width_spin.setRange(1, 10)
        self.edge_width_spin.setValue(3)
        self.edge_width_spin.setAlignment(Qt.AlignCenter)
        self.edge_width_spin.setStyleSheet("""
            QSpinBox {
                background-color: #FFFFFF;
                border: 1px solid #C8C8C8;
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 13px;
            }
            QSpinBox:hover {
                border-color: #A0A0A0;
            }
            QSpinBox:focus {
                border-color: #2196F3;
            }
        """)
        self.edge_width_spin.valueChanged.connect(self._update_preview)
        edge_grid.addWidget(self.edge_width_spin, 1, 1)

        edge_group.setLayout(edge_grid)
        layout.addWidget(edge_group)

        # Action buttons
        layout.addSpacing(10)
        button_layout = QVBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)

        reset_btn = QPushButton("Reset to Default")
        reset_btn.setFixedWidth(180)
        reset_btn.clicked.connect(self._reset_style)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #C8C8C8;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
                border-color: #A0A0A0;
            }
            QPushButton:pressed {
                background-color: #E0E0E0;
            }
        """)
        button_layout.addWidget(reset_btn)

        export_btn = QPushButton("Export as Template")
        export_btn.setFixedWidth(180)
        export_btn.clicked.connect(self._export_template)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                border: 1px solid #C8C8C8;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #F0F0F0;
                border-color: #A0A0A0;
            }
            QPushButton:pressed {
                background-color: #E0E0E0;
            }
        """)
        button_layout.addWidget(export_btn)

        layout.addLayout(button_layout)
        layout.addStretch()

        scroll.setWidget(content_widget)

        # Set main layout
        main_layout = QVBoxLayout(self.main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)

        # Set outer layout for the panel
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(self.main_widget)

    def _load_default_style(self):
        """Load default style for root node."""
        self.style_params = {
            "bg_color": "#2196F3",
            "text_color": "#FFFFFF",
            "font_size": 22,
            "font_weight": "Bold",
            "padding_w": 20,
            "padding_h": 16,
            "radius": 10,
            "edge_color": "#2196F3",
            "edge_width": 3,
        }
        self._update_ui_from_params()

    def _adjust_menu_width(self, menu: QMenu, button: QPushButton):
        """Adjust the menu width to match the button width."""
        menu.setFixedWidth(button.width())

    def _set_depth(self, value: str):
        """Set the depth value and update preview."""
        self.depth_combo.setText(value)

        # Show/hide sections based on selection
        if value == "Individual Node":
            self.importance_group.setVisible(True)
            self.spacing_group.setVisible(False)
        else:
            self.importance_group.setVisible(False)
            self.spacing_group.setVisible(True)

        print(f"Selected depth: {value}")

    def _set_importance(self, value: str):
        """Set the importance level."""
        self.importance_combo.setText(value)
        print(f"Selected importance: {value}")

    def _set_font_weight(self, value: str):
        """Set the font weight value and update preview."""
        self.font_weight_combo.setText(value)
        self._update_preview()

    def _on_depth_changed(self):
        """Handle depth selection change."""
        depth_map = {"Root (0)": 0, "Level 1": 1, "Level 2": 2, "Level 3+": 3}
        self.current_depth = depth_map.get(self.depth_combo.text(), 0)
        # TODO: Load style for selected depth
        print(f"Selected depth: {self.current_depth}")

    def _pick_color(self, param_name):
        """Open color picker dialog."""
        current_color = self.style_params.get(param_name, "#000000")
        color = QColorDialog.getColor(current_color, self)

        if color.isValid():
            hex_color = color.name()
            self.style_params[param_name] = hex_color

            # Update button appearance
            if param_name == "bg_color":
                self.bg_color_btn.setStyleSheet(
                    f"background-color: {hex_color}; color: white;"
                )
            if param_name == "text_color":
                self.bg_color_btn.setStyleSheet(
                    f"background-color: {hex_color}; color: black; border: 1px solid #ccc;"
                )
            elif param_name == "edge_color":
                self.edge_color_btn.setStyleSheet(f"background-color: {hex_color};")

            self._update_preview()

    def _update_ui_from_params(self):
        """Update UI controls from style parameters."""
        self.font_size_spin.setValue(self.style_params.get("font_size", 22))
        self.font_weight_combo.setText(self.style_params.get("font_weight", "Bold"))
        self.padding_w_spin.setValue(self.style_params.get("padding_w", 20))
        self.padding_h_spin.setValue(self.style_params.get("padding_h", 16))
        self.radius_spin.setValue(self.style_params.get("radius", 10))
        self.edge_width_spin.setValue(self.style_params.get("edge_width", 3))

    def _update_preview(self):
        """Update style parameters from UI controls."""
        self.style_params.update(
            {
                "font_size": self.font_size_spin.value(),
                "font_weight": self.font_weight_combo.text(),
                "padding_w": self.padding_w_spin.value(),
                "padding_h": self.padding_h_spin.value(),
                "radius": self.radius_spin.value(),
                "edge_width": self.edge_width_spin.value(),
            }
        )
        print(f"Style updated: {self.style_params}")
        # TODO: Apply to preview node in main window

    def _apply_to_layer(self):
        """Apply current style to the selected layer."""
        print(f"Applying style to depth {self.current_depth}: {self.style_params}")
        # TODO: Send style to main window to apply

    def _reset_style(self):
        """Reset to default style."""
        self._load_default_style()
        print("Style reset to defaults")

    def _export_template(self):
        """Export current style as template JSON."""
        import json

        template = {
            "name": "Custom Template",
            "depth_styles": {str(self.current_depth): self.style_params},
        }

        json_str = json.dumps(template, indent=2)
        print(json_str)
        # TODO: Show save dialog and write to file
