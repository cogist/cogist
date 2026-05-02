"""Common widget utilities for consistent UI behavior."""

from PySide6.QtWidgets import QSpinBox


class ReverseWheelSpinBox(QSpinBox):
    """QSpinBox with reversed wheel scrolling direction.

    Wheel up increases value (same as up arrow key).
    Wheel down decreases value (same as down arrow key).

    This provides a more intuitive user experience where scrolling
    up always means "increase" and scrolling down means "decrease".
    """

    def wheelEvent(self, event):
        """Override to reverse wheel scrolling direction."""
        # Get the angle delta (positive = up, negative = down)
        delta = event.angleDelta().y()

        if delta > 0:
            # Wheel up -> increase value
            self.stepBy(1)
        elif delta < 0:
            # Wheel down -> decrease value
            self.stepBy(-1)

        # Accept the event to prevent further propagation
        event.accept()
