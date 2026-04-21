"""Base layout classes and configuration - Domain Layer

Defines the abstract base class for all layout algorithms and
the layout configuration data structures.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from cogist.domain.entities.node import Node

# === Base Configuration Classes ===

@dataclass
class BaseLayoutConfig:
    """Base layout configuration (marker base class)"""
    pass


@dataclass
class DefaultLayoutConfig(BaseLayoutConfig):
    """Default layout configuration (left-right balanced)"""
    level_spacing: float = 0.0  # Not used, kept for API compatibility
    sibling_spacing: float = 0.0  # Not used, kept for API compatibility
    level_spacing_by_depth: dict[int, float] = field(default_factory=dict)
    sibling_spacing_by_depth: dict[int, float] = field(default_factory=dict)

    def get_level_spacing(self, depth: int) -> float:
        """Get level spacing for a specific depth

        Args:
            depth: Parent node's depth in tree

        Returns:
            Horizontal spacing for this parent-child relationship
        """
        if depth in self.level_spacing_by_depth:
            return self.level_spacing_by_depth[depth]
        return self.level_spacing

    def get_sibling_spacing(self, depth: int) -> float:
        """Get sibling spacing for a specific depth

        Args:
            depth: Node depth in tree

        Returns:
            Sibling spacing for this depth
        """
        if depth in self.sibling_spacing_by_depth:
            return self.sibling_spacing_by_depth[depth]
        return self.sibling_spacing


# === Type Union for all layout configs ===

LayoutConfigType = DefaultLayoutConfig
"""Union type of all layout configuration types.

Add new config types here when implementing new layouts:
    LayoutConfigType = Union[DefaultLayoutConfig, TreeLayoutConfig, ...]
"""


# === Preset configurations ===

DEFAULT_LAYOUT_CONFIG = DefaultLayoutConfig()
"""Default layout configuration for DefaultLayout algorithm"""


class LayoutMetadata:
    """Layout metadata (for UI display and configuration)

    Attributes:
        name: Display name (e.g., "Default", "Tree")
        description: Human-readable description
        icon: Icon path or identifier (optional)
        category: Layout category ("general", "specialized", etc.)
        supports_mixed: Whether this layout supports mixed layout mode
    """

    def __init__(
        self,
        name: str,
        description: str,
        icon: str | None = None,
        category: str = "general",
        supports_mixed: bool = False,
    ):
        self.name = name
        self.description = description
        self.icon = icon
        self.category = category
        self.supports_mixed = supports_mixed


class BaseLayout(ABC):
    """Abstract base class for all layout algorithms

    All layout algorithms must inherit from this class and implement
    the layout() method.

    Design principles:
    1. Stateless: layout() should not modify internal state
    2. Pure function: same input produces same output
    3. Minimal dependencies: only depends on Node entities, not UI layer

    Attributes:
        config: Layout configuration (geometric parameters only)
        METADATA: Layout metadata (must be defined by subclasses)
    """

    # Subclasses must define metadata
    METADATA: LayoutMetadata

    def __init__(self, config: LayoutConfigType | None = None):
        """Initialize layout algorithm

        Args:
            config: Layout configuration (uses default if not provided)
        """
        self.config = config or self._get_default_config()

    @abstractmethod
    def _get_default_config(self) -> LayoutConfigType:
        """Return default configuration for this layout

        Subclasses must implement this to provide their default config.

        Returns:
            Default configuration instance
        """
        pass

    @abstractmethod
    def layout(
        self,
        root_node: Node,
        canvas_width: float = 1200.0,
        canvas_height: float = 800.0,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Execute layout calculation

        Args:
            root_node: Root node of the mind map
            canvas_width: Canvas width for centering
            canvas_height: Canvas height for centering
            context: Optional context information
                     - focused_node_id: Currently focused/selected node ID
                     - preserve_positions: Set of node IDs to preserve positions
                     - custom_data: Layout-specific custom data

        Returns:
            None (directly modifies Node.position attributes)

        Note:
            - This method should directly modify Node.position
            - Should not create new Node objects
            - Should maintain idempotency (multiple calls produce same result)
        """
        pass

    def supports_mixed_layout(self) -> bool:
        """Check if this layout supports mixed layout mode

        Returns:
            True if this layout can be combined with other layouts
        """
        return self.METADATA.supports_mixed

    def validate_tree(self, root_node: Node) -> list[str]:
        """Validate if the node tree is suitable for this layout

        Args:
            root_node: Root node to validate

        Returns:
            List of error messages (empty list means validation passed)
        """
        errors = []

        # Generic validation
        if root_node is None:
            errors.append("Root node cannot be None")

        # Subclasses can override to add specific validation
        return errors

    def get_recommended_canvas_size(self, root_node: Node) -> tuple[float, float]:
        """Recommend canvas size based on node tree size

        Args:
            root_node: Root node of the tree

        Returns:
            (width, height) Recommended canvas dimensions
        """
        # Default implementation: estimate based on node count
        node_count = self._count_nodes(root_node)
        width = max(1200, node_count * 50)
        height = max(800, node_count * 30)
        return (width, height)

    # === Protected helper methods ===

    def _count_nodes(self, node: Node) -> int:
        """Recursively count total nodes in tree

        Args:
            node: Starting node

        Returns:
            Total number of nodes including this node and all descendants
        """
        count = 1
        for child in node.children:
            count += self._count_nodes(child)
        return count

    def _get_all_nodes(self, node: Node) -> list[Node]:
        """Get all nodes in tree (pre-order traversal)

        Args:
            node: Starting node

        Returns:
            List of all nodes in pre-order
        """
        nodes = [node]
        for child in node.children:
            nodes.extend(self._get_all_nodes(child))
        return nodes
