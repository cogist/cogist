"""Style configuration data structures for mind map styling."""

from dataclasses import dataclass, field

from .enums import NodeRole
from .extended_styles import RoleStyle

# NOTE: MAX_TEXT_WIDTH constant removed (v0.3.6)
# Text width is now defined per-role in RoleStyle.max_text_width:
# - ROOT: 300px
# - PRIMARY: 250px
# - SECONDARY: 200px
# - TERTIARY: 0 (unlimited, no wrapping)

# Default branch colors (10 colors: indices 0-7 for branches, index 8 for canvas background, index 9 for root node)
DEFAULT_BRANCH_COLORS: list[str] = [
    "#FFFF6B6B",  # [0] Red
    "#FF4ECDC4",  # [1] Teal
    "#FF45B7D1",  # [2] Light Blue
    "#FFFFA07A",  # [3] Light Salmon
    "#FF98D8C8",  # [4] Mint
    "#FFF7DC6F",  # [5] Yellow
    "#FFBB8FCE",  # [6] Purple
    "#FF85C1E2",  # [7] Sky Blue
    "#FFFFFFFF",  # [8] Canvas Background (White)
    "#FF2D3436",  # [9] Root Node Background (Dark Gray)
]


@dataclass
class MindMapStyle:
    """Complete mind map style configuration (NEW ARCHITECTURE).

    Self-contained style with embedded color pool and role configurations.
    No external dependencies on Template or ColorScheme.

    Attributes:
        name: Style name
        use_rainbow_branches: Enable rainbow branch mode (PRIMARY nodes cycle through colors)
        branch_colors: Color pool (9 colors: [0-7] branches, [8] canvas background)
        role_styles: Complete role-based configurations (flat structure)
    """

    name: str = "Default"

    # === Global settings ===
    use_rainbow_branches: bool = False
    branch_colors: list[str] = field(default_factory=lambda: DEFAULT_BRANCH_COLORS.copy())

    # === Role configurations (flat structure) ===
    role_styles: dict[NodeRole, RoleStyle] = field(default_factory=dict)
