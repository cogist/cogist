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

    # === Runtime resolved styles (computed by resolve_style()) ===
    resolved_template: Template | None = None
    resolved_color_scheme: ColorScheme | None = None

    # === Edge configuration (legacy - TODO: migrate to EdgeConfig) ===
    edge: LegacyEdgeConfig = field(default_factory=LegacyEdgeConfig)

    # === Canvas background (synced from color_scheme) ===
    canvas_bg_color: str = "#FFFFFF"
