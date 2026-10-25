"""Minimalist digital clock and date desktop widget."""

import tkinter as tk
from datetime import datetime
from typing import Tuple
from .base import BaseWidget
from ..utils.theme import Theme
from ..core.config import ConfigManager

class ClockWidget(BaseWidget):
    """A clean digital clock and calendar widget for the desktop."""

    def __init__(self, master: tk.Misc, theme: Theme, config: ConfigManager, **kwargs):
        super().__init__(master, theme, config, **kwargs)
        self._build_ui()

    def get_title(self) -> str:
        return "DESK CLOCK"

    def get_preferred_size(self) -> Tuple[int, int]:
        s = getattr(self, "scale_factor", 1.0)
        return (max(180, int(280 * s)), max(90, int(140 * s)))

    def _build_ui(self) -> None:
        s = getattr(self, "scale_factor", 1.0)
        self.container = tk.Frame(self, bg=self.theme.bg)
        self.container.pack(expand=True, fill=tk.BOTH, padx=max(8, int(16 * s)), pady=max(6, int(12 * s)))

        # Time display
        self.time_label = tk.Label(
            self.container,
            text="00:00:00",
            font=(self.theme.font_family, max(14, int(26 * s)), "bold"),
            fg=self.theme.text_primary,
            bg=self.theme.bg
        )
        self.time_label.pack(anchor="center", pady=(max(2, int(4 * s)), 0))

        # Date display
        self.date_label = tk.Label(
            self.container,
            text="Monday, Jan 01 2026",
            font=(self.theme.font_family, max(7, int(9 * s)), "bold"),
            fg=self.theme.accent,
            bg=self.theme.bg
        )
        self.date_label.pack(anchor="center", pady=(max(2, int(4 * s)), max(2, int(4 * s))))

        # Week & day badge
        self.badge_label = tk.Label(
            self.container,
            text="WEEK 01 • DAY 001",
            font=(self.theme.font_family, max(6, int(8 * s))),
            fg=self.theme.text_muted,
            bg=self.theme.bg
        )
        self.badge_label.pack(anchor="center")

    def on_scale_change(self, scale: float) -> None:
        """Dynamically adjust fonts when scale changes."""
        self.scale_factor = scale
        s = scale
        if hasattr(self, "container"):
            self.container.pack_configure(padx=max(8, int(16 * s)), pady=max(6, int(12 * s)))
        if hasattr(self, "time_label"):
            self.time_label.configure(font=(self.theme.font_family, max(14, int(26 * s)), "bold"))
        if hasattr(self, "date_label"):
            self.date_label.configure(font=(self.theme.font_family, max(7, int(9 * s)), "bold"))
        if hasattr(self, "badge_label"):
            self.badge_label.configure(font=(self.theme.font_family, max(6, int(8 * s))))

    def on_update(self) -> None:
        """Update clock labels with current timestamp."""
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        date_str = now.strftime("%A, %b %d %Y")
        week_num = now.isocalendar()[1]
        day_of_year = now.timetuple().tm_yday
        badge_str = f"WEEK {week_num:02d} • DAY {day_of_year:03d}"

        self.time_label.configure(text=time_str)
        self.date_label.configure(text=date_str)
        self.badge_label.configure(text=badge_str)

    def on_theme_change(self, new_theme: Theme) -> None:
        super().on_theme_change(new_theme)
        self.time_label.configure(bg=new_theme.bg, fg=new_theme.text_primary)
        self.date_label.configure(bg=new_theme.bg, fg=new_theme.accent)
        self.badge_label.configure(bg=new_theme.bg, fg=new_theme.text_muted)
