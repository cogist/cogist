"""Toggle Switch Widget - iOS Style

A modern toggle switch widget with rounded rectangle background and circular thumb.
Similar to iOS/macOS system switches.

This widget can be reused across the application for any on/off toggle functionality.
"""

from qtpy.QtCore import QRectF, Qt
from qtpy.QtGui import QColor, QPainter, QPainterPath
from qtpy.QtWidgets import QPushButton


class ToggleSwitch(QPushButton):
    """iOS-style toggle switch widget.

    A modern toggle switch with:
    - Rounded rectangle background (green when ON, gray when OFF)
    - Circular thumb that slides left/right
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
        # Don't use stylesheet, we'll paint manually
        self.setStyleSheet("QPushButton { background: transparent; border: none; }")

    def paintEvent(self, event):
        """Paint the toggle switch."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Colors based on state
        if self.isChecked():
            bg_color = QColor("#34C759")  # Green
            if self.isDown():
                bg_color = QColor("#2CA048")
            elif self.underMouse():
                bg_color = QColor("#30B350")
        else:
            bg_color = QColor("#E9E9EA")  # Gray
            if self.isDown():
                bg_color = QColor("#D1D1D2")
            elif self.underMouse():
                bg_color = QColor("#DCDCDD")

        # Draw rounded rectangle background
        rect = QRectF(0, 0, self.width(), self.height())
        path = QPainterPath()
        path.addRoundedRect(rect, 12, 12)
        painter.fillPath(path, bg_color)

        # Draw circular thumb
        thumb_radius = 10
        thumb_y = self.height() / 2

        if self.isChecked():
            # Thumb on right side
            thumb_x = self.width() - thumb_radius - 2
        else:
            # Thumb on left side
            thumb_x = thumb_radius + 2

        painter.setBrush(QColor("#FFFFFF"))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(
            thumb_x - thumb_radius,
            thumb_y - thumb_radius,
            thumb_radius * 2,
            thumb_radius * 2
        ))

    def set_checked(self, checked: bool):
        """Set the checked state without triggering signals.

        Args:
            checked: True for ON, False for OFF
        """
        self.blockSignals(True)
        self.setChecked(checked)
        self.blockSignals(False)
        self.update()  # Trigger repaint
