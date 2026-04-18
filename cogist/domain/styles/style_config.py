"""Style configuration data structures for mind map styling."""

from dataclasses import dataclass, field

from .enums import PriorityLevel

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
class EdgeConfig:
    """Edge style configuration"""

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
    """Complete mind map style configuration"""

    name: str = "Default"
    
    # Canvas
    canvas_bg_color: str = "#FFFFFF"

    # Node styles by depth
    depth_styles: dict[int, NodeStyleConfig] = field(default_factory=dict)

    # Priority scheme
    priority_scheme: PriorityScheme = field(default_factory=PriorityScheme)

    # Layout and edge configuration
    layout: LayoutConfig = field(default_factory=LayoutConfig)
    edge: EdgeConfig = field(default_factory=EdgeConfig)

    def __post_init__(self):
        """Initialize default depth styles and priority scheme if not provided"""
        if not self.depth_styles:
            self._init_default_depth_styles()
        
        # Initialize priority scheme with critical and minor overrides
        if self.priority_scheme.name == "Default":
            self._init_default_priority_scheme()

    def _init_default_depth_styles(self):
        """Initialize default depth-based styles (from current implementation)"""
        self.depth_styles = {
            0: NodeStyleConfig(
                shape="rounded_rect",
                font_size=22,
                font_weight="Bold",
                font_family="Arial",
                padding_width=20,
                padding_height=16,
                border_radius=10,
                border_style="solid",
                border_width=2,
                bg_color="#2196F3",
                text_color="#FFFFFF",
                border_color="#1976D2",
                max_text_width=MAX_TEXT_WIDTH,
            ),
            1: NodeStyleConfig(
                shape="rounded_rect",
                font_size=18,
                font_weight="Normal",
                font_family="Arial",
                padding_width=20,
                padding_height=16,
                border_radius=8,
                border_style="solid",
                border_width=2,
                bg_color="#4CAF50",
                text_color="#FFFFFF",
                border_color="#388E3C",
                max_text_width=MAX_TEXT_WIDTH,
            ),
            2: NodeStyleConfig(
                shape="rounded_rect",
                font_size=16,
                font_weight="Normal",
                font_family="Arial",
                padding_width=8,
                padding_height=6,
                border_radius=6,
                border_style="solid",
                border_width=2,
                bg_color="#FF9800",
                text_color="#FFFFFF",
                border_color="#F57C00",
                max_text_width=MAX_TEXT_WIDTH,
            ),
            3: NodeStyleConfig(
                shape="rounded_rect",
                font_size=14,
                font_weight="Normal",
                font_family="Arial",
                padding_width=6,
                padding_height=4,
                border_radius=4,
                border_style="solid",
                border_width=2,
                bg_color="#9E9E9E",
                text_color="#FFFFFF",
                border_color="#757575",
                max_text_width=MAX_TEXT_WIDTH,
            ),
        }

    def _init_default_priority_scheme(self):
        """Initialize priority scheme with critical and minor overrides"""
        # Critical (LEVEL_2) - Red, bold, thick border
        self.priority_scheme.levels[PriorityLevel.LEVEL_2].style_override = NodeStyleConfig(
            bg_color="#D32F2F",
            text_color="#FFFFFF",
            font_size=24,
            font_weight="ExtraBold",
            border_width=4,
            border_color="#B71C1C",
        )
        
        # Unimportant (LEVEL_0) - Gray, light
        self.priority_scheme.levels[PriorityLevel.LEVEL_0].style_override = NodeStyleConfig(
            bg_color="#BDBDBD",
            text_color="#FFFFFF",
            font_size=18,
            font_weight="Light",
            border_width=1,
        )

    def get_depth_style(self, depth: int) -> NodeStyleConfig:
        """Get base style for a given depth"""
        if depth in self.depth_styles:
            return self.depth_styles[depth]
        # For depth > 3, use depth 3 style
        return self.depth_styles.get(3, NodeStyleConfig())

    def resolve_node_style(self, depth: int, priority: PriorityLevel) -> NodeStyleConfig:
        """Resolve final style by merging depth and priority styles"""
        base_style = self.get_depth_style(depth)
        priority_override = self.priority_scheme.get_style_override(priority)
        return base_style.merge(priority_override)

    def get_level_spacing(self, parent_depth: int) -> float:
        """Get horizontal spacing based on parent depth"""
        if parent_depth == 0:
            return self.layout.level_spacing_depth_0
        elif parent_depth == 1:
            return self.layout.level_spacing_depth_1
        else:
            return self.layout.level_spacing_depth_2_plus

    def get_sibling_spacing(self, depth: int) -> float:
        """Get vertical spacing based on node depth"""
        if depth <= 1:
            return self.layout.sibling_spacing_depth_0_1
        elif depth == 2:
            return self.layout.sibling_spacing_depth_2
        else:
            return self.layout.sibling_spacing_depth_3_plus
