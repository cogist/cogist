"""Style widgets package for style editor.

This package contains modular components for the style editor,
implementing lazy initialization and collapsible panels for better UX.
"""

from .border_section import BorderSection
from .canvas_panel import CanvasPanel
from .collapsible_panel import CollapsiblePanel
from .color_dialog_manager import ColorDialogManager, show_color_dialog_with_undo
from .color_scheme_section import ColorSchemeSection
from .connector_section import ConnectorSection
from .font_style_section import FontStyleSection
from .layer_selector import LayerSelector
from .menu_button import MenuButton
from .node_style_section import NodeStyleSection
from .shadow_section import ShadowSection
from .spacing_section import SpacingSection

__all__ = [
    "CollapsiblePanel",
    "LayerSelector",
    "NodeStyleSection",
    "FontStyleSection",
    "BorderSection",
    "ConnectorSection",
    "ShadowSection",
    "SpacingSection",
    "MenuButton",
    "ColorSchemeSection",
    "CanvasPanel",
    "ColorDialogManager",
    "show_color_dialog_with_undo",
]
