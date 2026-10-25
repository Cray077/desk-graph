"""Canvas drawing helpers for modern rounded shapes and charts in Tkinter."""

import tkinter as tk
from typing import List, Tuple

def draw_rounded_rect(
    canvas: tk.Canvas,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    radius: float = 12,
    **kwargs
) -> int:
    """Draw a smooth rounded rectangle polygon on a Tkinter Canvas."""
    # Ensure radius does not exceed dimensions
    max_radius = min((x2 - x1) / 2, (y2 - y1) / 2)
    radius = min(radius, max_radius)
    
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

def draw_sparkline(
    canvas: tk.Canvas,
    data: List[float],
    x: float,
    y: float,
    width: float,
    height: float,
    min_val: float = 0.0,
    max_val: float = 100.0,
    line_color: str = "#6366f1",
    line_width: int = 2,
    fill_color: str = "",
    baseline_color: str = "#2e3247"
) -> None:
    """Draw a sparkline graph with optional area under curve on a canvas."""
    if not data or len(data) < 2:
        return

    val_range = max_val - min_val
    if val_range <= 0:
        val_range = 1.0

    step_x = width / (len(data) - 1)
    
    # Calculate coordinate pairs
    coords: List[Tuple[float, float]] = []
    for i, val in enumerate(data):
        clamped_val = max(min_val, min(max_val, val))
        norm = (clamped_val - min_val) / val_range
        px = x + (i * step_x)
        py = (y + height) - (norm * height)
        coords.append((px, py))

    # Optional grid/baseline
    if baseline_color:
        canvas.create_line(
            x, y + height, x + width, y + height,
            fill=baseline_color, width=1, dash=(2, 4)
        )
        canvas.create_line(
            x, y + height / 2, x + width, y + height / 2,
            fill=baseline_color, width=1, dash=(1, 5)
        )

    # Optional area fill under the line
    if fill_color:
        polygon_points = [x, y + height]
        for px, py in coords:
            polygon_points.extend([px, py])
        polygon_points.extend([coords[-1][0], y + height])
        canvas.create_polygon(polygon_points, fill=fill_color, outline="")

    # Draw line segments
    flattened_points = []
    for px, py in coords:
        flattened_points.extend([px, py])

    canvas.create_line(
        flattened_points,
        fill=line_color,
        width=line_width,
        smooth=True,
        capstyle=tk.ROUND,
        joinstyle=tk.ROUND
    )

    # Draw a highlighted dot on the latest value
    last_x, last_y = coords[-1]
    dot_r = line_width + 2
    canvas.create_oval(
        last_x - dot_r, last_y - dot_r,
        last_x + dot_r, last_y + dot_r,
        fill=line_color, outline="#ffffff", width=1
    )
