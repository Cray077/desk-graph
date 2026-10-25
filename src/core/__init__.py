"""Core application window and configuration management."""

from .config import ConfigManager
from .window import FloatingWidgetWindow, WindowManager

__all__ = ["ConfigManager", "FloatingWidgetWindow", "WindowManager"]
