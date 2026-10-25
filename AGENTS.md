# 🤖 AGENTS.md — Agent & Developer Guide for DeskGraph

Welcome, AI coding agent or human contributor! This document provides technical context, architecture decisions, lifecycle rules, and common Tkinter gotchas needed to work on **DeskGraph** safely, quickly, and effectively.

---

## 🧭 Project Overview & Design Philosophy

**DeskGraph** is a lightweight, frameless floating desktop widget application written in Python.

### Core Principles:
1. **Zero Mandatory Dependencies**: Core functionality (widgets, draggable floating windows, canvas rendering, config persistence) MUST run using only Python's standard library (`tkinter`, `urllib`, `json`, `threading`, `queue`). Optional features (like hardware CPU monitoring) may use `psutil` behind a graceful fallback.
2. **Pure Canvas Visuals**: Sparklines, status badges, and cards are rendered natively via `tkinter.Canvas` without heavy external graphing libraries (like `matplotlib` or `pyqt`).
3. **Multi-Window Support**: All windows are managed by a singleton `WindowManager`. Multiple independent floating cards can coexist simultaneously.
4. **Vibe-Coded & AI-Friendly**: Clean, modular, well-documented code designed for fast iterative agentic development.

---

## 🗺️ Codebase Map

| File / Directory | Purpose | Key Responsibilities |
| :--- | :--- | :--- |
| [`main.py`](main.py) | Application Entrypoint | CLI parsing (`argparse`), `WindowManager` instantiation, startup options |
| [`src/core/window.py`](src/core/window.py) | Window & Multi-Window Engine | `FloatingWidgetWindow` (Toplevel), `WindowManager` (Tk root), dragging, menus, geometry |
| [`src/core/config.py`](src/core/config.py) | Configuration Manager | JSON storage in `config/settings.json`, default fallbacks, auto-saving |
| [`src/utils/theme.py`](src/utils/theme.py) | Theme System | `Theme` dataclass, 10 curated Dark & Light palettes |
| [`src/utils/canvas_helpers.py`](src/utils/canvas_helpers.py) | Canvas Render Helpers | `draw_sparkline`, `draw_rounded_rect` |
| [`src/widgets/base.py`](src/widgets/base.py) | Widget Abstract Base Class | `BaseWidget` lifecycle hooks, dimensions, scaling interface |
| [`src/widgets/registry.py`](src/widgets/registry.py) | Modular Widget Registry | `WIDGET_REGISTRY` dict mapping keys (e.g. `"currency"`) to classes |
| [`src/widgets/currency_widget.py`](src/widgets/currency_widget.py) | Live Currency FX Widget | USD/IDR rates, dual API (Frankfurter & API.co.id), sparkline, minimal mode |
| [`src/widgets/graph_widget.py`](src/widgets/graph_widget.py) | System / Activity Graph | Real-time CPU monitor (`psutil`) with simulated fallback |
| [`src/widgets/clock_widget.py`](src/widgets/clock_widget.py) | Digital Clock Widget | Minimalist time, date, week display |
| [`build.bat`](build.bat) | Windows PyInstaller Script | One-click `--noconsole` portable `.exe` compiler |

---

## ⚠️ Critical Rules & Gotchas (Read Before Modifying Code)

### 1. 🧵 Tkinter Thread Safety (Strict Rule)
- **Tkinter is NOT thread-safe**.
- **NEVER** modify Tkinter UI elements, call `self.configure()`, or call `self.after()` directly from background threads (e.g. inside `_fetch_worker()`).
- **Pattern to follow**:
  - Run network requests or heavy tasks in a `threading.Thread(target=..., daemon=True)`.
  - Put results into a `queue.Queue()`.
  - Drain the queue on the main thread inside `on_update()` or via an existing periodic timer.

### 2. 🪟 Menu & Window Lifecycle Destruction (Strict Rule)
- When a user clicks **"Close This Window"** from a popup context menu (`tk_popup`), **NEVER** destroy the window synchronously inside the menu callback. Doing so destroys the window while `tk_popup` is still active in the C event loop, throwing:
  ```text
  _tkinter.TclError: can't invoke "tk" command: application has been destroyed
  ```
- **Pattern to follow**:
  - Defer the destruction by scheduling it on the main loop:
    ```python
    self.context_menu.add_command(label="Close This Window", command=lambda: self.after(10, self.close_app))
    ```
  - Always guard `tk_popup` in `try...except (tk.TclError, Exception): pass` with `finally: self.context_menu.grab_release()`.
  - Always return `"break"` from right-click event handlers to prevent event bubbling.
  - Guard `close_app()` with an `_is_closing` boolean to avoid re-entrant calls.

### 3. 📐 Dynamic Scaling & Dimensions
DeskGraph supports 5 window size presets (`very_small`, `small`, `medium`, `large`, `very_big`) ranging from 65% to 165% scale.
- When creating or modifying widgets:
  - Inherit from [`BaseWidget`](src/widgets/base.py).
  - Use `self.scale_factor` to compute font sizes, canvas dimensions, and paddings:
    ```python
    s = getattr(self, "scale_factor", 1.0)
    font_size = max(11, int(18 * s))
    ```
  - Implement `on_scale_change(self, scale: float)` to reconfigure fonts and resize canvases when the user changes size presets dynamically.
  - In `get_preferred_size(self) -> Tuple[int, int]`, multiply base width and height by `self.scale_factor`.

### 4. 🔒 Security & Sensitive Credentials
- **NEVER hardcode API keys or tokens in code files**.
- Keys must be loaded from `config/settings.json` (which is in `.gitignore`) or from environment variables (e.g. `API_CO_ID_KEY`).
- Provide placeholder examples in [`config/settings.example.json`](config/settings.example.json).

### 5. 🪟 Multi-Window Lifecycle (`WindowManager`)
- Each `FloatingWidgetWindow` is a `tk.Toplevel` attached to a hidden `tk.Tk` root managed by `WindowManager`.
- Closing a single window should call `self.manager.remove_window(self)`.
- When `len(self.windows) == 0`, `WindowManager` calls `self.root.quit()` followed by `self.root.destroy()` to exit gracefully.

---

## 🛠️ How to Add a New Widget (Step-by-Step)

To add a new widget (e.g. a Pomodoro timer, Crypto tracker, or Weather card):

### 1. Create `src/widgets/<name>_widget.py`
```python
import tkinter as tk
from typing import Tuple
from .base import BaseWidget
from ..utils.theme import Theme
from ..core.config import ConfigManager

class MyCustomWidget(BaseWidget):
    """My custom desktop widget."""

    def __init__(self, master: tk.Misc, theme: Theme, config: ConfigManager, **kwargs):
        super().__init__(master, theme, config, **kwargs)
        self._build_ui()

    def get_title(self) -> str:
        return "MY WIDGET"

    def get_preferred_size(self) -> Tuple[int, int]:
        s = getattr(self, "scale_factor", 1.0)
        return (int(280 * s), int(140 * s))

    def _build_ui(self) -> None:
        s = getattr(self, "scale_factor", 1.0)
        self.label = tk.Label(
            self,
            text="Hello World",
            font=(self.theme.font_family, max(12, int(18 * s)), "bold"),
            fg=self.theme.accent,
            bg=self.theme.bg
        )
        self.label.pack(expand=True, fill=tk.BOTH, padx=12, pady=12)

    def on_update(self) -> None:
        """Periodic tick (called ~1/sec). Update state/UI here."""
        pass

    def on_theme_change(self, new_theme: Theme) -> None:
        super().on_theme_change(new_theme)
        self.label.configure(bg=new_theme.bg, fg=new_theme.accent)

    def on_scale_change(self, scale: float) -> None:
        """Rescale fonts and padding when window size changes."""
        self.scale_factor = scale
        s = scale
        self.label.configure(font=(self.theme.font_family, max(12, int(18 * s)), "bold"))
```

### 2. Register in [`src/widgets/registry.py`](src/widgets/registry.py)
```python
from .my_custom_widget import MyCustomWidget

WIDGET_REGISTRY = {
    "currency": CurrencyWidget,
    "graph": GraphWidget,
    "clock": ClockWidget,
    "my_widget": MyCustomWidget,  # <-- Added
}
```

### 3. Test Your Widget
```bash
python main.py --widget my_widget
```

---

## 🧪 Testing & Verification Workflows

When implementing fixes or new features, verify non-interactively using Python one-liners:

```bash
# 1. Verify syntax and imports
python -c "import main; print('Imports OK')"

# 2. Verify window creation and size scaling
python -c "from src.core.window import WindowManager; wm = WindowManager.get_instance(); win = wm.create_window(); win.set_window_size('very_small'); win.set_window_size('very_big'); win.destroy(); wm.root.destroy(); print('Scaling OK')"

# 3. Verify clean context menu closing without TclError
python -c "from src.core.window import WindowManager; wm = WindowManager.get_instance(); win = wm.create_window(); win.after(200, lambda: win.context_menu.invoke('Close This Window')); wm.run(); print('Exited cleanly')"
```

---

## 📦 PyInstaller Packaging Notes

When updating dependencies or imports:
- Verify that [`build.bat`](build.bat) and [`DeskGraph.spec`](DeskGraph.spec) bundle all required modules.
- Ensure that paths handle `sys.frozen` correctly:
  ```python
  if getattr(sys, "frozen", False):
      base_dir = Path(sys.executable).resolve().parent
  else:
      base_dir = Path(__file__).resolve().parent
  ```
- Always test that DeskGraph runs without a console window attached.
