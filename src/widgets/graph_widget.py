"""Real-time sparkline graph widget for desktop monitoring."""

import tkinter as tk
import math
import random
from typing import List, Tuple
from .base import BaseWidget
from ..utils.theme import Theme
from ..utils.canvas_helpers import draw_sparkline, draw_rounded_rect
from ..core.config import ConfigManager

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class GraphWidget(BaseWidget):
    """A sleek sparkline graph desktop widget displaying live activity or CPU load."""

    def __init__(self, master: tk.Misc, theme: Theme, config: ConfigManager, **kwargs):
        super().__init__(master, theme, config, **kwargs)
        
        # Historical metrics buffer
        self.max_points = 24
        self.history: List[float] = [20.0 + 5.0 * math.sin(i * 0.4) for i in range(self.max_points)]
        self._sim_phase = 0.0

        # Build UI
        self._build_ui()

    def get_title(self) -> str:
        return "SYSTEM MONITOR" if HAS_PSUTIL else "ACTIVITY GRAPH"

    def get_preferred_size(self) -> Tuple[int, int]:
        s = getattr(self, "scale_factor", 1.0)
        return (max(200, int(300 * s)), max(120, int(175 * s)))

    def _build_ui(self) -> None:
        s = getattr(self, "scale_factor", 1.0)

        # Top stats header
        self.header_frame = tk.Frame(self, bg=self.theme.bg)
        self.header_frame.pack(fill=tk.X, padx=max(6, int(12 * s)), pady=(max(4, int(8 * s)), max(2, int(4 * s))))

        # Main value label
        self.val_label = tk.Label(
            self.header_frame,
            text="--%",
            font=(self.theme.font_family, max(12, int(20 * s)), "bold"),
            fg=self.theme.accent,
            bg=self.theme.bg
        )
        self.val_label.pack(side=tk.LEFT)

        # Sub-stats (Avg & Peak)
        self.sub_frame = tk.Frame(self.header_frame, bg=self.theme.bg)
        self.sub_frame.pack(side=tk.RIGHT, pady=max(1, int(2 * s)))

        self.avg_label = tk.Label(
            self.sub_frame,
            text="AVG: --%",
            font=(self.theme.font_family, max(6, int(8 * s))),
            fg=self.theme.text_secondary,
            bg=self.theme.bg
        )
        self.avg_label.pack(anchor="e")

        self.peak_label = tk.Label(
            self.sub_frame,
            text="PEAK: --%",
            font=(self.theme.font_family, max(6, int(8 * s))),
            fg=self.theme.text_muted,
            bg=self.theme.bg
        )
        self.peak_label.pack(anchor="e")

        # Canvas for sparkline
        self.canvas_width = max(160, int(276 * s))
        self.canvas_height = max(50, int(85 * s))
        self.canvas = tk.Canvas(
            self,
            width=self.canvas_width,
            height=self.canvas_height,
            bg=self.theme.card_bg,
            highlightthickness=1,
            highlightbackground=self.theme.card_border
        )
        self.canvas.pack(padx=max(6, int(12 * s)), pady=(max(1, int(2 * s)), max(3, int(6 * s))))

        # Bottom info pill
        self.footer = tk.Label(
            self,
            text="Mode: " + ("Live CPU (psutil)" if HAS_PSUTIL else "Simulation (install psutil for CPU)"),
            font=(self.theme.font_family, max(5, int(7 * s))),
            fg=self.theme.text_muted,
            bg=self.theme.bg
        )
        self.footer.pack(side=tk.BOTTOM, pady=(0, max(3, int(6 * s))))

    def on_scale_change(self, scale: float) -> None:
        """Dynamically adjust fonts and sparkline dimensions when scale changes."""
        self.scale_factor = scale
        s = scale
        if hasattr(self, "val_label"):
            self.val_label.configure(font=(self.theme.font_family, max(12, int(20 * s)), "bold"))
        if hasattr(self, "avg_label"):
            self.avg_label.configure(font=(self.theme.font_family, max(6, int(8 * s))))
        if hasattr(self, "peak_label"):
            self.peak_label.configure(font=(self.theme.font_family, max(6, int(8 * s))))
        if hasattr(self, "canvas"):
            self.canvas_width = max(160, int(276 * s))
            self.canvas_height = max(50, int(85 * s))
            self.canvas.configure(width=self.canvas_width, height=self.canvas_height)
        if hasattr(self, "footer"):
            self.footer.configure(font=(self.theme.font_family, max(5, int(7 * s))))
        if hasattr(self, "history") and len(self.history) > 0:
            self._render_graph()

    def _fetch_next_value(self) -> float:
        """Fetch the next metric point (CPU percentage or realistic simulation)."""
        if HAS_PSUTIL:
            try:
                return float(psutil.cpu_percent(interval=None))
            except Exception:
                pass

        # Realistic oscillating data with noise if psutil is not installed
        self._sim_phase += 0.25
        base = 35.0 + 20.0 * math.sin(self._sim_phase)
        noise = random.uniform(-6.0, 6.0)
        return max(5.0, min(95.0, round(base + noise, 1)))

    def on_update(self) -> None:
        """Called periodically to refresh the graph and numerical readouts."""
        val = self._fetch_next_value()
        self.history.append(val)
        if len(self.history) > self.max_points:
            self.history.pop(0)

        # Update stats
        avg_val = sum(self.history) / len(self.history)
        peak_val = max(self.history)

        self.val_label.configure(text=f"{val:.1f}%")
        self.avg_label.configure(text=f"AVG: {avg_val:.1f}%")
        self.peak_label.configure(text=f"PEAK: {peak_val:.1f}%")

        # Color tint based on load
        if val > 80:
            self.val_label.configure(fg=self.theme.danger)
        elif val > 50:
            self.val_label.configure(fg=self.theme.accent_secondary)
        else:
            self.val_label.configure(fg=self.theme.accent)

        # Redraw canvas
        self._render_graph()

    def _render_graph(self) -> None:
        self.canvas.delete("all")

        # Render subtle sparkline graph
        draw_sparkline(
            canvas=self.canvas,
            data=self.history,
            x=8,
            y=8,
            width=self.canvas_width - 16,
            height=self.canvas_height - 16,
            min_val=0.0,
            max_val=100.0,
            line_color=self.theme.accent,
            line_width=2,
            fill_color=self.theme.card_bg, # Can be enhanced or empty
            baseline_color=self.theme.card_border
        )

    def on_theme_change(self, new_theme: Theme) -> None:
        super().on_theme_change(new_theme)
        self.header_frame.configure(bg=new_theme.bg)
        self.sub_frame.configure(bg=new_theme.bg)
        self.val_label.configure(bg=new_theme.bg, fg=new_theme.accent)
        self.avg_label.configure(bg=new_theme.bg, fg=new_theme.text_secondary)
        self.peak_label.configure(bg=new_theme.bg, fg=new_theme.text_muted)
        self.canvas.configure(
            bg=new_theme.card_bg,
            highlightbackground=new_theme.card_border
        )
        self.footer.configure(bg=new_theme.bg, fg=new_theme.text_muted)
        self._render_graph()
