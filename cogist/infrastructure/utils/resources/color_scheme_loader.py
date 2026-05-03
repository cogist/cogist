"""Resource loader for color schemes."""

import json
from pathlib import Path
from typing import Any


def get_builtin_color_scheme(name: str = "default") -> dict[str, Any] | None:
    """Get a built-in color scheme from assets directory.

    Args:
        name: Color scheme name (without .json extension)

    Returns:
        Color scheme data dictionary, or None if not found
    """
    try:
        # Try loading from project root's assets/color_schemes/
        import sys

        # Get the base directory (project root or executable directory)
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            base_dir = Path(sys.executable).parent
        else:
            # Running as script
            base_dir = Path(__file__).parent.parent.parent.parent.parent  # Go up to project root

        scheme_file = base_dir / 'assets' / 'color_schemes' / f"{name}.json"

        if scheme_file.exists():
            return json.loads(scheme_file.read_text(encoding='utf-8'))
    except Exception:
        pass

    return None


def load_color_scheme_with_fallback(name: str = "default") -> dict[str, Any]:
    """Load color scheme with two-level fallback strategy.

    Level 1: User's customized color scheme (if exists)
    Level 2: Built-in color scheme (read-only, no auto-copy)

    Args:
        name: Color scheme name

    Returns:
        Color scheme data dictionary

    Raises:
        RuntimeError: If both user and built-in color schemes fail to load
    """
    from cogist.infrastructure.utils import config_manager

    # Level 1: Try user's customized color scheme
    template_dir = config_manager.get_template_directory()
    color_schemes_dir = template_dir.parent / "color_schemes"
    user_scheme = color_schemes_dir / f"{name}.json"

    if user_scheme.exists():
        try:
            return json.loads(user_scheme.read_text(encoding='utf-8'))
        except Exception as e:
            print(f"Failed to load user color scheme: {e}, falling back to built-in")

    # Level 2: Load built-in color scheme directly (read-only)
    builtin_data = get_builtin_color_scheme(name)
    if builtin_data:
        return builtin_data
    else:
        raise RuntimeError(
            f"Failed to load color scheme '{name}'. Built-in color scheme is missing or corrupted."
        )
