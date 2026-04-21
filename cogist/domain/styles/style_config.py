"""Style configuration data structures for mind map styling."""

from dataclasses import dataclass, field

from .extended_styles import ColorScheme, Template

# Global constant for maximum text width across all node levels
MAX_TEXT_WIDTH = 250.0


@dataclass
class LegacyEdgeConfig:
    """Legacy edge style configuration (used for backward compatibility with main.py)."""

    connector_type: str = "bezier"  # straight, orthogonal, bezier
    connector_style: str = "solid"  # solid, dashed, dotted
    start_width: float = 6.0  # Width at source node
    end_width: float = 2.0    # Width at target node
    color: str = "#666666"


@dataclass
class MindMapStyle:
    """Complete mind map style configuration (new architecture).

    Uses template and color scheme references instead of embedded styles.
    This is the ONLY authoritative style system - no legacy fields.
    """

    name: str = "Default"

    # === Template and ColorScheme references (authoritative) ===
    template_name: str = "default"
    color_scheme_name: str = "default"

    # === Spacing configuration (pixel values) ===
    parent_child_spacing: float = 80.0  # Horizontal spacing between parent and child
    sibling_spacing: float = 60.0       # Vertical spacing between siblings

    # === Per-depth spacing configuration (for true layer isolation) ===
    level_spacing_by_depth: dict[int, float] = field(default_factory=lambda: {
        0: 80.0,   # Root → Level 1
        1: 60.0,   # Level 1 → Level 2
        2: 40.0,   # Level 2+
    })
    sibling_spacing_by_depth: dict[int, float] = field(default_factory=lambda: {
        0: 60.0,   # Level 1 siblings
        1: 45.0,   # Level 2 siblings
        2: 35.0,   # Level 3+ siblings
    })

    # === Per-depth connector configuration (for layer-specific edge styles) ===
    connector_config_by_depth: dict[int, dict] = field(default_factory=lambda: {
        0: {"connector_type": "bezier", "connector_style": "solid", "line_width": 2.0},  # Root → Level 1
        1: {"connector_type": "bezier", "connector_style": "solid", "line_width": 2.0},  # Level 1 → Level 2
        2: {"connector_type": "bezier", "connector_style": "solid", "line_width": 2.0},  # Level 2+
    })

    # === Runtime resolved styles (computed by resolve_style()) ===
    resolved_template: Template | None = None
    resolved_color_scheme: ColorScheme | None = None

    # === Edge configuration (legacy - TODO: migrate to EdgeConfig) ===
    edge: LegacyEdgeConfig = field(default_factory=LegacyEdgeConfig)

    # === Canvas background (synced from color_scheme) ===
    canvas_bg_color: str = "#FFFFFF"
