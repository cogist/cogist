"""Common widget utilities for consistent UI behavior."""

from qtpy.QtWidgets import QSpinBox


class SpinBox(QSpinBox):
    """QSpinBox with reversed wheel scrolling direction.

    Wheel up increases value (same as up arrow key).
    Wheel down decreases value (same as down arrow key).

    This provides a more intuitive user experience where scrolling
    up always means "increase" and scrolling down means "decrease".
    """

    # Standard spinbox stylesheet for consistent appearance
    STANDARD_STYLE = (
        "QSpinBox {"
        "    border: 1px solid #C8C8C8;"
        "    border-radius: 4px;"
        "    padding: 2px 8px;"
        "    background: white;"
        "}"
        "QSpinBox::up-button {"
        "    width: 14px;"
        "    height: 14px;"
        "    border: none;"
        "    background: transparent;"
        "    padding: 2px;"
        "}"
        "QSpinBox::down-button {"
        "    width: 14px;"
        "    height: 14px;"
        "    border: none;"
        "    background: transparent;"
        "    padding: 2px;"
        "}"
        "QSpinBox::up-button:hover, QSpinBox::down-button:hover {"
        "    background: #F5F5F5;"
        "}"
        "QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {"
        "    background: #E8E8E8;"
        "}"
        "QSpinBox::up-arrow {"
        "    image: url(assets/icons/arrow-up.svg);"
        "    width: 10px;"
        "    height: 10px;"
        "}"
        "QSpinBox::down-arrow {"
        "    image: url(assets/icons/arrow-down.svg);"
        "    width: 10px;"
        "    height: 10px;"
        "}"
    )

    def __init__(self, parent=None):
        """Initialize with standard styling applied."""
        super().__init__(parent)
        self.setStyleSheet(self.STANDARD_STYLE)

    def wheelEvent(self, event):
        """Override to ensure consistent scroll direction across platforms.

        Ensures wheel up increases value and wheel down decreases value,
        regardless of system scroll settings.
        """
        # Get the angle delta
        delta = event.angleDelta().y()

        if delta != 0:
            # On macOS with natural scrolling enabled, delta is inverted
            # We need to check the platform and adjust accordingly
            import sys
            if sys.platform == 'darwin':
                # macOS: invert delta to compensate for natural scrolling
                steps = -1 if delta > 0 else 1
            else:
                # Other platforms: use normal direction
                steps = 1 if delta > 0 else -1

            self.stepBy(steps)

        # Accept the event to prevent further propagation
        event.accept()
