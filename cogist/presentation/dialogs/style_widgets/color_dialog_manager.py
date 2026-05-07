"""Color dialog manager for non-modal color picking with undo support.

This module provides a centralized color dialog manager that:
1. Creates non-modal QColorDialog instances
2. Tracks the original color before changes
3. Supports one-click undo to restore the original color
4. Uses qtpy for cross-Qt compatibility
"""

from collections.abc import Callable

from qtpy.QtGui import QColor
from qtpy.QtWidgets import QColorDialog, QPushButton, QWidget

from .dialog_utils import position_color_dialog


class ColorDialogManager:
    """Manages non-modal color dialogs with undo support.

    This class creates and manages QColorDialog instances that:
    - Are non-modal (don't block UI)
    - Apply colors in real-time as user picks
    - Support one-click undo to restore original color
    - Automatically clean up when closed

    Usage:
        manager = ColorDialogManager()
        manager.show_color_dialog(
            parent_widget=button,
            initial_color="#FFFF0000",
            on_color_changed=lambda color: apply_color(color),
            command_history=command_history,  # Optional: for undo support
            create_undo_command=lambda old, new: ChangeStyleCommand(...)
        )
    """

    def __init__(self):
        self._active_dialogs: dict[int, dict] = {}  # id(dialog) -> dialog info

    def show_color_dialog(
        self,
        parent_widget: QWidget,
        trigger_button: QPushButton,
        initial_color: str,
        on_color_changed: Callable[[str], None],
        layer: str = "",
        style_key: str = "",
        command_history=None,
        create_undo_command=None,
        show_alpha: bool = False,
    ) -> QColorDialog:
        """Show a non-modal color dialog with undo support.

        Args:
            parent_widget: Parent widget for dialog lifecycle
            trigger_button: Button that triggered the dialog (for positioning)
            initial_color: Initial color in #AARRGGBB or #RRGGBB format
            on_color_changed: Callback when color changes (receives hex color)
            layer: Layer name for undo command (e.g., "root", "level_1")
            style_key: Style property key (e.g., "bg_color", "border_color")
            command_history: CommandHistory instance for undo/redo (optional)
            create_undo_command: Function to create undo command (optional)
                Signature: (old_color: str, new_color: str) -> Command
            show_alpha: Whether to show alpha channel in dialog

        Returns:
            QColorDialog instance
        """
        top_level = parent_widget.window() if parent_widget.window() else parent_widget

        # Create or reuse dialog
        dialog = QColorDialog(top_level)
        dialog.setOptions(
            QColorDialog.NoButtons  # No OK/Cancel - apply immediately
            | QColorDialog.DontUseNativeDialog
        )

        if show_alpha:
            dialog.setOption(QColorDialog.ShowAlphaChannel, True)

        # Store original color for undo
        original_color = initial_color

        # Track if user has made changes
        has_changes = False

        def on_current_color_changed(color: QColor):
            """Handle real-time color changes."""
            nonlocal has_changes
            hex_color = color.name(QColor.NameFormat.HexArgb)

            # Mark that changes have been made
            has_changes = True

            # Apply color in real-time
            on_color_changed(hex_color)

        def on_dialog_finished(result):
            """Handle dialog close."""
            dialog_id = id(dialog)

            if dialog_id in self._active_dialogs:
                dialog_info = self._active_dialogs[dialog_id]

                # If user accepted (clicked outside or pressed Escape = rejected)
                if (result == QColorDialog.DialogCode.Accepted or has_changes) and command_history and create_undo_command and has_changes:
                    try:
                        cmd = create_undo_command(original_color, dialog_info.get("last_color", original_color))
                        cmd.execute()
                        command_history.push(cmd)
                    except Exception as e:
                        print(f"Failed to create undo command: {e}")

                # Clean up
                del self._active_dialogs[dialog_id]

        # Connect signals
        dialog.currentColorChanged.connect(on_current_color_changed)
        dialog.finished.connect(on_dialog_finished)

        # Set initial color (block signals to prevent triggering change)
        dialog.blockSignals(True)
        if initial_color.startswith("#"):
            color_str = initial_color[1:]
        else:
            color_str = initial_color

        if len(color_str) == 6:
            # #RRGGBB format
            qt_color = QColor(f"#{color_str}")
            qt_color.setAlpha(255)
        elif len(color_str) == 8:
            # #AARRGGBB format
            alpha = int(color_str[0:2], 16)
            rgb = color_str[2:]
            qt_color = QColor(f"#{rgb}")
            qt_color.setAlpha(alpha)
        else:
            qt_color = QColor("#FF000000")

        dialog.setCurrentColor(qt_color)
        dialog.blockSignals(False)

        # Store dialog info
        self._active_dialogs[id(dialog)] = {
            "original_color": original_color,
            "last_color": original_color,
            "layer": layer,
            "style_key": style_key,
        }

        # Show dialog
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

        # Position dialog next to trigger button
        position_color_dialog(dialog, trigger_button)

        return dialog

    def close_all_dialogs(self):
        """Close all active color dialogs."""
        for dialog_id in list(self._active_dialogs.keys()):
            # Dialog should be deleted by WA_DeleteOnClose, but we clean up our tracking
            if dialog_id in self._active_dialogs:
                del self._active_dialogs[dialog_id]


# Global instance for convenience
_global_color_dialog_manager = ColorDialogManager()


def show_color_dialog_with_undo(
    parent_widget: QWidget,
    trigger_button: QPushButton,
    initial_color: str,
    on_color_changed: Callable[[str], None],
    layer: str = "",
    style_key: str = "",
    command_history=None,
    create_undo_command=None,
    show_alpha: bool = False,
) -> QColorDialog:
    """Convenience function to show color dialog with undo support.

    This is a wrapper around ColorDialogManager.show_color_dialog()
    using a global manager instance.

    Args:
        See ColorDialogManager.show_color_dialog()

    Returns:
        QColorDialog instance
    """
    return _global_color_dialog_manager.show_color_dialog(
        parent_widget=parent_widget,
        trigger_button=trigger_button,
        initial_color=initial_color,
        on_color_changed=on_color_changed,
        layer=layer,
        style_key=style_key,
        command_history=command_history,
        create_undo_command=create_undo_command,
        show_alpha=show_alpha,
    )
