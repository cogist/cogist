"""Toggle Switch Widget - iOS Style

A modern toggle switch widget with rounded rectangle background and circular thumb.
Similar to iOS/macOS system switches.

This widget can be reused across the application for any on/off toggle functionality.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton


class ToggleSwitch(QPushButton):
    """iOS-style toggle switch widget.

    A modern toggle switch with:
    - Rounded rectangle background (green when ON, gray when OFF)
    - Smooth hover and pressed states
    - Compact size (44x24 pixels)

    Usage:
        toggle = ToggleSwitch()
        toggle.toggled.connect(lambda checked: print(f"Switch is {'ON' if checked else 'OFF'}"))
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setChecked(False)
        self.setFixedSize(44, 24)
        self.setCursor(Qt.PointingHandCursor)
        self._update_style()
        self.toggled.connect(self._update_style)

    def _update_style(self):
        """Update stylesheet based on checked state."""
        if self.isChecked():
            # ON state: green background
            self.setStyleSheet("""
                QPushButton {
                    background-color: #34C759;
                    border-radius: 12px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #30B350;
                }
                QPushButton:pressed {
                    background-color: #2CA048;
                }
            """)
        else:
            # OFF state: gray background
            self.setStyleSheet("""
                QPushButton {
                    background-color: #E9E9EA;
                    border-radius: 12px;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #DCDCDD;
                }
                QPushButton:pressed {
                    background-color: #D1D1D2;
                }
            """)

    def set_checked(self, checked: bool):
        """Set the checked state without triggering signals.

        Args:
            checked: True for ON, False for OFF
        """
        self.blockSignals(True)
        self.setChecked(checked)
        self.blockSignals(False)
        self._update_style()
