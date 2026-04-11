"""Style configuration data structures for mind map styling."""

from dataclasses import dataclass, field

from .enums import PriorityLevel

# Global constant for maximum text width across all node levels
MAX_TEXT_WIDTH = 250.0


@dataclass
class NodeStyleConfig:
    """Complete node style configuration"""

    font_size: int = 16
    font_weight: str = "Normal"  # Normal, Bold
    padding_width: int = 10
    padding_height: int = 8
    border_radius: int = 8
    max_text_width: float = 250.0
    bg_color: str | None = None  # None means use template default
    text_color: str | None = "#000000"
    no_background: bool = False

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

    width: float = 2.0
    color: str = "#CCCCCC"
    style: str = "solid"  # solid, dashed


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

    # Node styles by depth
    depth_styles: dict[int, NodeStyleConfig] = field(default_factory=dict)

    # Priority scheme
    priority_scheme: PriorityScheme = field(default_factory=PriorityScheme)

    # Layout and edge configuration
    layout: LayoutConfig = field(default_factory=LayoutConfig)
    edge: EdgeConfig = field(default_factory=EdgeConfig)

    def __post_init__(self):
        """Initialize default depth styles if not provided"""
        if not self.depth_styles:
            self._init_default_depth_styles()

    def _init_default_depth_styles(self):
        """Initialize default depth-based styles (from current implementation)"""
        self.depth_styles = {
            0: NodeStyleConfig(
                font_size=22,
                font_weight="Bold",
                padding_width=20,
                padding_height=16,
                border_radius=10,
                max_text_width=MAX_TEXT_WIDTH,
            ),
            1: NodeStyleConfig(
                font_size=18,
                font_weight="Bold",
                padding_width=20,
                padding_height=16,
                border_radius=8,
                max_text_width=MAX_TEXT_WIDTH,
            ),
            2: NodeStyleConfig(
                font_size=16,
                font_weight="Normal",
                padding_width=8,
                padding_height=6,
                border_radius=6,
                max_text_width=MAX_TEXT_WIDTH,
            ),
            3: NodeStyleConfig(
                font_size=14,
                font_weight="Normal",
                padding_width=6,
                padding_height=4,
                border_radius=4,
                max_text_width=MAX_TEXT_WIDTH,
                no_background=True,
            ),
        }

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
