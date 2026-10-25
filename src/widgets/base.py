"""Base class for modular desktop widgets."""

import tkinter as tk
from abc import ABC, abstractmethod
from typing import Tuple
from ..utils.theme import Theme
from ..core.config import ConfigManager

class BaseWidget(tk.Frame, ABC):
    """Abstract base class that all desktop widget components inherit from."""

    def __init__(self, master: tk.Misc, theme: Theme, config: ConfigManager, **kwargs):
        super().__init__(master, bg=theme.bg, **kwargs)
        self.theme = theme
        self.config = config
        self.scale_factor: float = float(config.get("scale_factor", 1.0))

    @abstractmethod
    def get_title(self) -> str:
        """Return the display title of the widget."""
        pass

    @abstractmethod
    def get_preferred_size(self) -> Tuple[int, int]:
        """Return the ideal (width, height) in pixels for this widget."""
        return (280, 160)

    def on_mount(self) -> None:
        """Called immediately after widget is mounted in the parent window."""
        pass

    def on_update(self) -> None:
        """Periodic tick called by the main window loop (e.g. every second)."""
        pass

    def on_theme_change(self, new_theme: Theme) -> None:
        """Called when user changes the active color palette."""
        self.theme = new_theme
        self.configure(bg=new_theme.bg)

    def set_scale(self, scale: float) -> None:
        """Apply scaling factor to fonts and layouts."""
        self.scale_factor = scale
        self.on_scale_change(scale)

    def on_scale_change(self, scale: float) -> None:
        """Override in subclasses to update fonts, canvas sizes, paddings."""
        pass

    def on_destroy(self) -> None:
        """Cleanup handler before the widget is destroyed or switched."""
        pass
