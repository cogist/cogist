"""Presentation layer widgets."""

from .color_pool_popup import ColorPoolPopup
from .connector_previews import (
    generate_bezier_preview,
    generate_bezier_uniform_preview,
    generate_orthogonal_preview,
    generate_rounded_orthogonal_preview,
    generate_sharp_first_rounded_preview,
    generate_straight_preview,
)
from .toggle_switch import ToggleSwitch
from .visual_list_popup import VisualListPopup
from .visual_preview_button import VisualPreviewButton
from .visual_selector import VisualOption, VisualOptionButton, VisualSelector

__all__ = [
    # Widgets
    "ColorPoolPopup",
    "ToggleSwitch",
    "VisualListPopup",
    "VisualOption",
    "VisualOptionButton",
    "VisualPreviewButton",
    "VisualSelector",

    # Preview generators
    "generate_bezier_preview",
    "generate_bezier_uniform_preview",
    "generate_straight_preview",
    "generate_orthogonal_preview",
    "generate_rounded_orthogonal_preview",
    "generate_sharp_first_rounded_preview",
]
