# Color Dialog Manager Usage Guide

## Overview

`ColorDialogManager` provides a unified non-modal color dialog management solution with real-time preview and one-click undo functionality.

## Core Features

1. **Non-modal Dialogs** - Don't block UI; users can interact with other controls simultaneously
2. **Real-time Preview** - Color changes are applied immediately
3. **One-click Undo** - Automatically creates an undo command when closing the dialog, restoring to original color with one undo
4. **Cross-platform Compatible** - Uses qtpy compatibility layer, supporting PyQt5/6 and PySide2/6
5. **Automatic Cleanup** - Dialog resources are automatically cleaned up when closed

## Basic Usage

### Simple Example (Without Undo)

```python
from cogist.presentation.dialogs.style_widgets.color_dialog_manager import (
    show_color_dialog_with_undo
)

def on_bg_color_changed(hex_color: str):
    """Apply background color in real-time."""
    role_style.bg_color = hex_color
    update_node_preview()

# Show color dialog
show_color_dialog_with_undo(
    parent_widget=self,
    trigger_button=self.bg_color_btn,
    initial_color="#FFFF0000",
    on_color_changed=on_bg_color_changed,
    show_alpha=False,
)
```

### Full Example (With Undo Support)

```python
from cogist.application.commands import ChangeStyleCommand
from cogist.application.commands.change_style_command import StyleChange
from cogist.presentation.dialogs.style_widgets.color_dialog_manager import (
    show_color_dialog_with_undo
)

def create_bg_color_undo_command(old_color: str, new_color: str) -> ChangeStyleCommand:
    """Create undo command for background color change."""
    change = StyleChange(
        layer="root",  # or "level_1", "level_2", etc.
        style_updates={"bg_color": new_color}
    )
    return ChangeStyleCommand(
        style_config=self.style_config,
        changes=[change]
    )

def on_bg_color_changed(hex_color: str):
    """Apply background color in real-time."""
    role_style.bg_color = hex_color
    update_node_preview()

# Show color dialog with undo support
show_color_dialog_with_undo(
    parent_widget=self,
    trigger_button=self.bg_color_btn,
    initial_color=role_style.bg_color,
    on_color_changed=on_bg_color_changed,
    layer="root",
    style_key="bg_color",
    command_history=self.command_history,
    create_undo_command=create_bg_color_undo_command,
    show_alpha=False,
)
```

### Example with Alpha Channel (Shadow Color)

```python
def create_shadow_color_undo_command(old_color: str, new_color: str) -> ChangeStyleCommand:
    """Create undo command for shadow color change."""
    change = StyleChange(
        layer="root",
        style_updates={"shadow_color": new_color}
    )
    return ChangeStyleCommand(
        style_config=self.style_config,
        changes=[change]
    )

def on_shadow_color_changed(hex_color: str):
    """Apply shadow color in real-time."""
    shadow_config["color"] = hex_color
    update_shadow_preview()

# Show color dialog with alpha channel
show_color_dialog_with_undo(
    parent_widget=self,
    trigger_button=self.shadow_color_btn,
    initial_color=shadow_config["color"],
    on_color_changed=on_shadow_color_changed,
    layer="root",
    style_key="shadow_color",
    command_history=self.command_history,
    create_undo_command=create_shadow_color_undo_command,
    show_alpha=True,  # Enable alpha channel
)
```

## Parameter Description

### show_color_dialog_with_undo()

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `parent_widget` | QWidget | ✅ | Parent widget for dialog lifecycle management |
| `trigger_button` | QPushButton | ✅ | Trigger button for dialog positioning |
| `initial_color` | str | ✅ | Initial color (#RRGGBB or #AARRGGBB format) |
| `on_color_changed` | Callable[[str], None] | ✅ | Color change callback (receives hex color string) |
| `layer` | str | ❌ | Layer name (for undo command) |
| `style_key` | str | ❌ | Style property key (for undo command) |
| `command_history` | CommandHistory | ❌ | Command history manager (enables undo support) |
| `create_undo_command` | Callable | ❌ | Factory function to create undo commands |
| `show_alpha` | bool | ❌ | Whether to show Alpha channel (default False) |

### create_undo_command Signature

```python
def create_undo_command(old_color: str, new_color: str) -> Command:
    """
    Create an undo command for color change.
    
    Args:
        old_color: Original color before changes (#AARRGGBB format)
        new_color: Final color after user selection (#AARRGGBB format)
    
    Returns:
        Command instance that can be executed/undone
    """
    pass
```

## Undo Behavior Explanation

### Scenario 1: User Selects New Color and Closes Dialog

```
Initial color: #FFFF0000 (red)
User adjusts to: #FF00FF00 (green)
User closes dialog

Undo stack: [ChangeStyleCommand(old=#FFFF0000, new=#FF00FF00)]
Press Undo once: Restores to #FFFF0000
```

### Scenario 2: User Opens Dialog but Doesn't Modify Color

```
Initial color: #FFFF0000
User opens dialog, makes no changes, closes directly

Undo stack: [] (no command added)
Press Undo: No effect
```

### Scenario 3: User Adjusts Color Multiple Times

```
Initial color: #FFFF0000
User adjusts: #FFFF0000 → #FF00FF00 → #FF0000FF
User closes dialog

Undo stack: [ChangeStyleCommand(old=#FFFF0000, new=#FF0000FF)]
Press Undo once: Directly restores to #FFFF0000 (not intermediate states)
```

**Key Point**: Regardless of how many times the user adjusts colors in the dialog, undo will directly restore to the **original color before opening the dialog**.

## Migrating Existing Code

### Migrating from Old Approach

**Old Code** (implementation in node_style_section.py):

```python
def _pick_bg_color(self):
    # Create or reuse color picker
    if self._color_picker is None or not isalive(self._color_picker):
        self._color_picker = create_color_picker(top_level)
        self._color_picker.color_selected.connect(self._on_bg_color_selected)
        self._color_picker.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
    
    self._color_picker.set_current_color(current_color)
    self._color_picker.show()
    position_color_dialog(self._color_picker, self.bg_color_btn)

def _on_bg_color_selected(self, hex_color: str):
    # Apply color directly (no undo support)
    role_style.bg_color = hex_color
    apply_styles()
```

**New Code** (using ColorDialogManager):

```python
from cogist.presentation.dialogs.style_widgets.color_dialog_manager import (
    show_color_dialog_with_undo
)

def _pick_bg_color(self):
    def create_undo_command(old_color: str, new_color: str):
        from cogist.application.commands import ChangeStyleCommand
        from cogist.application.commands.change_style_command import StyleChange
        
        change = StyleChange(
            layer="root",
            style_updates={"bg_color": new_color}
        )
        return ChangeStyleCommand(
            style_config=self.style_config,
            changes=[change]
        )
    
    def on_color_changed(hex_color: str):
        # Real-time preview
        role_style.bg_color = hex_color
        self._apply_styles_to_mindmap()
    
    show_color_dialog_with_undo(
        parent_widget=self,
        trigger_button=self.bg_color_btn,
        initial_color=role_style.bg_color,
        on_color_changed=on_color_changed,
        layer="root",
        style_key="bg_color",
        command_history=self.command_history,
        create_undo_command=create_undo_command,
        show_alpha=False,
    )
    # No need to store _color_picker - manager handles lifecycle
```

## Advantages

✅ **Unified Interface** - All color selection uses the same manager  
✅ **Automatic Undo** - No manual undo command creation needed  
✅ **Real-time Preview** - Better user experience  
✅ **Resource Management** - Automatic dialog instance cleanup  
✅ **Easy to Maintain** - Centralized color dialog logic  

## Notes

1. **Color Format** - Always use `#AARRGGBB` or `#RRGGBB` format
2. **Callback Function** - `on_color_changed` is called frequently (every color change), ensure good performance
3. **Undo Commands** - If providing `command_history`, you must also provide `create_undo_command`
4. **Dialog Reuse** - Each call creates a new dialog; don't attempt to reuse

## Future Extensions

Potential features to add:
- [ ] Recently used colors list
- [ ] Custom color palettes
- [ ] Color history
- [ ] Quick color preset selection
