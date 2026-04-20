"""Style system enums and constants."""

from enum import IntEnum, StrEnum


class PriorityLevel(IntEnum):
    """Node priority levels (fixed count and order)"""

    LEVEL_0 = 0  # Unimportant / Note
    LEVEL_1 = 1  # Normal (default)
    LEVEL_2 = 2  # Important / Critical

    @property
    def default_name(self) -> str:
        """Get default display name for this priority level"""
        names = {
            PriorityLevel.LEVEL_0: "Unimportant",
            PriorityLevel.LEVEL_1: "Normal",
            PriorityLevel.LEVEL_2: "Important",
        }
        return names[self]


class NodeRole(StrEnum):
    """Node roles for style assignment"""

    ROOT = "root"              # Root node / central topic
    PRIMARY = "primary"        # First level branches
    SECONDARY = "secondary"    # Second level branches
    TERTIARY = "tertiary"      # Third level and below
    LEAF = "leaf"              # Leaf nodes (no children)
    CUSTOM = "custom"          # Custom role


class SpacingLevel(StrEnum):
    """Abstract spacing levels for layout compatibility"""

    COMPACT = "compact"      # Compact spacing
    NORMAL = "normal"        # Normal spacing (default)
    RELAXED = "relaxed"      # Relaxed spacing
    SPACIOUS = "spacious"    # Spacious spacing
