"""Global Activity Bar - VSCode-style sidebar navigation.

Provides icon-based navigation to switch between different panels:
- Style Panel (current)
- Future: Layout, Theme, Settings, etc.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QPushButton, QVBoxLayout


class ActivityBarButton(QPushButton):
    """A button in the activity bar with icon and active state."""

    def __init__(self, icon_text: str, tooltip: str, parent=None):
        super().__init__(icon_text, parent)
        self.setFixedSize(48, 48)
        self.setToolTip(tooltip)
        self.setCheckable(True)
        self.setStyleSheet("""
            ActivityBarButton {
                background-color: #333333;
                border: none;
                color: #858585;
                font-size: 20px;
            }
            ActivityBarButton:hover {
                background-color: #333333;
                color: #C5C5C5;
            }
            ActivityBarButton:checked {
                background-color: #333333;
                color: #FFFFFF;
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
        # Simple mode button (⚙ Settings icon)
        simple_btn = ActivityBarButton("⚙", "Simple Mode")
        layout.addWidget(simple_btn)
        self.buttons["simple"] = simple_btn
        simple_btn.clicked.connect(lambda: self._on_activated("simple"))

        # Advanced mode button (🔧 Tools icon)
        advanced_btn = ActivityBarButton("🔧", "Advanced Mode")
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
