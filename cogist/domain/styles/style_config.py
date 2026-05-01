"""Style configuration data structures for mind map styling."""

from dataclasses import dataclass

from .enums import NodeRole
from .extended_styles import RoleStyle

# NOTE: MAX_TEXT_WIDTH constant removed (v0.3.6)
# Text width is now defined per-role in RoleStyle.max_text_width:
# - ROOT: 300px
# - PRIMARY: 250px
# - SECONDARY: 200px
# - TERTIARY: 0 (unlimited, no wrapping)

# NOTE: Default branch colors are now loaded from assets/color_schemes/default.json
# This constant is kept for backward compatibility but should not be used in new code.
# The color scheme loader will override this during initialization.
DEFAULT_BRANCH_COLORS: list[str] = []


@dataclass
class MindMapStyle:
    """Complete mind map style configuration (NEW ARCHITECTURE).

    Self-contained style with embedded color pool and role configurations.
    No external dependencies on Template or ColorScheme.

    IMPORTANT: NO hardcoded default values! All defaults must come from template files.

    Attributes:
        name: Style name
        use_rainbow_branches: Enable rainbow branch mode (PRIMARY nodes cycle through colors)
        color_pool: Color pool (8 branch colors + special colors like canvas_bg, root_background, etc.)
                   Loaded from color scheme JSON file during initialization
        special_colors: Special role colors dictionary (canvas_bg, root_background, etc.)
        role_styles: Complete role-based configurations (flat structure)
    """

    name: str

    # === Global settings ===
    use_rainbow_branches: bool
    color_pool: list[str]
    special_colors: dict[str, str]

    # === Role configurations (flat structure) ===
    role_styles: dict[NodeRole, RoleStyle]
