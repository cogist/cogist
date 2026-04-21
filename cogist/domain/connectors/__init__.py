"""Connector strategies for edge path generation.

This module provides different connector types using the Strategy pattern.
Each connector type implements the ConnectorStrategy interface.
"""

from .base import ConnectorStrategy
from .bezier_connector import BezierConnector
from .orthogonal_connector import OrthogonalConnector
from .straight_connector import StraightConnector

__all__ = [
    "ConnectorStrategy",
    "BezierConnector",
    "StraightConnector",
    "OrthogonalConnector",
]
