# Universal Color Dialog Manager Design Document

## 📋 Overview

This document describes the **Universal Color Dialog Manager** implemented in the Cogist project. The manager provides non-modal color selection functionality with support for **one-click undo** (regardless of how many times the user adjusts colors in the dialog, pressing undo once restores the original color before opening the dialog).

## 🎯 Design Goals

1. **Unified Management** - All color selection uses a unified manager to avoid code duplication
2. **Non-modal Interaction** - Dialogs don't block UI; users can interact with other controls simultaneously
3. **Real-time Preview** - Color changes are applied immediately, providing instant feedback
4. **One-click Undo** - A single undo command is created when closing the dialog, restoring the original color
5. **Cross-platform Compatibility** - Uses qtpy compatibility layer, supporting PyQt5/6 and PySide2/6
6. **Automatic Cleanup** - Resources are automatically cleaned up when dialogs close, no manual management needed

## 🏗️ Architecture Design

### Core Components

```
ColorDialogManager (Manager)
├── show_color_dialog()          # Show color dialog
├── close_all_dialogs()          # Close all active dialogs
└── _active_dialogs              # Track active dialogs

show_color_dialog_with_undo()    # Convenience function (global singleton)
```

### Workflow

```
User clicks color button
    ↓
Call show_color_dialog_with_undo()
    ↓
Create QColorDialog (non-modal)
    ↓
Backup original color (original_color)
    ↓
User adjusts color → on_color_changed() applies in real-time
    ↓
User closes dialog
    ↓
If color has changed:
    - Create ChangeStyleCommand(old=original, new=final)
    - Execute command and push to command_history
Otherwise:
    - Don't create command
    ↓
Clean up dialog resources
```

## 💻 Usage

### Basic Usage (Without Undo)

```python
from cogist.presentation.dialogs.style_widgets import show_color_dialog_with_undo

def on_bg_color_changed(hex_color: str):
    """Apply background color in real-time."""
    role_style.bg_color = hex_color
    update_node_preview()

show_color_dialog_with_undo(
    parent_widget=self,
    trigger_button=self.bg_color_btn,
    initial_color="#FFFF0000",
    on_color_changed=on_bg_color_changed,
    show_alpha=False,
)
```

### Full Usage (With Undo Support)

```python
from cogist.presentation.dialogs.style_widgets import show_color_dialog_with_undo
from cogist.application.commands import ChangeStyleCommand
from cogist.application.commands.change_style_command import StyleChange

def create_undo_command(old_color: str, new_color: str):
    """Create undo command for color change."""
    change = StyleChange(
        layer="root",
        style_updates={"bg_color": new_color}
    )
    return ChangeStyleCommand(
        style_config=self.style_config,
        changes=[change]
    )

def on_color_changed(hex_color: str):
    """Apply color in real-time."""
    role_style.bg_color = hex_color
    apply_styles()

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
```

### With Alpha Channel (Shadow Color)

```python
show_color_dialog_with_undo(
    parent_widget=self,
    trigger_button=self.shadow_color_btn,
    initial_color=shadow_config["color"],
    on_color_changed=lambda c: apply_shadow_color(c),
    layer="root",
    style_key="shadow_color",
    command_history=self.command_history,
    create_undo_command=create_shadow_undo_command,
    show_alpha=True,  # Enable Alpha channel
)
```

## 🔄 Undo Behavior Explanation

### Scenario 1: User Selects New Color

```
Initial color: #FFFF0000 (red)
User adjusts: #FFFF0000 → #FF00FF00 → #FF0000FF
User closes dialog

Undo stack: [ChangeStyleCommand(old=#FFFF0000, new=#FF0000FF)]
Press Undo once: Restores directly to #FFFF0000 ✅
```

### Scenario 2: User Doesn't Modify Color

```
Initial color: #FFFF0000
User opens dialog, doesn't modify, closes directly

Undo stack: [] (no command added)
Press Undo: No effect ✅
```

### Scenario 3: Multiple Dialog Opens

```
1st time: #FFFF0000 → #FF00FF00  → Undo stack: [cmd1]
2nd time: #FF00FF00 → #FF0000FF  → Undo stack: [cmd1, cmd2]

Press Undo (1st time): Restores to #FF00FF00
Press Undo (2nd time): Restores to #FFFF0000
```

**Key Points**:
- ✅ Each dialog open records the original color
- ✅ Regardless of how many times the user adjusts in the dialog, undo restores to the **color before opening**
- ✅ Modifications to different properties (e.g., bg_color, text_color) create independent undo steps

## 📊 Technical Implementation Details

### 1. Color Format Handling

```python
# Supported input formats
"#RRGGBB"   → Automatically append Alpha=255 → "#FFFFRRGGBB"
"#AARRGGBB" → Use directly

# Output format (always)
QColor.name(QColor.NameFormat.HexArgb) → "#AARRGGBB"
```

### 2. Signal Connections

```python
# Real-time preview
dialog.currentColorChanged.connect(on_current_color_changed)

# Dialog closed
dialog.finished.connect(on_dialog_finished)

# Prevent initial setup from triggering signals
dialog.blockSignals(True)
dialog.setCurrentColor(qt_color)
dialog.blockSignals(False)
```

### 3. Undo Command Creation Timing

```python
def on_dialog_finished(result):
    # Only create undo command if color has changed
    if has_changes and command_history and create_undo_command:
        cmd = create_undo_command(original_color, final_color)
        cmd.execute()
        command_history.push(cmd)
```

### 4. Resource Management

```python
# No need for WA_DeleteOnClose, we track manually
# Dialog is automatically removed from _active_dialogs when closed
def on_dialog_finished(result):
    dialog_id = id(dialog)
    if dialog_id in self._active_dialogs:
        del self._active_dialogs[dialog_id]
```

## 🔧 Migration Guide

### Migrating from Old Code

**Old Code Pattern** (shadow_section.py):

```python
class OldSection:
    def __init__(self):
        self._color_picker = None  # ❌ Requires manual management
    
    def _pick_color(self):
        if self._color_picker is None:
            self._color_picker = create_color_picker(...)
            self._color_picker.color_selected.connect(self._on_color_selected)
        self._color_picker.show()
    
    def _on_color_selected(self, hex_color):
        # ❌ No undo support
        apply_color(hex_color)
```

**New Code Pattern**:

```python
class NewSection:
    def __init__(self):
        # ✅ No need to store _color_picker
    
    def _pick_color(self):
        show_color_dialog_with_undo(
            parent_widget=self,
            trigger_button=self.color_btn,
            initial_color=current_color,
            on_color_changed=lambda c: apply_color(c),
            layer="root",
            style_key="bg_color",
            command_history=self.command_history,
            create_undo_command=create_undo_cmd,
        )
        # ✅ Automatic lifecycle management and undo
```

### Migration Checklist

- [ ] Remove `_color_picker` instance variable
- [ ] Remove manual dialog creation code
- [ ] Import `show_color_dialog_with_undo`
- [ ] Create undo command factory function
- [ ] Replace old `_pick_color()` implementation
- [ ] Pass `command_history` and `style_config`
- [ ] Test undo/redo functionality
- [ ] Remove unused imports

**Estimated Time**: 10-15 minutes per section

## ✅ Advantages Summary

| Feature | Old Way | New Way |
|---------|---------|---------|
| Code Size | ~50 lines/location | ~20 lines/location |
| Undo Support | ❌ None or complex | ✅ Built-in |
| Resource Management | Manual | Automatic |
| Consistency | Different across sections | Unified interface |
| Maintainability | Low | High |
| Testability | Difficult | Simple |

## 📝 File List

### New Files

1. **color_dialog_manager.py** - Core manager implementation
2. **COLOR_DIALOG_USAGE.md** - Usage guide
3. **example_color_dialog_migration.py** - Migration examples
4. **COLOR_DIALOG_MANAGER_DESIGN.md** - This design document

### Modified Files

1. **__init__.py** - Export new manager class

### Files to Migrate (Optional)

- `shadow_section.py` - Shadow color selection
- `node_style_section.py` - Node background color selection
- `border_section.py` - Border color selection
- `connector_section.py` - Connector color selection
- `font_style_section.py` - Text color selection

## 🚀 Future Extensions

Potential features to add:

- [ ] Recently used colors list
- [ ] Custom color palettes
- [ ] Color history
- [ ] Quick color preset selection
- [ ] Color contrast checking
- [ ] Colorblind-friendly mode

## 🔗 Related Documentation

- [CHANGE_STYLE_COMMAND.md](../commands/CHANGE_STYLE_COMMAND.md) - Style change command design
- [COMMAND_HISTORY.md](../commands/COMMAND_HISTORY.md) - Command history management
- [STYLE_PANEL_ARCHITECTURE.md](../../STYLE_PANEL_ARCHITECTURE.md) - Style panel architecture

---

**Created**: 2026-05-07  
**Version**: v1.0  
**Status**: Implementation complete, pending migration of existing code
