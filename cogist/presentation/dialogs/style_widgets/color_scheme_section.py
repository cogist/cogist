"""Color scheme section widget.

Provides controls for customizing color scheme including:
- Per-role colors (foreground, background, border, connector)
- Auto-calculation for derived levels
- Rainbow branch colors
- Canvas background

This section is Part of Presentation Layer (UI).
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from .collapsible_panel import CollapsiblePanel


class ColorPickerButton(QPushButton):
    """Color picker button with color display."""

    def __init__(self, color: str = "#FFFFFF", parent=None):
        super().__init__(parent)
        self.current_color = color
        self._init_ui()

    def _init_ui(self):
        self.setFixedHeight(28)
        self.setFixedWidth(60)
        self._update_style()

    def _update_style(self):
        self.setStyleSheet(
            f"background-color: {self.current_color}; "
            "border: 1px solid #CCCCCC; border-radius: 4px;"
        )

    def set_color(self, color: str):
        self.current_color = color
        self._update_style()

    def get_color(self) -> str:
        return self.current_color

    def mousePressEvent(self, event):
        from PySide6.QtWidgets import QColorDialog
        color = QColorDialog.getColor(
            QColor(self.current_color), self, "Select Color", QColorDialog.ShowAlphaChannel
        )
        if color.isValid():
            self.current_color = color.name(QColor.HexArgb)
            self._update_style()
            self.color_changed.emit(self.current_color)

    color_changed = Signal(str)


class RainbowColorPool(QWidget):
    """Rainbow branch color pool with 8 color buttons."""

    color_pool_changed = Signal(list)

    def __init__(self, colors: list[str] = None, parent=None):
        super().__init__(parent)
        self.colors = colors or [
            "#FF6B6B", "#FF4ECDC4", "#FF45B7D1", "#FFFFA07A",
            "#FF98D8C8", "#FFF7DC6F", "#FFBB8FCE", "#FF85C1E9",
        ]
        self._init_ui()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)

        self.buttons = []
        for i, color in enumerate(self.colors):
            btn = QPushButton()
            btn.setFixedSize(24, 24)
            btn.setStyleSheet(f"background-color: {color}; border: 1px solid #CCCCCC; border-radius: 3px;")
            btn.clicked.connect(lambda _, idx=i: self._edit_color(idx))
            self.buttons.append(btn)
            layout.addWidget(btn)

    def _edit_color(self, index: int):
        from PySide6.QtWidgets import QColorDialog
        color = QColorDialog.getColor(
            QColor(self.colors[index]), self, "Select Branch Color", QColorDialog.ShowAlphaChannel
        )
        if color.isValid():
            self.colors[index] = color.name(QColor.HexArgb)
            self.buttons[index].setStyleSheet(
                f"background-color: {self.colors[index]}; border: 1px solid #CCCCCC; border-radius: 3px;"
            )
            self.color_pool_changed.emit(self.colors)

    def set_colors(self, colors: list[str]):
        self.colors = colors[:8]  # Ensure 8 colors
        for i, btn in enumerate(self.buttons):
            btn.setStyleSheet(
                f"background-color: {self.colors[i]}; border: 1px solid #CCCCCC; border-radius: 3px;"
            )

    def get_colors(self) -> list[str]:
        return self.colors


class ColorSchemeSection(CollapsiblePanel):
    """Color scheme settings section.

    Signals:
        color_changed(dict): Emitted when color properties change
    """

    color_changed = Signal(dict)

    # UI constants
    LABEL_WIDTH = 65
    WIDGET_HEIGHT = 28
    GROUP_MARGIN = 10

    def __init__(self, parent=None):
        super().__init__("Color Scheme", collapsed=True, parent=parent)

        self._initialized = False
        self.current_role = None
        self._rainbow_visible = False  # Track rainbow check state
        self._default_colors = {
            "foreground": "#FFFFFF",
            "background": "#FF2196F3",
            "border": "#FF1976D2",
            "connector": "#FF1565C0",
        }
        self._auto_enabled = {
            "level2": False,
            "level3": False,
        }
        # Store label references
        self.fg_label: QLabel | None = None
        self.bg_label: QLabel | None = None
        self.border_label: QLabel | None = None
        self.conn_label: QLabel | None = None
        self.canvas_label: QLabel | None = None
        self.rainbow_label: QLabel | None = None
        self._rainbow_row = -1

        self.toggled.connect(self._on_toggled)

    def _on_toggled(self, checked: bool):
        if checked and not self._initialized:
            self._init_content()
            self._initialized = True
            # Initialize role visibility after content is created
            self.set_role("root")

    def _init_content(self):
        layout = QGridLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(self.GROUP_MARGIN, 16, self.GROUP_MARGIN, 16)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)
        layout.setColumnStretch(2, 0)

        # Foreground color
        fg_label = QLabel("Foreground:")
        fg_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        fg_label.setMinimumWidth(self.LABEL_WIDTH)
        self.fg_picker = ColorPickerButton(self._default_colors["foreground"])
        self.fg_picker.color_changed.connect(lambda c: self._emit_change("foreground", c))
        self.auto_fg = QCheckBox("Auto")
        self.auto_fg.stateChanged.connect(lambda s: self._on_auto_changed("foreground", s))
        layout.addWidget(fg_label, 0, 0)
        layout.addWidget(self.fg_picker, 0, 1)
        layout.addWidget(self.auto_fg, 0, 2)

        # Background color (show for: root, level_1, level_2, level_3_plus)
        self.bg_label = QLabel("Background:")
        self.bg_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.bg_picker = ColorPickerButton(self._default_colors["background"])
        self.bg_picker.color_changed.connect(lambda c: self._emit_change("background", c))
        self.auto_bg = QCheckBox("Auto")
        self.auto_bg.stateChanged.connect(lambda s: self._on_auto_changed("background", s))
        layout.addWidget(self.bg_label, 1, 0)
        layout.addWidget(self.bg_picker, 1, 1)
        layout.addWidget(self.auto_bg, 1, 2)

        # Border color (show for: root, level_1, level_2, level_3_plus)
        self.border_label = QLabel("Border:")
        self.border_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.border_picker = ColorPickerButton(self._default_colors["border"])
        self.border_picker.color_changed.connect(lambda c: self._emit_change("border", c))
        self.auto_border = QCheckBox("Auto")
        self.auto_border.stateChanged.connect(lambda s: self._on_auto_changed("border", s))
        layout.addWidget(self.border_label, 2, 0)
        layout.addWidget(self.border_picker, 2, 1)
        layout.addWidget(self.auto_border, 2, 2)

        # Connector color (show for: root, level_1, level_2, level_3_plus)
        self.conn_label = QLabel("Connector:")
        self.conn_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.conn_picker = ColorPickerButton(self._default_colors["connector"])
        self.conn_picker.color_changed.connect(lambda c: self._emit_change("connector", c))
        self.auto_conn = QCheckBox("Auto")
        self.auto_conn.stateChanged.connect(lambda s: self._on_auto_changed("connector", s))
        layout.addWidget(self.conn_label, 3, 0)
        layout.addWidget(self.conn_picker, 3, 1)
        layout.addWidget(self.auto_conn, 3, 2)

        # Canvas background (show only when Layer is canvas)
        self.canvas_label = QLabel("Canvas:")
        self.canvas_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.canvas_picker = ColorPickerButton("#FFFFFF")
        self.canvas_picker.color_changed.connect(lambda c: self._emit_change("canvas_bg", c))
        self.canvas_row = 4
        layout.addWidget(self.canvas_label, 4, 0)
        layout.addWidget(self.canvas_picker, 4, 1)

        # Rainbow branches (show only when Layer is level_1)
        rainbow_label = QLabel("Rainbow:")
        rainbow_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.rainbow_label = rainbow_label
        self.rainbow_check = QCheckBox("Rainbow")
        self.rainbow_check.stateChanged.connect(self._on_rainbow_changed)
        self.rainbow_pool = RainbowColorPool()
        self.rainbow_pool.setVisible(False)
        self.rainbow_pool.color_pool_changed.connect(
            lambda colors: self._emit_change("rainbow_pool", colors)
        )
        # Rainbow row (initially hidden, adjusted in set_role)
        self._rainbow_row = -1

        self.setLayout(layout)

    def _emit_change(self, key: str, value):
        self.color_changed.emit({key: value})

    def _on_auto_changed(self, color_type: str, state: int):
        enabled = state == Qt.Checked
        if color_type == "foreground":
            self.fg_picker.setEnabled(not enabled)
            self._emit_change("auto_fg", enabled)
        elif color_type == "background":
            self.bg_picker.setEnabled(not enabled)
            # Emit level auto based on current role
            if self.current_role == "level_2":
                self._emit_change("level2_auto", enabled)
            elif self.current_role == "level_3_plus":
                self._emit_change("level3_auto", enabled)
        elif color_type == "border":
            self.border_picker.setEnabled(not enabled)
        elif color_type == "connector":
            self.conn_picker.setEnabled(not enabled)

    def _on_rainbow_changed(self, state: int):
        enabled = state == Qt.Checked
        self._rainbow_visible = enabled
        self.rainbow_pool.setVisible(enabled)
        self._emit_change("use_rainbow", enabled)

    def set_role(self, role: str):
        """Set current role and update UI accordingly."""
        self.current_role = role

        # Canvas: show only canvas picker
        if role == "canvas":
            if self.fg_label:
                self.fg_label.setVisible(False)
            self.fg_picker.setVisible(False)
            self.auto_fg.setVisible(False)

            if self.bg_label:
                self.bg_label.setVisible(False)
            self.bg_picker.setVisible(False)
            self.auto_bg.setVisible(False)

            if self.border_label:
                self.border_label.setVisible(False)
            self.border_picker.setVisible(False)
            self.auto_border.setVisible(False)

            if self.conn_label:
                self.conn_label.setVisible(False)
            self.conn_picker.setVisible(False)
            self.auto_conn.setVisible(False)

            if self.rainbow_label:
                self.rainbow_label.setVisible(False)
            self.rainbow_check.setVisible(False)
            self.rainbow_pool.setVisible(False)

            # Show canvas
            if self.canvas_label:
                self.canvas_label.setVisible(True)
            self.canvas_picker.setVisible(True)

        # Root/Level 1: show all colors, hide Auto and rainbow (Level 1 shows rainbow below)
        elif role in ("root", "level_1"):
            if self.fg_label:
                self.fg_label.setVisible(True)
            self.fg_picker.setVisible(True)
            self.auto_fg.setVisible(False)

            if self.bg_label:
                self.bg_label.setVisible(True)
            self.bg_picker.setVisible(True)
            self.auto_bg.setVisible(False)

            if self.border_label:
                self.border_label.setVisible(True)
            self.border_picker.setVisible(True)
            self.auto_border.setVisible(False)

            if self.conn_label:
                self.conn_label.setVisible(True)
            self.conn_picker.setVisible(True)
            self.auto_conn.setVisible(False)

            if self.canvas_label:
                self.canvas_label.setVisible(False)
            self.canvas_picker.setVisible(False)

            # Level 1 shows rainbow
            if role == "level_1":
                if self.rainbow_label:
                    self.rainbow_label.setVisible(True)
                self.rainbow_check.setVisible(True)
                if self._rainbow_visible:
                    self.rainbow_pool.setVisible(True)
            else:
                if self.rainbow_label:
                    self.rainbow_label.setVisible(False)
                self.rainbow_check.setVisible(False)
                self.rainbow_pool.setVisible(False)

        # Level 2+: show colors + Auto
        elif role in ("level_2", "level_3_plus"):
            if self.fg_label:
                self.fg_label.setVisible(True)
            self.fg_picker.setVisible(True)
            self.auto_fg.setVisible(True)

            if self.bg_label:
                self.bg_label.setVisible(True)
            self.bg_picker.setVisible(True)
            self.auto_bg.setVisible(True)

            if self.border_label:
                self.border_label.setVisible(True)
            self.border_picker.setVisible(True)
            self.auto_border.setVisible(True)

            if self.conn_label:
                self.conn_label.setVisible(True)
            self.conn_picker.setVisible(True)
            self.auto_conn.setVisible(True)

            if self.canvas_label:
                self.canvas_label.setVisible(False)
            self.canvas_picker.setVisible(False)

            if self.rainbow_label:
                self.rainbow_label.setVisible(False)
            self.rainbow_check.setVisible(False)
            self.rainbow_pool.setVisible(False)

    def set_colors(self, colors: dict):
        """Set color values from ColorScheme."""
        if "foreground" in colors:
            self.fg_picker.set_color(colors["foreground"])
        if "background" in colors:
            self.bg_picker.set_color(colors["background"])
        if "border" in colors:
            self.border_picker.set_color(colors["border"])
        if "connector" in colors:
            self.conn_picker.set_color(colors["connector"])
        if "canvas_bg" in colors:
            self.canvas_picker.set_color(colors["canvas_bg"])
        if "use_rainbow" in colors:
            self.rainbow_check.setChecked(colors["use_rainbow"])
            self.rainbow_pool.setVisible(colors["use_rainbow"])
        if "rainbow_pool" in colors:
            self.rainbow_pool.set_colors(colors["rainbow_pool"])
        if "level2_auto" in colors:
            self.auto_bg.setChecked(colors["level2_auto"])
        if "level3_auto" in colors:
            self.auto_bg.setChecked(colors["level3_auto"])
