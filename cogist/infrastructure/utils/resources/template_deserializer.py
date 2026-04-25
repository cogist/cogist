"""Template deserialization utilities."""

from typing import Any

from cogist.domain.styles import (
    MindMapStyle,
    deserialize_color_scheme,
    deserialize_style,
    deserialize_template,
)


def deserialize_complete_template(data: dict[str, Any]) -> MindMapStyle:
    """Deserialize a complete template from JSON data.

    This reuses the same logic as CGSSerializer._read_style_config(),
    but reads from a single JSON structure instead of separate files.

    Args:
        data: Complete template data containing style_config, template, and color_scheme

    Returns:
        MindMapStyle instance with resolved template and color scheme
    """
    # Deserialize style config (same as CGS format)
    style_config_data = data.get('style_config', {})
    style = deserialize_style(style_config_data)

    # Deserialize and attach template if present (same as CGS format)
    if 'template' in data:
        template_data = data['template']
        style.resolved_template = deserialize_template(template_data)

    # Deserialize and attach color scheme if present (same as CGS format)
    if 'color_scheme' in data:
        color_scheme_data = data['color_scheme']
        style.resolved_color_scheme = deserialize_color_scheme(color_scheme_data)

        # Sync canvas background color
        if style.resolved_color_scheme:
            style.canvas_bg_color = style.resolved_color_scheme.canvas_bg_color

    return style
