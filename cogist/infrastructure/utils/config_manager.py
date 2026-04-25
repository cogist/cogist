"""Configuration Manager - Infrastructure Layer

Manages application configuration with cross-platform support.
Handles loading, saving, and accessing user preferences.
"""
import json
import os
from pathlib import Path
from typing import Any

from .platform import PLATFORM


class ConfigManager:
    """Manages application configuration.

    Stores configuration in platform-specific directories:
    - macOS: ~/Library/Application Support/cogist/config.json
    - Windows: %APPDATA%/cogist/config.json
    - Linux: ~/.config/cogist/config.json
    """

    def __init__(self):
        self.config_file = self._get_config_file_path()
        self.config: dict[str, Any] = {}
        self.load()

    def _get_config_file_path(self) -> Path:
        """Get platform-specific config file path."""
        if PLATFORM == "Darwin":
            base = Path.home() / "Library" / "Application Support" / "cogist"
        elif PLATFORM == "Windows":
            base = Path(os.environ.get("APPDATA", "")) / "cogist"
        else:  # Linux and others
            base = Path.home() / ".config" / "cogist"

        base.mkdir(parents=True, exist_ok=True)
        return base / "config.json"

    def load(self):
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                self.config = json.loads(self.config_file.read_text())
            except Exception as e:
                print(f"Failed to load config: {e}")
                self.config = {}

    def save(self):
        """Save configuration to file."""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.config_file.write_text(
            json.dumps(self.config, indent=2, ensure_ascii=False)
        )

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value."""
        self.config[key] = value

    def get_template_directory(self) -> Path:
        """Get template directory path.

        Returns user-configured path if set, otherwise uses default platform path.

        Default paths:
        - macOS: ~/Library/Application Support/cogist/templates/
        - Windows: %APPDATA%/cogist/templates/
        - Linux: ~/.local/share/cogist/templates/
        """
        # Check if user has custom path in config
        custom_path = self.config.get("template_directory")
        if custom_path:
            return Path(custom_path)

        # Use default platform path
        if PLATFORM == "Darwin":
            base = Path.home() / "Library" / "Application Support" / "cogist"
        elif PLATFORM == "Windows":
            base = Path(os.environ.get("APPDATA", "")) / "cogist"
        else:  # Linux and others
            base = Path.home() / ".local" / "share" / "cogist"

        template_dir = base / "templates"
        template_dir.mkdir(parents=True, exist_ok=True)
        return template_dir


# Singleton instance
config_manager = ConfigManager()
