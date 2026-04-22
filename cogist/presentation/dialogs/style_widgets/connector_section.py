"""Connector (edge) style section widget.

Provides controls for customizing edge appearance between nodes.
Implements lazy initialization for better performance.
"""

from PySide6.QtCore import QPoint, QSize, Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QGraphicsDropShadowEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from cogist.presentation.widgets import (
    generate_bezier_preview,
    generate_bezier_uniform_preview,
    generate_orthogonal_preview,
    generate_rounded_orthogonal_preview,
    generate_straight_preview,
)

from .collapsible_panel import CollapsiblePanel


class ConnectorShapePopup(QDialog):
    """Custom popup widget for connector shape selection with visual previews."""

    shape_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Content widget with background (flat design)
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            background-color: rgb(236, 236, 236);
            border-radius: 6px;
        """)

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 2)
        content_widget.setGraphicsEffect(shadow)

        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 4, 0, 4)
        content_layout.setSpacing(2)

        # Create preview options
        self.preview_labels = {}
        connector_shapes = [
            ("bezier", generate_bezier_preview),
            ("bezier_uniform", generate_bezier_uniform_preview),
            ("straight", generate_straight_preview),
            ("orthogonal", generate_orthogonal_preview),
            ("rounded_orthogonal", generate_rounded_orthogonal_preview),
        ]

        for value, preview_gen in connector_shapes:
            item_widget = QWidget()
            item_widget.setProperty("connector_shape_value", value)
            item_widget.setCursor(Qt.PointingHandCursor)

            item_layout = QVBoxLayout(item_widget)
            item_layout.setContentsMargins(0, 2, 0, 2)
            item_layout.setSpacing(0)

            # Create preview with smaller width for better centering
            preview_size = QSize(140, 30)
            pixmap = preview_gen(preview_size, selected=False)
            preview_label = QLabel()
            preview_label.setPixmap(pixmap)
            preview_label.setAlignment(Qt.AlignCenter)
            preview_label.setFixedSize(preview_size)
            preview_label.setStyleSheet("background: transparent;")
            item_layout.addWidget(preview_label, alignment=Qt.AlignCenter)

            self.preview_labels[value] = {
                "widget": item_widget,
                "label": preview_label,
                "generator": preview_gen,
                "size": preview_size,
            }

            # Connect click event
            item_widget.mousePressEvent = lambda _, v=value: self._on_item_clicked(v)
            item_widget.enterEvent = lambda _, v=value: self._on_item_hover(v, True)
            item_widget.leaveEvent = lambda _, v=value: self._on_item_hover(v, False)

            content_layout.addWidget(item_widget)

        main_layout.addWidget(content_widget)

    def _on_item_clicked(self, value: str):
        """Handle item click."""
        self.shape_selected.emit(value)
        self.close()

    def _on_item_hover(self, value: str, hovered: bool):
        """Update preview on hover."""
        if value in self.preview_labels:
            info = self.preview_labels[value]
            pixmap = info["generator"](info["size"], selected=hovered)
            info["label"].setPixmap(pixmap)

            # Apply blue background on hover (same as QMenu selection)
            if hovered:
                info["widget"].setStyleSheet("""
                    background-color: rgb(84, 143, 255);
                    border-radius: 4px;
                """)
            else:
                info["widget"].setStyleSheet("background: transparent;")


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

        # Connector shape selector (visual dropdown)
        shape_label = QLabel("Shape:")
        shape_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        shape_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(shape_label, 0, 0)

        # Create a button to show preview pattern only
        self.connector_shape_btn = QPushButton()
        self.connector_shape_btn.setFixedHeight(self.WIDGET_HEIGHT)
        self.connector_shape_btn.setFixedWidth(148)  # 140px pattern + 8px margins
        self.connector_shape_btn.setStyleSheet(self._button_style())

        # Button layout: preview pattern centered
        btn_layout = QHBoxLayout(self.connector_shape_btn)
        btn_layout.setContentsMargins(4, 2, 4, 2)
        btn_layout.setSpacing(0)

        btn_layout.addStretch()

        # Preview pattern label
        self.connector_shape_preview = QLabel()
        self.connector_shape_preview.setFixedSize(QSize(140, 30))
        self.connector_shape_preview.setAlignment(Qt.AlignCenter)
        self.connector_shape_preview.setStyleSheet("background: transparent;")
        btn_layout.addWidget(self.connector_shape_preview)

        btn_layout.addStretch()

        # Store preview options for popup
        self.connector_shape_options = [
            ("bezier", generate_bezier_preview),
            ("bezier_uniform", generate_bezier_uniform_preview),
            ("straight", generate_straight_preview),
            ("orthogonal", generate_orthogonal_preview),
            ("rounded_orthogonal", generate_rounded_orthogonal_preview),
        ]

        # Set initial preview pattern
        self._update_shape_preview()

        # Create custom popup widget instead of QMenu
        self.connector_shape_popup = ConnectorShapePopup(self)
        self.connector_shape_btn.clicked.connect(self._show_connector_shape_popup)

        # Connect popup selection signal
        self.connector_shape_popup.shape_selected.connect(
            self._on_connector_shape_changed
        )
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
        self.connector_style_combo = QPushButton(initial_connector_style)
        self.connector_style_combo.setFixedHeight(self.WIDGET_HEIGHT)
        self.connector_style_combo.setStyleSheet(self._button_style())

        self.connector_style_menu = QMenu()
        self.connector_style_menu.aboutToShow.connect(
            lambda: self.connector_style_menu.setFixedWidth(
                self.connector_style_combo.width()
            )
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

    def _show_connector_shape_popup(self):
        """Show custom popup for connector shape selection."""
        # Position popup below the button with same width
        btn_width = self.connector_shape_btn.width()
        btn_pos = self.connector_shape_btn.mapToGlobal(
            QPoint(0, self.connector_shape_btn.height())
        )
        self.connector_shape_popup.setFixedWidth(btn_width)
        self.connector_shape_popup.move(btn_pos)
        self.connector_shape_popup.show()

    def _update_shape_preview(self):
        """Update the preview pattern on the button."""
        shape = self.current_style.get("connector_shape", "bezier")
        preview_size = QSize(140, 30)  # Match the label size

        # Find the generator for current shape
        for shape_value, generator in self.connector_shape_options:
            if shape_value == shape:
                pixmap = generator(preview_size, selected=False)
                self.connector_shape_preview.setPixmap(pixmap)
                break

    def _on_connector_shape_changed(self, value: str):
        """Handle connector shape selection change."""
        self.current_style["connector_shape"] = value
        self._update_shape_preview()
        self.connector_shape_popup.close()
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
                self._update_shape_preview()

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
