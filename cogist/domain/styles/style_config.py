"""Style configuration data structures for mind map styling."""

from dataclasses import dataclass, field

from .enums import PriorityLevel
from .extended_styles import ColorScheme, EdgeConfig as NewEdgeConfig, Template

# Global constant for maximum text width across all node levels
MAX_TEXT_WIDTH = 250.0


@dataclass
class NodeStyleConfig:
    """Complete node style configuration"""

    # Shape
    shape: str = "rounded_rect"  # rect, rounded_rect, circle

    # Font
    font_size: int = 16
    font_weight: str = "Normal"  # Normal, Bold, ExtraBold, Light
    font_family: str = "Arial"
    font_italic: bool = False
    font_underline: bool = False
    font_strikeout: bool = False  # Strikethrough text

    # Padding and sizing
    padding_width: int = 10
    padding_height: int = 8
    border_radius: int = 8
    max_text_width: float = 250.0

    # Border
    border_style: str = "solid"  # solid, dashed, dotted, dash_dot
    border_width: int = 2

    # Colors
    bg_color: str | None = None  # None means use template default
    text_color: str | None = "#000000"
    border_color: str | None = None

    def merge(self, other: "NodeStyleConfig") -> "NodeStyleConfig":
        """Merge another config on top of this one (other takes precedence)

        Only non-default values from other will override self values.
        """
        result = NodeStyleConfig()
        for key in self.__dataclass_fields__:
            other_value = getattr(other, key)
            self_value = getattr(self, key)
            # Use other's value if it's not the default
            default_value = self.__dataclass_fields__[key].default
            if other_value != default_value:
                setattr(result, key, other_value)
            else:
                setattr(result, key, self_value)
        return result


@dataclass
class LayoutConfig:
    """Layout spacing configuration"""

    # Horizontal spacing (parent to child)
    level_spacing_depth_0: float = 80.0  # Root to level 1
    level_spacing_depth_1: float = 60.0  # Level 1 to level 2
    level_spacing_depth_2_plus: float = 40.0  # Level 2+

    # Vertical spacing (between siblings)
    sibling_spacing_depth_0_1: float = 60.0  # Level 1 nodes
    sibling_spacing_depth_2: float = 45.0  # Level 2 nodes
    sibling_spacing_depth_3_plus: float = 35.0  # Level 3+


@dataclass
class LegacyEdgeConfig:
    """Legacy edge style configuration (deprecated, use extended_styles.EdgeConfig)."""

    connector_type: str = "bezier"  # straight, orthogonal, bezier
    connector_style: str = "solid"  # solid, dashed, dotted
    start_width: float = 6.0  # Width at source node
    end_width: float = 2.0    # Width at target node
    color: str = "#666666"


@dataclass
class PriorityDefinition:
    """Definition of a single priority level"""

    level: PriorityLevel
    name: str  # Customizable display name
    style_override: NodeStyleConfig = field(default_factory=NodeStyleConfig)


@dataclass
class PriorityScheme:
    """Complete priority scheme (customizable by user)"""

    name: str = "Default"
    levels: dict[PriorityLevel, PriorityDefinition] = field(default_factory=dict)

    def __post_init__(self):
        """Initialize default priority levels if not provided"""
        if not self.levels:
            for level in PriorityLevel:
                self.levels[level] = PriorityDefinition(
                    level=level,
                    name=level.default_name,
                    style_override=NodeStyleConfig(),
                )

    def get_name(self, level: PriorityLevel) -> str:
        """Get display name for a priority level"""
        return self.levels[level].name

    def set_name(self, level: PriorityLevel, name: str):
        """Set custom display name for a priority level"""
        self.levels[level].name = name

    def get_style_override(self, level: PriorityLevel) -> NodeStyleConfig:
        """Get style override for a priority level"""
        return self.levels[level].style_override


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

    # === Edge configuration (new architecture) ===
    edge: NewEdgeConfig = field(default_factory=NewEdgeConfig)
    
    # === Canvas background (synced from color_scheme) ===
    canvas_bg_color: str = "#FFFFFF"
