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
    # Per-depth spacing
    "level_spacing_by_depth",
    "sibling_spacing_by_depth",
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
                    backup[key] = self.style_config.canvas_bg_color
                    # Also backup resolved_color_scheme if it exists
                    if self.style_config.resolved_color_scheme:
                        backup["resolved_canvas_bg_color"] = (
                            self.style_config.resolved_color_scheme.canvas_bg_color
                        )
        else:
            # Check if this is a spacing or connector config change (layer-level, not role-level)
            spacing_keys = {"parent_child_spacing", "sibling_spacing"}
            connector_keys = {"connector_shape", "connector_style", "line_width", "color"}

            if keys & spacing_keys:
                # Backup spacing configuration for the current layer's depth
                # Map layer name to depth
                layer_to_depth = {
                    "root": 0,
                    "level_1": 1,
                    "level_2": 2,
                    "level_3_plus": 3,
                    "critical": 3,
                    "minor": 3,
                }
                depth = layer_to_depth.get(layer, 2)

                # For level_3_plus, we need to backup all depths >= 3
                if layer == "level_3_plus":
                    all_depths = set()
                    if hasattr(self.style_config, 'level_spacing_by_depth'):
                        all_depths.update(self.style_config.level_spacing_by_depth.keys())
                    if hasattr(self.style_config, 'sibling_spacing_by_depth'):
                        all_depths.update(self.style_config.sibling_spacing_by_depth.keys())
                    depths_to_backup = [d for d in all_depths if d >= 3]
                    if not depths_to_backup:
                        depths_to_backup = [3]
                else:
                    depths_to_backup = [depth]

                # Backup spacing values for all target depths
                backup["spacing_depths"] = {}
                for d in depths_to_backup:
                    parent_child_val = self.style_config.level_spacing_by_depth.get(d) if hasattr(self.style_config, 'level_spacing_by_depth') else None
                    sibling_val = self.style_config.sibling_spacing_by_depth.get(d) if hasattr(self.style_config, 'sibling_spacing_by_depth') else None
                    backup["spacing_depths"][d] = {
                        "parent_child": parent_child_val,
                        "sibling": sibling_val,
                    }
            elif keys & connector_keys:
                # Backup connector configuration for the current depth
                # Map layer name to depth
                layer_to_depth = {
                    "root": 0,
                    "level_1": 1,
                    "level_2": 2,
                    "level_3_plus": 3,
                    "critical": 3,
                    "minor": 3,
                }
                depth = layer_to_depth.get(layer, 2)

                # For level_3_plus, we need to backup all depths >= 3
                if layer == "level_3_plus":
                    all_depths = set(self.style_config.connector_config_by_depth.keys())
                    depths_to_backup = [d for d in all_depths if d >= 3]
                    if not depths_to_backup:
                        depths_to_backup = [3]
                else:
                    depths_to_backup = [depth]

                backup["connector_depths"] = {}
                for d in depths_to_backup:
                    connector_config = self.style_config.connector_config_by_depth.get(d, {})
                    backup["connector_depths"][d] = dict(connector_config)  # Deep copy

                    # Backup specific fields that are being changed
                    for key in keys & connector_keys:
                        if key == "color":
                            backup[f"connector_{d}_color"] = connector_config.get("color")
                        else:
                            backup[f"connector_{d}_{key}"] = connector_config.get(key)
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
                                    # Background color from color_scheme
                                    if self.style_config.resolved_color_scheme:
                                        backup[key] = self.style_config.resolved_color_scheme.node_colors.get(role)
                                elif key == "text_color":
                                    # Text color from color_scheme
                                    if self.style_config.resolved_color_scheme and self.style_config.resolved_color_scheme.text_colors:
                                        backup[key] = self.style_config.resolved_color_scheme.text_colors.get(role)
                                elif key == "border_color":
                                    # Border color from color_scheme
                                    if self.style_config.resolved_color_scheme and self.style_config.resolved_color_scheme.border_colors:
                                        backup[key] = self.style_config.resolved_color_scheme.border_colors.get(role)
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
            if "bg_color" in style_updates:
                self.style_config.canvas_bg_color = style_updates["bg_color"]
            # Also restore resolved_color_scheme if it was backed up
            if "resolved_canvas_bg_color" in style_updates:
                if self.style_config.resolved_color_scheme:
                    self.style_config.resolved_color_scheme.canvas_bg_color = (
                        style_updates["resolved_canvas_bg_color"]
                    )
            # Sync canvas_bg_color to resolved_color_scheme if only bg_color is present
            elif "bg_color" in style_updates and self.style_config.resolved_color_scheme:
                self.style_config.resolved_color_scheme.canvas_bg_color = (
                    style_updates["bg_color"]
                )
        else:
            # Check if this is a spacing or connector config change (layer-level, not role-level)
            spacing_keys = {"parent_child_spacing", "sibling_spacing"}
            connector_keys = {"connector_shape", "connector_style", "line_width", "color"}

            if style_updates.keys() & spacing_keys:
                # Apply spacing configuration for the current layer's depth
                # Map layer name to depth
                layer_to_depth = {
                    "root": 0,
                    "level_1": 1,
                    "level_2": 2,
                    "level_3_plus": 3,
                    "critical": 3,
                    "minor": 3,
                }
                depth = layer_to_depth.get(layer, 2)

                # For level_3_plus, we need to update all depths >= 3
                if layer == "level_3_plus":
                    all_depths = set()
                    if hasattr(self.style_config, 'level_spacing_by_depth'):
                        all_depths.update(self.style_config.level_spacing_by_depth.keys())
                    if hasattr(self.style_config, 'sibling_spacing_by_depth'):
                        all_depths.update(self.style_config.sibling_spacing_by_depth.keys())
                    depths_to_update = [d for d in all_depths if d >= 3]
                    if not depths_to_update:
                        depths_to_update = [3]
                else:
                    depths_to_update = [depth]

                # Ensure dictionaries exist
                if not hasattr(self.style_config, 'level_spacing_by_depth'):
                    self.style_config.level_spacing_by_depth = {}
                if not hasattr(self.style_config, 'sibling_spacing_by_depth'):
                    self.style_config.sibling_spacing_by_depth = {}

                # Update spacing for all target depths
                if "parent_child_spacing" in style_updates:
                    for d in depths_to_update:
                        self.style_config.level_spacing_by_depth[d] = style_updates["parent_child_spacing"]
                if "sibling_spacing" in style_updates:
                    for d in depths_to_update:
                        self.style_config.sibling_spacing_by_depth[d] = style_updates["sibling_spacing"]

                # Handle backup format (spacing_depths)
                if "spacing_depths" in style_updates:
                    for d, values in style_updates["spacing_depths"].items():
                        if values["parent_child"] is not None:
                            self.style_config.level_spacing_by_depth[d] = values["parent_child"]
                        if values["sibling"] is not None:
                            self.style_config.sibling_spacing_by_depth[d] = values["sibling"]
            elif style_updates.keys() & connector_keys:
                # Apply connector configuration for the current depth
                # Map layer name to depth
                layer_to_depth = {
                    "root": 0,
                    "level_1": 1,
                    "level_2": 2,
                    "level_3_plus": 3,
                    "critical": 3,
                    "minor": 3,
                }
                depth = layer_to_depth.get(layer, 2)

                # For level_3_plus, we need to update all depths >= 3
                if layer == "level_3_plus":
                    all_depths = set(self.style_config.connector_config_by_depth.keys())
                    depths_to_update = [d for d in all_depths if d >= 3]
                    if not depths_to_update:
                        depths_to_update = [3]
                else:
                    depths_to_update = [depth]

                # Update connector config for all target depths
                for d in depths_to_update:
                    connector_config = self.style_config.connector_config_by_depth.get(d, {})
                    self.style_config.connector_config_by_depth[d] = connector_config

                    # Update connector config
                    if "connector_shape" in style_updates:
                        connector_config["connector_shape"] = style_updates["connector_shape"]
                    if "connector_style" in style_updates:
                        connector_config["connector_style"] = style_updates["connector_style"]
                    if "line_width" in style_updates:
                        connector_config["line_width"] = style_updates["line_width"]
                    if "color" in style_updates:
                        connector_config["color"] = style_updates["color"]
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
                                    # Background color goes to color_scheme
                                    if self.style_config.resolved_color_scheme:
                                        self.style_config.resolved_color_scheme.node_colors[role] = value
                                elif key == "text_color":
                                    # Text color goes to color_scheme
                                    if self.style_config.resolved_color_scheme:
                                        if not self.style_config.resolved_color_scheme.text_colors:
                                            self.style_config.resolved_color_scheme.text_colors = {}
                                        self.style_config.resolved_color_scheme.text_colors[role] = value
                                elif key == "border_color":
                                    # Border color goes to color_scheme
                                    if self.style_config.resolved_color_scheme:
                                        if not self.style_config.resolved_color_scheme.border_colors:
                                            self.style_config.resolved_color_scheme.border_colors = {}
                                        self.style_config.resolved_color_scheme.border_colors[role] = value
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

        # Check if there's at least one common numeric field
        self_numeric_fields = set(self.changes[0].style_updates.keys()) & NUMERIC_STYLE_FIELDS
        other_numeric_fields = set(other.changes[0].style_updates.keys()) & NUMERIC_STYLE_FIELDS

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
