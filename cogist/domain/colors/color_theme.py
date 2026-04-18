"""Color themes - Domain Layer

Defines color theme data structures for consistent color schemes.
Themes provide colors only, independent of templates and layouts.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ColorTheme:
    """Color theme definition (pure color scheme)
    
    Themes define the color palette for the mind map without specifying
    geometric properties or layout algorithms.
    
    Attributes:
        name: Theme identifier (e.g., "blue", "dark", "warm")
        canvas_bg: Canvas background color (hex)
        node_colors: Node colors by depth level (hex)
        edge_color: Edge/connector color (hex)
        text_color: Default text color (hex)
        priority_colors: Colors for different priority levels (hex)
    """
    name: str
    
    # Canvas
    canvas_bg: str = "#FFFFFF"
    
    # Node colors by depth (level 0 = root, level 1 = first children, etc.)
    node_colors: dict[int, str] = field(default_factory=lambda: {
        0: "#2196F3",  # Root - Blue
        1: "#4CAF50",  # Level 1 - Green
        2: "#FF9800",  # Level 2 - Orange
        3: "#9C27B0",  # Level 3 - Purple
        4: "#F44336",  # Level 4+ - Red
    })
    
    # Edges
    edge_color: str = "#666666"
    
    # Text
    text_color: str = "#333333"
    
    # Priority colors (override node colors for priority nodes)
    priority_colors: dict[str, str | None] = field(default_factory=lambda: {
        "critical": "#D32F2F",  # Dark red for critical
        "normal": None,          # Use default node color
        "low": "#9E9E9E",       # Gray for low priority
    })
    
    def get_node_color(self, depth: int) -> str:
        """Get node color for a specific depth level
        
        Args:
            depth: Node depth in tree (0 = root)
        
        Returns:
            Hex color code
        """
        # Return color for specific depth, or use last defined color
        if depth in self.node_colors:
            return self.node_colors[depth]
        
        # For depths beyond defined levels, cycle through available colors
        max_depth = max(self.node_colors.keys())
        if depth > max_depth:
            # Cycle: use modulo to repeat colors
            cycle_depth = ((depth - max_depth - 1) % (max_depth + 1))
            return self.node_colors.get(cycle_depth, self.node_colors[max_depth])
        
        return self.node_colors.get(0, "#000000")
    
    def get_priority_color(self, priority: str, base_color: str | None = None) -> str:
        """Get color for a priority level
        
        Args:
            priority: Priority level (e.g., "critical", "normal", "low")
            base_color: Base node color (for relative adjustments)
        
        Returns:
            Hex color code for priority node
        """
        priority_color = self.priority_colors.get(priority)
        
        if priority_color is None:
            # No override, use base color
            return base_color or self.get_node_color(0)
        
        return priority_color


# === Preset Themes ===

BLUE_THEME = ColorTheme(
    name="blue",
    canvas_bg="#FFFFFF",
    node_colors={
        0: "#2196F3",  # Blue
        1: "#4CAF50",  # Green
        2: "#FF9800",  # Orange
        3: "#9C27B0",  # Purple
    },
    edge_color="#666666",
    text_color="#333333",
    priority_colors={
        "critical": "#D32F2F",
        "normal": None,
        "low": "#9E9E9E",
    },
)
"""Blue theme with vibrant colors"""


DARK_THEME = ColorTheme(
    name="dark",
    canvas_bg="#1E1E1E",
    node_colors={
        0: "#4FC3F7",  # Light blue
        1: "#81C784",  # Light green
        2: "#FFB74D",  # Light orange
        3: "#BA68C8",  # Light purple
    },
    edge_color="#999999",
    text_color="#E0E0E0",
    priority_colors={
        "critical": "#EF5350",
        "normal": None,
        "low": "#757575",
    },
)
"""Dark theme for low-light environments"""


WARM_THEME = ColorTheme(
    name="warm",
    canvas_bg="#FFF8E1",
    node_colors={
        0: "#FF6F00",  # Amber
        1: "#F57C00",  # Orange
        2: "#D84315",  # Deep orange
        3: "#BF360C",  # Red-orange
    },
    edge_color="#8D6E63",
    text_color="#4E342E",
    priority_colors={
        "critical": "#C62828",
        "normal": None,
        "low": "#A1887F",
    },
)
"""Warm theme with earth tones"""


COOL_THEME = ColorTheme(
    name="cool",
    canvas_bg="#E3F2FD",
    node_colors={
        0: "#1565C0",  # Dark blue
        1: "#00838F",  # Cyan
        2: "#00695C",  # Teal
        3: "#2E7D32",  # Green
    },
    edge_color="#546E7A",
    text_color="#263238",
    priority_colors={
        "critical": "#B71C1C",
        "normal": None,
        "low": "#78909C",
    },
)
"""Cool theme with calming blues and greens"""


# Theme registry
COLOR_THEMES: dict[str, ColorTheme] = {
    "blue": BLUE_THEME,
    "dark": DARK_THEME,
    "warm": WARM_THEME,
    "cool": COOL_THEME,
}
"""Registry of all available color themes"""
