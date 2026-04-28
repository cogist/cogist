"""Style widgets package for advanced style panel.

This package contains modular components for the advanced style panel,
implementing lazy initialization and collapsible panels for better UX.
"""

from .border_section import BorderSection
from .canvas_section import CanvasSection
from .collapsible_panel import CollapsiblePanel
from .color_scheme_section import ColorSchemeSection
from .connector_section import ConnectorSection
from .layer_selector import LayerSelector
from .menu_button import MenuButton
from .node_style_section import NodeStyleSection
from .shadow_section import ShadowSection
from .spacing_section import SpacingSection

__all__ = [
    "CollapsiblePanel",
    "LayerSelector",
    "CanvasSection",
    "NodeStyleSection",
    "BorderSection",
    "ConnectorSection",
    "ShadowSection",
    "SpacingSection",
    "MenuButton",
    "ColorSchemeSection",
]
