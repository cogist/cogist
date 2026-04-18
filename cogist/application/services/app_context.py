"""Application context for global state management.

Provides a centralized way to access application-wide services and components.
This pattern supports both SDI (current) and future MDI architectures.
"""

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from main import MainWindow


class AppContext:
    """Global application context singleton.
    
    Provides access to the current active window and its components.
    In SDI mode: returns the single MainWindow instance.
    In MDI mode (future): returns the currently active tab/window.
    """

    _instance: Optional['AppContext'] = None
    _main_window: Optional['MainWindow'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> 'AppContext':
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def set_main_window(self, window: 'MainWindow') -> None:
        """Set the current main window (called during initialization)."""
        self._main_window = window

    def get_main_window(self) -> Optional['MainWindow']:
        """Get the current main window."""
        return self._main_window

    def get_mindmap_view(self):
        """Get the mind map view from current window."""
        if self._main_window:
            return self._main_window.mindmap_view
        return None

    def get_style_config(self):
        """Get the current style configuration."""
        if self._main_window:
            return self._main_window.current_style
        return None


# Convenience function for easy access
def get_app_context() -> AppContext:
    """Get the global application context."""
    return AppContext.get_instance()
