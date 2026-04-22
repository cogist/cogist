"""Style configuration data structures for mind map styling."""

from dataclasses import dataclass, field

from .extended_styles import ColorScheme, Template

# Global constant for maximum text width across all node levels
MAX_TEXT_WIDTH = 250.0


@dataclass
class LegacyEdgeConfig:
    """Legacy edge style configuration (used for backward compatibility with main.py).

    Note: enable_gradient is automatically determined by connector_shape.
    gradient_ratio should be stored in connector_config_by_depth, not here.
    """

    connector_shape: str = "bezier"  # bezier, straight, orthogonal
    connector_style: str = "solid"  # solid, dashed, dotted, dash_dot
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
    parent_child_spacing: float = field(default=0.0)  # Must be set in create_default_template()
    sibling_spacing: float = field(default=0.0)       # Must be set in create_default_template()

    # === Per-depth spacing configuration (for true layer isolation) ===
    # NOTE: All initialization should happen in create_default_template(), not here
    level_spacing_by_depth: dict[int, float] = field(default_factory=dict)
    sibling_spacing_by_depth: dict[int, float] = field(default_factory=dict)

    # === Per-depth connector configuration (for layer-specific edge styles) ===
    # NOTE: All initialization should happen in create_default_template(), not here
    connector_config_by_depth: dict[int, dict] = field(default_factory=dict)

    # === Runtime resolved styles (computed by resolve_style()) ===
    resolved_template: Template | None = None
    resolved_color_scheme: ColorScheme | None = None

    # === Edge configuration (legacy - TODO: migrate to EdgeConfig) ===
    edge: LegacyEdgeConfig = field(default_factory=LegacyEdgeConfig)

    # === Canvas background (synced from color_scheme) ===
    canvas_bg_color: str = "#FFFFFF"
