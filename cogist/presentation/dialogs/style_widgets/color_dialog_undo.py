"""Color dialog undo helper for style widgets.

Provides a reusable mixin class for color dialogs with undo support.
This ensures consistent behavior across all color pickers in the style editor.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class ColorDialogUndoMixin:
    """Mixin class to add undo support to color dialogs.

    Usage:
        1. Inherit from this mixin in your widget class
        2. Call setup_color_dialog_undo() when creating the color picker
        3. Call on_color_dialog_closed() when dialog closes

    Example:
        class MyWidget(ColorDialogUndoMixin):
            def _on_color_clicked(self):
                self._color_picker = create_color_picker(parent)
                self.setup_color_dialog_undo(
                    color_picker=self._color_picker,
                    layer="root",
                    style_key="bg_color",
                    get_current_color=lambda: self.style_config.special_colors["root_background"],
                )
                self._color_picker.finished.connect(self.on_color_dialog_closed)
    """

    def setup_color_dialog_undo(
        self,
        color_picker,
        layer: str,
        style_key: str,
        get_current_color,
    ):
        """Setup undo support for a color dialog.

        Args:
            color_picker: The ColorPicker instance
            layer: Layer name (e.g., "root", "canvas")
            style_key: Style property key (e.g., "bg_color", "border_color")
            get_current_color: Callable that returns the current color value
        """
        # Save original color for undo command
        self._original_color = get_current_color()
        self._undo_layer = layer
        self._undo_style_key = style_key
        self._color_picker_ref = color_picker

        # Connect finished signal to create undo command
        color_picker.finished.connect(self._on_color_dialog_finished_for_undo)

    def _on_color_dialog_finished_for_undo(self):
        """Handle color dialog close - create undo command."""
        if not hasattr(self, '_undo_layer'):
            return

        # Get parent (StyleEditorTab)
        parent = getattr(self, '_advanced_tab', None)
        if not parent:
            return

        if not hasattr(parent, 'style_config') or not parent.style_config:
            return

        if not hasattr(parent, 'command_history') or not parent.command_history:
            return

        # Get final color (already updated by real-time preview)
        final_color = self._get_final_color()
        original_color = getattr(self, '_original_color', None)

        if original_color is None:
            return

        # Only create undo command if color actually changed
        if final_color != original_color:
            from cogist.application.commands import ChangeStyleCommand
            from cogist.application.commands.change_style_command import StyleChange

            change = StyleChange(
                layer=self._undo_layer,
                style_updates={self._undo_style_key: final_color}
            )
            command = ChangeStyleCommand(
                style_config=parent.style_config,
                changes=[change]
            )
            # Manually set old_values to the original color before any changes
            command.old_values.append({
                "layer": self._undo_layer,
                "old_values": {self._undo_style_key: original_color}
            })
            command.execute()
            parent.command_history.push(command)

        # Cleanup
        if hasattr(self, '_original_color'):
            del self._original_color
        if hasattr(self, '_undo_layer'):
            del self._undo_layer
        if hasattr(self, '_undo_style_key'):
            del self._undo_style_key

    def _get_final_color(self):
        """Get the final color value. Override this method in subclasses."""
        raise NotImplementedError("Subclasses must implement _get_final_color()")
