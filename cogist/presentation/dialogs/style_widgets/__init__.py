"""Style widgets package for advanced style panel.

This package contains modular components for the advanced style panel,
implementing lazy initialization and collapsible panels for better UX.
"""

from .collapsible_panel import CollapsiblePanel
from .layer_selector import LayerSelector
from .canvas_section import CanvasSection
from .node_style_section import NodeStyleSection
from .border_section import BorderSection
from .connector_section import ConnectorSection

__all__ = [
    "CollapsiblePanel",
    "LayerSelector",
    "CanvasSection",
    "NodeStyleSection",
    "BorderSection",
    "ConnectorSection",
]
