"""Global Activity Bar - VSCode-style sidebar navigation.

Provides icon-based navigation to switch between different panels:
- Style Panel (current)
- Future: Layout, Theme, Settings, etc.
"""

import sys
from pathlib import Path

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout


def get_resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller mode
        base_path = Path(sys._MEIPASS)
    else:
        # Development mode - go up 4 levels from this file to project root
        base_path = Path(__file__).resolve().parent.parent.parent.parent

    return str(base_path / relative_path)


class ActivityBarButton(QPushButton):
    """A button in the activity bar with icon and active state."""

    def __init__(self, icon_path: str, tooltip: str, parent=None):
        super().__init__(parent)
        self.setFixedSize(48, 48)
        self.setToolTip(tooltip)
        self.setCheckable(True)

        # Set SVG icon
        icon = QIcon(icon_path)
        self.setIcon(icon)
        self.setIconSize(QSize(32, 32))

        # Set tooltip style - white text on dark background (opposite of button background)
        self.setStyleSheet("""
            ActivityBarButton {
                background-color: #333333;
                border: none;
            }
            ActivityBarButton:hover {
                background-color: #333333;
            }
            ActivityBarButton:checked {
                background-color: #333333;
            }
            QToolTip {
                background-color: #FFFFFF;
                color: #000000;
                border: 1px solid #CCCCCC;
                padding: 4px;
            }
        """)


class ActivityBar(QFrame):
    """Global activity bar for the main window.

    Signals:
        panel_activated(str): Emitted when a panel button is clicked
    """

    panel_activated = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(48)
        self.setStyleSheet("background-color: #333333; border: none;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignTop)

        # Activity buttons
        self.buttons = {}

        # Style panel buttons
        # Color scheme button (Color wheel icon)
        color_scheme_icon = get_resource_path("assets/icons/color-scheme.svg")
        color_scheme_btn = ActivityBarButton(color_scheme_icon, "Color Scheme")
        layout.addWidget(color_scheme_btn)
        self.buttons["color_scheme"] = color_scheme_btn
        color_scheme_btn.clicked.connect(lambda: self._on_activated("color_scheme"))

        # Advanced mode button (Gear icon)
        gear_icon = get_resource_path("assets/icons/gear.svg")
        advanced_btn = ActivityBarButton(gear_icon, "Advanced Mode")
        layout.addWidget(advanced_btn)
        self.buttons["advanced"] = advanced_btn
        advanced_btn.clicked.connect(lambda: self._on_activated("advanced"))

        # Future: add more buttons here
        # layout_btn = ActivityBarButton("📐", "Layout Panel")
        # layout.addWidget(layout_btn)
        # self.buttons["layout"] = layout_btn

        layout.addStretch()

    def _on_activated(self, panel_name: str):
        """Handle button click."""
        # Uncheck all other buttons
        for name, btn in self.buttons.items():
            if name != panel_name:
                btn.setChecked(False)

        self.panel_activated.emit(panel_name)

    def activate_panel(self, panel_name: str):
        """Programmatically activate a panel."""
        if panel_name in self.buttons:
            self.buttons[panel_name].setChecked(True)
            # Trigger the click handler
            for name, btn in self.buttons.items():
                if name != panel_name:
                    btn.setChecked(False)
            self.panel_activated.emit(panel_name)
