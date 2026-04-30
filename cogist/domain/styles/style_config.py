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

    # === Runtime resolved styles (computed by resolve_style()) ===
    resolved_template: Template | None = None
    resolved_color_scheme: ColorScheme | None = None

    # === Global settings ===
    canvas_bg_color: str = "#FFFFFFFF"  # Canvas background color
    use_rainbow_branches: bool = False  # Enable rainbow branch mode
