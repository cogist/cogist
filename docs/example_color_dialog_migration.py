"""Example: Migrating to ColorDialogManager

This file demonstrates how to migrate existing color picker code
to use the new ColorDialogManager with undo support.
"""

# ============================================================================
# BEFORE: Old implementation (shadow_section.py style)
# ============================================================================

class OldShadowSection:
    """Old implementation without centralized management."""
    
    def __init__(self):
        self._color_picker = None
        self.current_shadow = {"color": "#FF000000", "offset_x": 2, "offset_y": 2, "blur": 4}
    
    def _pick_color_old(self):
        """Old way: manual dialog management."""
        from qtpy.QtWidgets import QColorDialog
        from qtpy.QtCore import Qt
        from .color_picker import create_color_picker
        from .dialog_utils import position_color_dialog
        
        top_level = self.window() if self.window() else self
        
        # Manual lifecycle management
        if self._color_picker is None or not self._color_picker:
            self._color_picker = create_color_picker(top_level)
            self._color_picker.color_selected.connect(self._on_shadow_color_selected)
            self._color_picker.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
            
            # Enable alpha channel
            self._color_picker.setOption(QColorDialog.ShowAlphaChannel, True)
        
        # Set current color
        current_color = self.current_shadow["color"]
        self._color_picker.set_current_color(current_color)
        
        # Show dialog
        self._color_picker.show()
        self._color_picker.raise_()
        self._color_picker.activateWindow()
        
        # Position dialog
        position_color_dialog(self._color_picker, self.shadow_color_btn)
    
    def _on_shadow_color_selected(self, hex_color: str):
        """Handle color selection - NO UNDO SUPPORT."""
        self.current_shadow["color"] = hex_color
        # Apply immediately, no undo command created
        self._apply_shadow()


# ============================================================================
# AFTER: New implementation with ColorDialogManager
# ============================================================================

class NewShadowSection:
    """New implementation with ColorDialogManager and undo support."""
    
    def __init__(self, command_history=None, style_config=None):
        # No need to store _color_picker - manager handles it
        self.command_history = command_history
        self.style_config = style_config
        self.current_shadow = {"color": "#FF000000", "offset_x": 2, "offset_y": 2, "blur": 4}
    
    def _pick_color_new(self):
        """New way: using ColorDialogManager with undo support."""
        from cogist.presentation.dialogs.style_widgets import show_color_dialog_with_undo
        from cogist.application.commands import ChangeStyleCommand
        from cogist.application.commands.change_style_command import StyleChange
        
        def create_undo_command(old_color: str, new_color: str):
            """Create undo command for shadow color change."""
            change = StyleChange(
                layer="root",  # Adjust based on current layer
                style_updates={"shadow_color": new_color}
            )
            return ChangeStyleCommand(
                style_config=self.style_config,
                changes=[change]
            )
        
        def on_color_changed(hex_color: str):
            """Apply shadow color in real-time."""
            self.current_shadow["color"] = hex_color
            self._apply_shadow()  # Real-time preview
        
        # Show color dialog with undo support
        show_color_dialog_with_undo(
            parent_widget=self,
            trigger_button=self.shadow_color_btn,
            initial_color=self.current_shadow["color"],
            on_color_changed=on_color_changed,
            layer="root",
            style_key="shadow_color",
            command_history=self.command_history,
            create_undo_command=create_undo_command,
            show_alpha=True,  # Shadow needs alpha channel
        )
        # No need to manage dialog lifecycle - manager handles it!


# ============================================================================
# Key Differences
# ============================================================================

"""
OLD APPROACH:
-------------
1. Manual dialog instance management (_color_picker)
2. Manual signal connection
3. Manual lifecycle management (WA_DeleteOnClose)
4. No undo support (or complex manual implementation)
5. Code duplication across different sections

NEW APPROACH:
-------------
1. No manual dialog management
2. Unified interface via show_color_dialog_with_undo()
3. Automatic lifecycle management
4. Built-in undo support with one line of configuration
5. Consistent behavior across all color pickers

BENEFITS:
---------
✅ Less code to maintain
✅ Automatic undo/redo support
✅ Consistent user experience
✅ Better resource management
✅ Easier to test and debug
"""


# ============================================================================
# Usage in Style Editor
# ============================================================================

class StyleEditorTabExample:
    """Example showing integration with style editor."""
    
    def __init__(self):
        from cogist.application.commands import CommandHistory
        self.command_history = CommandHistory()
        self.style_config = None  # Your MindMapStyle instance
        
        # Create sections with command history
        self.shadow_section = NewShadowSection(
            command_history=self.command_history,
            style_config=self.style_config
        )
    
    def undo(self):
        """Undo last action."""
        if self.command_history.can_undo():
            self.command_history.undo()
            self._refresh_ui()
    
    def redo(self):
        """Redo last undone action."""
        if self.command_history.can_redo():
            self.command_history.redo()
            self._refresh_ui()
    
    def _refresh_ui(self):
        """Refresh UI after undo/redo."""
        # Update all sections to reflect current state
        self.shadow_section.update_from_config(self.style_config)


# ============================================================================
# Migration Checklist
# ============================================================================

"""
To migrate existing code to ColorDialogManager:

1. [ ] Remove _color_picker instance variable
2. [ ] Remove manual dialog creation code
3. [ ] Import show_color_dialog_with_undo
4. [ ] Create undo command factory function
5. [ ] Replace old _pick_color() with new implementation
6. [ ] Pass command_history and style_config to section
7. [ ] Test undo/redo functionality
8. [ ] Remove unused imports (create_color_picker, etc.)

Estimated time per section: 10-15 minutes
"""
