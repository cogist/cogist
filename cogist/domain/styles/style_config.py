"""Style configuration data structures for mind map styling."""

from dataclasses import dataclass, field

from .extended_styles import ColorScheme, Template

# NOTE: MAX_TEXT_WIDTH constant removed (v0.3.6)
# Text width is now defined per-role in RoleBasedStyle.max_text_width:
# - ROOT: 300px
# - PRIMARY: 250px
# - SECONDARY: 200px
# - TERTIARY: 0 (unlimited, no wrapping)


@dataclass
class MindMapStyle:
    """Complete mind map style configuration (new architecture).

    Template and ColorScheme are saved separately in independent files.
    This is the ONLY authoritative style system - no legacy fields.
    """

    name: str = "Default"

    # === Spacing configuration (pixel values) ===
    parent_child_spacing: float = field(default=0.0)  # Must be set in create_default_template()
    sibling_spacing: float = field(default=0.0)       # Must be set in create_default_template()

    # === Per-depth spacing configuration (for true layer isolation) ===
    # NOTE: All initialization should happen in create_default_template(), not here
    level_spacing_by_depth: dict[int, float] = field(default_factory=dict)
    sibling_spacing_by_depth: dict[int, float] = field(default_factory=dict)

    # === Per-depth connector configuration (for layer-specific edge styles) ===
    # NOTE: All initialization should happen in create_default_template(), not here
    connector_config_by_depth: dict[int, dict] = field(default_factory=dict)

    # === Per-depth text constraints (for layer-specific max text width) ===
    # NOTE: All initialization should happen in create_default_template(), not here
    max_text_width_by_depth: dict[int, float] = field(default_factory=dict)

    # === Runtime resolved styles (computed by resolve_style()) ===
    resolved_template: Template | None = None
    resolved_color_scheme: ColorScheme | None = None

    # === Canvas background (synced from color_scheme) ===
    canvas_bg_color: str = "#FFFFFF"
