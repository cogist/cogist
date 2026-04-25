"""Registry for border drawing strategies."""


from .base import BorderStrategy
from .container_borders import CircleBorder, RoundedRectBorder
from .decorative_lines import BottomLineBorder, LeftLineBorder


class BorderStrategyRegistry:
    """Registry mapping shape names to border strategy classes.

    Provides a centralized way to get the appropriate border strategy
    for a given shape name. Follows the same pattern as ConnectorStrategy.
    """

    _strategies: dict[str, type[BorderStrategy]] = {
        "rounded_rect": RoundedRectBorder,
        "rect": RoundedRectBorder,  # Rect uses same strategy with radius=0
        "circle": CircleBorder,
        "bottom_line": BottomLineBorder,
        "left_line": LeftLineBorder,
    }

    @classmethod
    def get_strategy(cls, shape_name: str) -> BorderStrategy:
        """Get border strategy instance for given shape name.

        Args:
            shape_name: Name of the shape (e.g., 'rounded_rect', 'bottom_line')

        Returns:
            BorderStrategy instance

        Raises:
            ValueError: If shape_name is not registered
        """
        strategy_class = cls._strategies.get(shape_name)
        if not strategy_class:
            raise ValueError(f"Unknown shape: {shape_name}. Available shapes: {list(cls._strategies.keys())}")
        return strategy_class()

    @classmethod
    def register(cls, shape_name: str, strategy_class: type[BorderStrategy]) -> None:
        """Register a new border strategy.

        This allows extending the system with custom shapes without modifying
        the registry code.

        Args:
            shape_name: Name to associate with this strategy
            strategy_class: BorderStrategy subclass
        """
        cls._strategies[shape_name] = strategy_class

    @classmethod
    def get_available_shapes(cls) -> list[str]:
        """Get list of all registered shape names.

        Returns:
            List of available shape names
        """
        return list(cls._strategies.keys())
