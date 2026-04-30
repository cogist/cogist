"""
Change Style Command - Application Layer

Command to change style configuration.
Supports undo/redo functionality with coalescing for numeric values.

For numeric type style changes, only the last changed value is saved in the stack
to avoid redundant entries when the user adjusts values continuously.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from cogist.application.commands.command import Command

if TYPE_CHECKING:
    from cogist.domain.styles.style_config import MindMapStyle


# Numeric style fields that should use coalescing (only keep last value)
NUMERIC_STYLE_FIELDS = {
    # Spacing
    "parent_child_spacing",
    "sibling_spacing",
    # Node style numeric fields
    "radius",
    "padding_w",
    "padding_h",
    "max_text_width",
    "font_size",
    # Border numeric fields
    "border_width",
    "border_radius",
    # Connector numeric fields
    "line_width",
    # Shadow numeric fields
    "shadow_offset_x",
    "shadow_offset_y",
    "shadow_blur",
}


@dataclass
class StyleChange:
    """Represents a single style change."""
    layer: str  # Layer name (e.g., "root", "level_1", "canvas")
    style_updates: dict  # Style property changes


class ChangeStyleCommand(Command):
    """
    Command to change style configuration.

    This command supports coalescing for numeric values:
    - When multiple numeric changes occur for the same layer, only the last value is kept
    - This prevents the undo stack from being flooded with intermediate values

    Attributes:
        style_config: The style configuration to modify
        changes: List of style changes to apply
        old_values: Backup of old values (for undo)
    """

    def __init__(
        self,
        style_config: "MindMapStyle",
        changes: list[StyleChange],
    ):
        """
        Initialize the change style command.

        Args:
            style_config: The style configuration to modify
            changes: List of style changes to apply
        """
        self.style_config = style_config
        self.changes = changes
        self.old_values: list[dict] = []  # Backup old values for undo

    def execute(self) -> None:
        """
        Execute the command - apply style changes.

        This applies all style changes and backs up old values for undo.
        """
        self.old_values = []

        for change in self.changes:
            # Backup old values
            old_values_for_layer = self._backup_layer_style(change.layer, change.style_updates.keys())
            self.old_values.append({
                "layer": change.layer,
                "old_values": old_values_for_layer,
            })

            # Apply new values
            self._apply_layer_style(change.layer, change.style_updates)

    def undo(self) -> None:
        """
        Undo the command - restore old style values.

        This reverts the style back to what it was before the command.
        """
        for old_value_entry in reversed(self.old_values):
            layer = old_value_entry["layer"]
            old_values = old_value_entry["old_values"]
            self._restore_layer_style(layer, old_values)

    def _backup_layer_style(self, layer: str, keys: set[str]) -> dict:
        """Backup current style values for a layer.

        Args:
            layer: Layer name
            keys: Style property keys to backup

        Returns:
            Dictionary with backed up values
        """
        backup = {}

        if layer == "canvas":
            for key in keys:
                if key == "bg_color":
                    # Read from branch_colors[8]
                    if hasattr(self.style_config, 'branch_colors') and len(self.style_config.branch_colors) > 8:
                        backup[key] = self.style_config.branch_colors[8]
                    else:
                        backup[key] = "#FFFFFFFF"  # Default white
        else:
            # Check if this is a spacing or connector config change (layer-level, not role-level)
            spacing_keys = {"parent_child_spacing", "sibling_spacing"}
            connector_keys = {"connector_shape", "connector_style", "line_width", "connector_color"}

            if keys & spacing_keys:
                # Backup spacing configuration from role-based style
                # Map layer name to role
                from cogist.domain.styles.extended_styles import NodeRole

                layer_to_role = {
                    "root": NodeRole.ROOT,
                    "level_1": NodeRole.PRIMARY,
                    "level_2": NodeRole.SECONDARY,
                    "level_3_plus": NodeRole.TERTIARY,
                    "critical": NodeRole.TERTIARY,
                    "minor": NodeRole.TERTIARY,
                }
                role = layer_to_role.get(layer)

                if role and self.style_config.resolved_template and role in self.style_config.resolved_template.role_styles:
                    role_style = self.style_config.resolved_template.role_styles[role]
                    backup["parent_child_spacing"] = role_style.parent_child_spacing
                    backup["sibling_spacing"] = role_style.sibling_spacing
            elif keys & connector_keys:
                # Backup connector configuration from role-based style
                from cogist.domain.styles.extended_styles import NodeRole

                layer_to_role = {
                    "root": NodeRole.ROOT,
                    "level_1": NodeRole.PRIMARY,
                    "level_2": NodeRole.SECONDARY,
                    "level_3_plus": NodeRole.TERTIARY,
                    "critical": NodeRole.TERTIARY,
                    "minor": NodeRole.TERTIARY,
                }
                role = layer_to_role.get(layer)

                if role and self.style_config.resolved_template and role in self.style_config.resolved_template.role_styles:
                    role_style = self.style_config.resolved_template.role_styles[role]
                    backup["connector_shape"] = role_style.connector_shape
                    backup["connector_style"] = role_style.connector_style
                    backup["line_width"] = role_style.line_width
                    backup["connector_color"] = role_style.connector_color
            else:
                # For node layers, access the resolved template
                if self.style_config.resolved_template:
                    from cogist.domain.styles import NodeRole

                    # Map layer name to role
                    layer_to_role = {
                        "root": "root",
                        "level_1": "primary",
                        "level_2": "secondary",
                        "level_3_plus": "tertiary",
                        "critical": "tertiary",
                        "minor": "tertiary",
                    }

                    role_str = layer_to_role.get(layer)
                    if role_str:
                        role = NodeRole(role_str)
                        if role in self.style_config.resolved_template.role_styles:
                            role_style = self.style_config.resolved_template.role_styles[role]

                            for key in keys:
                                if key == "shape":
                                    # Backup shape type
                                    if hasattr(role_style, 'shape'):
                                        backup[key] = role_style.shape.basic_shape
                                elif key == "radius":
                                    # Backup border radius
                                    if hasattr(role_style, 'shape'):
                                        backup[key] = role_style.shape.border_radius
                                elif key == "bg_color":
                                    # Background color from role_configs
                                    if self.style_config.resolved_color_scheme:
                                        backup[key] = self.style_config.resolved_color_scheme.role_configs[role].bg_color
                                elif key == "text_color":
                                    # Text color from role_configs
                                    if self.style_config.resolved_color_scheme:
                                        backup[key] = self.style_config.resolved_color_scheme.role_configs[role].text_color
                                elif key == "border_color":
                                    # Border color from role_configs
                                    if self.style_config.resolved_color_scheme:
                                        backup[key] = self.style_config.resolved_color_scheme.role_configs[role].border_color
                                elif key == "font_italic":
                                    # Direct boolean backup
                                    if hasattr(role_style, 'font_italic'):
                                        backup[key] = role_style.font_italic
                                elif key.startswith("border_") and hasattr(role_style, 'border'):
                                    # Backup border attributes from border object
                                    border_attr = key
                                    if hasattr(role_style.border, border_attr):
                                        backup[key] = getattr(role_style.border, border_attr)
                                elif hasattr(role_style, key):
                                    backup[key] = getattr(role_style, key)

        return backup

    def _apply_layer_style(self, layer: str, style_updates: dict) -> None:
        """Apply style updates to a layer.

        Args:
            layer: Layer name
            style_updates: Dictionary of style properties to update
        """
        if layer == "canvas":
            if "bg_color" in style_updates and hasattr(self.style_config, 'branch_colors'):
                # Update branch_colors[8]
                while len(self.style_config.branch_colors) < 9:
                    self.style_config.branch_colors.append("#FFFFFFFF")
                self.style_config.branch_colors[8] = style_updates["bg_color"]
        else:
            # Check if this is a spacing or connector config change (layer-level, not role-level)
            spacing_keys = {"parent_child_spacing", "sibling_spacing"}
            connector_keys = {"connector_shape", "connector_style", "line_width", "connector_color"}

            if style_updates.keys() & spacing_keys:
                # Apply spacing configuration to role-based style
                from cogist.domain.styles.extended_styles import NodeRole

                layer_to_role = {
                    "root": NodeRole.ROOT,
                    "level_1": NodeRole.PRIMARY,
                    "level_2": NodeRole.SECONDARY,
                    "level_3_plus": NodeRole.TERTIARY,
                    "critical": NodeRole.TERTIARY,
                    "minor": NodeRole.TERTIARY,
                }
                role = layer_to_role.get(layer)

                if role and self.style_config.resolved_template and role in self.style_config.resolved_template.role_styles:
                    role_style = self.style_config.resolved_template.role_styles[role]

                    if "parent_child_spacing" in style_updates:
                        role_style.parent_child_spacing = style_updates["parent_child_spacing"]
                    if "sibling_spacing" in style_updates:
                        role_style.sibling_spacing = style_updates["sibling_spacing"]
            elif style_updates.keys() & connector_keys:
                # Apply connector configuration to role-based style
                from cogist.domain.styles.extended_styles import NodeRole

                layer_to_role = {
                    "root": NodeRole.ROOT,
                    "level_1": NodeRole.PRIMARY,
                    "level_2": NodeRole.SECONDARY,
                    "level_3_plus": NodeRole.TERTIARY,
                    "critical": NodeRole.TERTIARY,
                    "minor": NodeRole.TERTIARY,
                }
                role = layer_to_role.get(layer)

                if role and self.style_config.resolved_template and role in self.style_config.resolved_template.role_styles:
                    role_style = self.style_config.resolved_template.role_styles[role]

                    if "connector_shape" in style_updates:
                        role_style.connector_shape = style_updates["connector_shape"]
                    if "connector_style" in style_updates:
                        role_style.connector_style = style_updates["connector_style"]
                    if "line_width" in style_updates:
                        role_style.line_width = style_updates["line_width"]
                    if "connector_color" in style_updates:
                        role_style.connector_color = style_updates["connector_color"]
            else:
                # For node layers, access the resolved template
                if self.style_config.resolved_template:
                    from cogist.domain.styles import NodeRole

                    # Map layer name to role
                    layer_to_role = {
                        "root": "root",
                        "level_1": "primary",
                        "level_2": "secondary",
                        "level_3_plus": "tertiary",
                        "critical": "tertiary",
                        "minor": "tertiary",
                    }

                    role_str = layer_to_role.get(layer)
                    if role_str:
                        role = NodeRole(role_str)
                        if role in self.style_config.resolved_template.role_styles:
                            role_style = self.style_config.resolved_template.role_styles[role]

                            for key, value in style_updates.items():
                                if key == "shape":
                                    # Handle shape type update
                                    if hasattr(role_style, 'shape'):
                                        role_style.shape.basic_shape = value
                                elif key == "radius":
                                    # Handle border radius update
                                    if hasattr(role_style, 'shape'):
                                        role_style.shape.border_radius = value
                                elif key == "bg_color":
                                    # Background color goes to role_configs
                                    if self.style_config.resolved_color_scheme:
                                        self.style_config.resolved_color_scheme.role_configs[role].bg_color = value
                                elif key == "text_color":
                                    # Text color goes to role_configs
                                    if self.style_config.resolved_color_scheme:
                                        self.style_config.resolved_color_scheme.role_configs[role].text_color = value
                                elif key == "border_color":
                                    # Border color goes to role_configs
                                    if self.style_config.resolved_color_scheme:
                                        self.style_config.resolved_color_scheme.role_configs[role].border_color = value
                                elif key == "font_italic":
                                    # Direct boolean assignment
                                    if hasattr(role_style, 'font_italic'):
                                        role_style.font_italic = value
                                elif key.startswith("border_") and hasattr(role_style, 'border'):
                                    # Apply border attributes to border object
                                    border_attr = key
                                    if hasattr(role_style.border, border_attr):
                                        setattr(role_style.border, border_attr, value)
                                elif hasattr(role_style, key):
                                    # Direct attribute update (includes shadow_enabled, shadow_offset_x, etc.)
                                    setattr(role_style, key, value)

    def _restore_layer_style(self, layer: str, old_values: dict) -> None:
        """Restore old style values for a layer.

        Args:
            layer: Layer name
            old_values: Dictionary of old values to restore
        """
        self._apply_layer_style(layer, old_values)

    def should_coalesce_with(self, other: "ChangeStyleCommand") -> bool:
        """Check if this command should be coalesced with another command.

        Coalescing is applied when:
        - Both commands affect the same layer
        - Both commands have at least one common numeric style field
        - The other command was the most recent command

        Args:
            other: Another ChangeStyleCommand to check

        Returns:
            True if commands should be coalesced
        """
        if not isinstance(other, ChangeStyleCommand):
            return False

        # Must have exactly one change each
        if len(self.changes) != 1 or len(other.changes) != 1:
            return False

        # Must be the same layer
        if self.changes[0].layer != other.changes[0].layer:
            return False

        # CRITICAL: Only coalesce if both commands have EXACTLY the same keys
        # This ensures that adjusting a slider (same field repeatedly) gets coalesced,
        # but changing different properties (bg_color, then text_color) creates separate undo steps
        self_keys = set(self.changes[0].style_updates.keys())
        other_keys = set(other.changes[0].style_updates.keys())
        if self_keys != other_keys:
            return False

        # Check if there's at least one common numeric field
        self_numeric_fields = self_keys & NUMERIC_STYLE_FIELDS
        other_numeric_fields = other_keys & NUMERIC_STYLE_FIELDS

        # If both have numeric fields and they overlap, allow coalescing
        return bool(self_numeric_fields & other_numeric_fields)

    def merge_with(self, other: "ChangeStyleCommand") -> None:
        """Merge another command into this command (for coalescing).

        This replaces the current values with the newer values from the other command.

        Args:
            other: The newer command to merge into this one
        """
        # Update style updates with newer values
        self.changes[0].style_updates.update(other.changes[0].style_updates)

        # Keep our old values (the original state before any changes)
        # Don't update old_values - we want to undo to the original state
