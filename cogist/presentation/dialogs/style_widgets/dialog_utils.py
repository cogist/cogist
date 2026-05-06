"""Dialog utility functions for style widgets.

Provides common helper functions for dialog positioning and interaction.
"""

from qtpy.QtWidgets import QApplication


def position_color_dialog(color_dialog, button):
    """Position color dialog to the right of button with screen boundary check.

    Args:
        color_dialog: QColorDialog instance to position
        button: QPushButton that triggered the dialog

    The function will:
    - Try to position dialog to the right of button (4px gap)
    - If right side has no space, position to the left
    - Ensure dialog stays within screen boundaries
    - Align top edges by default
    """
    # Get button position in global coordinates
    button_pos = button.mapToGlobal(button.rect().topLeft())
    button_width = button.width()

    # Calculate initial position (right of button, top aligned)
    dialog_x = button_pos.x() + button_width + 4  # 4px gap
    dialog_y = button_pos.y()

    # Get screen geometry for boundary check
    screen = QApplication.screenAt(button_pos)
    if screen is None:
        screen = QApplication.primaryScreen()

    if screen:
        screen_geometry = screen.availableGeometry()
        dialog_width = color_dialog.sizeHint().width()
        dialog_height = color_dialog.sizeHint().height()

        # Check right boundary
        if dialog_x + dialog_width > screen_geometry.right():
            # Position to the left of button instead
            dialog_x = button_pos.x() - dialog_width - 4

        # Check bottom boundary
        if dialog_y + dialog_height > screen_geometry.bottom():
            # Align to bottom of screen
            dialog_y = screen_geometry.bottom() - dialog_height

        # Check top boundary
        if dialog_y < screen_geometry.top():
            dialog_y = screen_geometry.top()

        # Check left boundary
        if dialog_x < screen_geometry.left():
            dialog_x = screen_geometry.left()

    # Move dialog to calculated position
    color_dialog.move(dialog_x, dialog_y)
