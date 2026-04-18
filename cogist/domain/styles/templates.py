"""Preset templates for mind map styling."""

from .enums import PriorityLevel
from .style_config import MindMapStyle, NodeStyleConfig


def create_default_template() -> MindMapStyle:
    """Current default style as a template"""
    style = MindMapStyle(name="Default")

    # Add priority style overrides
    style.priority_scheme.levels[PriorityLevel.LEVEL_2].style_override = NodeStyleConfig(
        bg_color="#D32F2F",  # Red for important
        font_weight="Bold",
    )

    style.priority_scheme.levels[PriorityLevel.LEVEL_0].style_override = NodeStyleConfig(
        bg_color="#9E9E9E",  # Gray for unimportant
        text_color="#FFFFFF",
    )

    return style
