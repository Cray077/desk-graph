"""Widget registry for desktop widgets."""

from typing import Dict, Type
from .base import BaseWidget
from .graph_widget import GraphWidget
from .clock_widget import ClockWidget
from .currency_widget import CurrencyWidget

WIDGET_REGISTRY: Dict[str, Type[BaseWidget]] = {
    "currency": CurrencyWidget,
    "graph": GraphWidget,
    "clock": ClockWidget,
}

__all__ = ["WIDGET_REGISTRY"]
