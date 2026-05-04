"""Resource loader for built-in templates."""

import json
from pathlib import Path
from typing import Any


def get_builtin_template(name: str = "default") -> dict[str, Any] | None:
    """Get a built-in template from assets directory.

    Args:
        name: Template name (without .json extension)

    Returns:
        Template data dictionary, or None if not found
    """
    try:
        # Try loading from project root's assets/templates/
        # This works in both development and packaged environments
        import sys

        # Get the base directory (project root or executable directory)
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            # For macOS .app bundles, resources are in Contents/Resources/
            if sys.platform == 'darwin' and '.app' in str(Path(sys.executable)):
                # macOS .app bundle: go up from MacOS/ to Contents/, then to Resources/
                base_dir = Path(sys.executable).parent.parent / 'Resources'
            else:
                # Other platforms: resources are next to executable
                base_dir = Path(sys.executable).parent
        else:
            # Running as script
            base_dir = Path(__file__).parent.parent.parent.parent.parent  # Go up to project root

        template_file = base_dir / 'assets' / 'templates' / f"{name}.json"

        if template_file.exists():
            return json.loads(template_file.read_text(encoding='utf-8'))
    except Exception:
        pass

    return None


def save_template_to_user_dir(template_data: dict[str, Any], name: str = "default") -> Path | None:
    """Save template to user's template directory.

    Args:
        template_data: Template data dictionary
        name: Template name

    Returns:
        Path to saved file, or None if failed
    """
    try:
        from cogist.infrastructure.utils import config_manager

        template_dir = config_manager.get_template_directory()
        template_file = template_dir / f"{name}.json"

        import json
        template_file.write_text(
            json.dumps(template_data, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

        return template_file
    except Exception as e:
        print(f"Failed to save template to user directory: {e}")
        return None
