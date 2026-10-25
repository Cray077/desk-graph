"""Available desktop widget components and registry."""

from .base import BaseWidget
from .graph_widget import GraphWidget
from .clock_widget import ClockWidget
from .currency_widget import CurrencyWidget
from .registry import WIDGET_REGISTRY

__all__ = [
    "BaseWidget",
    "GraphWidget",
    "ClockWidget",
    "CurrencyWidget",
    "WIDGET_REGISTRY"
]
