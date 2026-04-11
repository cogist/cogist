"""Style system enums and constants."""

from enum import IntEnum


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
