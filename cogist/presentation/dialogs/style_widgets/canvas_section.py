"""Canvas background section widget.

Provides controls for customizing the canvas background color.
Implements lazy initialization - only creates widgets when expanded.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton

from .collapsible_panel import CollapsiblePanel
from .dialog_utils import position_color_dialog


class CanvasSection(CollapsiblePanel):
    """Canvas background settings with lazy initialization.

    Signals:
        color_changed(str): Emitted when canvas background color changes
    """

    color_changed = Signal(str)

    # UI constants
    LABEL_WIDTH = 75
    WIDGET_HEIGHT = 32
    GROUP_MARGIN = 10

    def __init__(self, parent=None):
        super().__init__("Canvas Background", collapsed=True, parent=parent)

        # State
        self._initialized = False
        self.current_color = "#FFFFFF"

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

        # Background color label
        bg_label = QLabel("Background:")
        bg_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        bg_label.setMinimumWidth(self.LABEL_WIDTH)
        layout.addWidget(bg_label, 0, 0)

        # Color picker button
        self.canvas_bg_btn = QPushButton()
        self.canvas_bg_btn.setFixedHeight(self.WIDGET_HEIGHT)
        self.canvas_bg_btn.setStyleSheet(
            f"background-color: {self.current_color}; "
            "border: 1px solid #ccc; border-radius: 6px;"
        )
        self.canvas_bg_btn.clicked.connect(self._pick_color)
        layout.addWidget(self.canvas_bg_btn, 0, 1)

        self.setLayout(layout)

    def _pick_color(self):
        """Open color picker dialog."""
        from PySide6.QtWidgets import QColorDialog

        current = QColor(self.current_color)
        color_dialog = QColorDialog(current, self)
        color_dialog.setWindowTitle("Select Canvas Background Color")

        # Use Qt's standard dialog instead of native dialog to allow positioning
        color_dialog.setOption(QColorDialog.DontUseNativeDialog)

        # Enable alpha channel (transparency) support
        color_dialog.setOption(QColorDialog.ShowAlphaChannel)

        # Position dialog with boundary check
        position_color_dialog(color_dialog, self.canvas_bg_btn)

        if color_dialog.exec():
            color = color_dialog.currentColor()
            if color.isValid():
                self.current_color = color.name()
                self.canvas_bg_btn.setStyleSheet(
                    f"background-color: {self.current_color}; "
                    "border: 1px solid #ccc; border-radius: 6px;"
                )
                self.color_changed.emit(self.current_color)

    def get_color(self) -> str:
        """Get current canvas background color."""
        return self.current_color

    def set_color(self, color: str):
        """Set canvas background color programmatically.

        Args:
            color: Hex color string (e.g., "#FFFFFF")
        """
        self.current_color = color
        if hasattr(self, 'canvas_bg_btn'):
            self.canvas_bg_btn.setStyleSheet(
                f"background-color: {color}; "
                "border: 1px solid #ccc; border-radius: 6px;"
            )
