"""Template deserialization utilities."""

from typing import Any

from cogist.domain.styles import (
    MindMapStyle,
    deserialize_style,
)


def deserialize_complete_template(data: dict[str, Any]) -> MindMapStyle:
    """Deserialize a complete template from JSON data.

    NEW: Uses self-contained MindMapStyle format (no resolved_template/resolved_color_scheme).

    Args:
        data: Complete template data containing style_config (self-contained)

    Returns:
        MindMapStyle instance with embedded role_styles
    """
    # Deserialize style config (self-contained in new format)
    style_config_data = data.get('style_config', data)  # Fallback to root if no style_config key
    style = deserialize_style(style_config_data)

    return style
