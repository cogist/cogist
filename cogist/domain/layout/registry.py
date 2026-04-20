"""Layout algorithm registry - Domain Layer

Provides a registry for managing and creating layout algorithm instances.
Supports dynamic switching between different layout algorithms.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from cogist.domain.layout.base import BaseLayout, LayoutConfigType

if TYPE_CHECKING:
    pass


class LayoutRegistry:
    """Registry for layout algorithms

    Manages available layout algorithms and provides factory methods
    to create layout instances by name.

    Usage:
        registry = LayoutRegistry()
        registry.register("default", DefaultLayout)

        # Create layout instance
        layout = registry.get_layout("default", config)

        # Get available layouts
        names = registry.get_available_layouts()  # ["default"]
    """

    def __init__(self):
        """Initialize the layout registry"""
        self._layouts: dict[str, type[BaseLayout]] = {}

    def register(self, name: str, layout_class: type[BaseLayout]) -> None:
        """Register a layout algorithm

        Args:
            name: Unique identifier for the layout (e.g., "default", "tree")
            layout_class: Layout class (must inherit from BaseLayout)

        Raises:
            ValueError: If name is already registered
        """
        if name in self._layouts:
            raise ValueError(f"Layout '{name}' is already registered")

        self._layouts[name] = layout_class

    def unregister(self, name: str) -> None:
        """Unregister a layout algorithm

        Args:
            name: Layout identifier to remove

        Raises:
            KeyError: If layout is not registered
        """
        if name not in self._layouts:
            raise KeyError(f"Layout '{name}' is not registered")

        del self._layouts[name]

    def get_layout(self, name: str, config: LayoutConfigType | None = None) -> BaseLayout:
        """Create a layout algorithm instance

        Args:
            name: Layout identifier
            config: Optional configuration (uses layout's default if not provided)

        Returns:
            Layout algorithm instance

        Raises:
            ValueError: If layout is not registered
        """
        if name not in self._layouts:
            available = ", ".join(self._layouts.keys())
            raise ValueError(
                f"Unknown layout algorithm: '{name}'. "
                f"Available layouts: {available}"
            )

        layout_class = self._layouts[name]
        return layout_class(config)

    def get_available_layouts(self) -> list[str]:
        """Get all registered layout algorithm names

        Returns:
            List of layout identifiers
        """
        return list(self._layouts.keys())

    def has_layout(self, name: str) -> bool:
        """Check if a layout algorithm is registered

        Args:
            name: Layout identifier

        Returns:
            True if layout is registered
        """
        return name in self._layouts

    def clear(self) -> None:
        """Remove all registered layouts"""
        self._layouts.clear()


# Global registry instance
layout_registry = LayoutRegistry()
"""Global layout registry for the application

This singleton instance should be used throughout the application
to maintain a consistent set of registered layouts.
"""
