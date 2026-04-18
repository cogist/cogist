"""Node templates - Domain Layer

Defines node template data structures for consistent visual styling.
Templates define geometric properties only, independent of colors and layouts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class NodeShape(Enum):
    """Node shape types"""
    ROUNDED_RECT = "rounded_rect"
    CIRCLE = "circle"
    RECTANGLE = "rectangle"
    NONE = "none"  # No visible border/background


@dataclass
class PriorityRule:
    """Priority rule for node styling overrides
    
    Defines how nodes with different priority levels should be styled.
    These are relative adjustments to the base template style.
    """
    # Border adjustments
    border_width_override: int | None = None  # Absolute override
    border_width_delta: int = 0  # Relative adjustment

    # Font adjustments
    font_weight_override: str | None = None  # "normal", "bold", etc.
    font_size_delta: int = 0  # Points to add/subtract

    # Visual indicators
    icon: str | None = None  # Emoji or symbol prefix
    badge: str | None = None  # Badge text (e.g., "P1", "HIGH")

    # Color adjustments (relative to theme)
    brightness_delta: float = 0.0  # -1.0 to 1.0 (darker to lighter)


@dataclass
class NodeTemplate:
    """Node template definition (geometric properties only)
    
    Templates define the visual appearance of nodes without specifying colors.
    Colors are provided by ColorTheme separately.
    
    Attributes:
        name: Template identifier (e.g., "modern", "minimal")
        shape: Node shape type
        corner_radius: Radius for rounded corners (pixels)
        border_width: Border thickness (pixels)
        padding: Internal spacing (pixels)
        min_width: Minimum node width (pixels)
        min_height: Minimum node height (pixels)
        recommended_layouts: Suggested layout algorithms for this template
        priority_rules: Custom priority styling rules (optional)
    """
    name: str
    shape: NodeShape = NodeShape.ROUNDED_RECT

    # Geometric properties
    corner_radius: int = 8
    border_width: int = 2
    padding: int = 12
    min_width: int = 60
    min_height: int = 30

    # Layout recommendations
    recommended_layouts: list[str] = field(default_factory=list)

    # Priority rules (template-specific overrides)
    priority_rules: dict[str, PriorityRule] = field(default_factory=dict)

    def get_priority_rule(self, priority: str) -> PriorityRule | None:
        """Get priority rule for a specific priority level
        
        Args:
            priority: Priority level (e.g., "critical", "normal", "low")
        
        Returns:
            PriorityRule if defined, None otherwise
        """
        return self.priority_rules.get(priority)


# === Preset Templates ===

MODERN_TEMPLATE = NodeTemplate(
    name="modern",
    shape=NodeShape.ROUNDED_RECT,
    corner_radius=8,
    border_width=2,
    padding=12,
    recommended_layouts=["default", "tree"],
    priority_rules={
        "critical": PriorityRule(
            border_width_delta=2,
            font_weight_override="bold",
            icon="⚠️",
            badge="P1",
        ),
        "low": PriorityRule(
            border_width_delta=-1,
            brightness_delta=-0.2,
        ),
    },
)
"""Modern template with rounded corners and clean borders"""


MINIMAL_TEMPLATE = NodeTemplate(
    name="minimal",
    shape=NodeShape.ROUNDED_RECT,
    corner_radius=4,
    border_width=1,
    padding=10,
    recommended_layouts=["default", "radial"],
)
"""Minimal template with subtle borders"""


COLORFUL_TEMPLATE = NodeTemplate(
    name="colorful",
    shape=NodeShape.CIRCLE,
    corner_radius=0,  # Not used for circles
    border_width=3,
    padding=15,
    recommended_layouts=["radial", "tree"],
    priority_rules={
        "critical": PriorityRule(
            border_width_delta=2,
            icon="🔥",
        ),
    },
)
"""Colorful template with circular nodes"""


PROFESSIONAL_TEMPLATE = NodeTemplate(
    name="professional",
    shape=NodeShape.RECTANGLE,
    corner_radius=0,
    border_width=2,
    padding=14,
    min_width=80,
    recommended_layouts=["default", "left_to_right"],
    priority_rules={
        "critical": PriorityRule(
            border_width_override=4,
            font_weight_override="bold",
            badge="HIGH",
        ),
    },
)
"""Professional template with rectangular nodes"""


# Template registry
NODE_TEMPLATES: dict[str, NodeTemplate] = {
    "modern": MODERN_TEMPLATE,
    "minimal": MINIMAL_TEMPLATE,
    "colorful": COLORFUL_TEMPLATE,
    "professional": PROFESSIONAL_TEMPLATE,
}
"""Registry of all available node templates"""
