"""Floating, draggable, borderless desktop widget window implementation with multi-window support."""

import tkinter as tk
from typing import Optional, List
from .config import ConfigManager
from ..utils.theme import THEMES, DEFAULT_THEME, Theme
from ..widgets.base import BaseWidget
from ..widgets.registry import WIDGET_REGISTRY

WINDOW_SIZE_PRESETS = [
    ("very_small", "Very Small (65%)", 0.65),
    ("small", "Small (80%)", 0.80),
    ("medium", "Medium (100% / Default)", 1.00),
    ("large", "Large (130%)", 1.30),
    ("very_big", "Very Big (165%)", 1.65),
]


class WindowManager:
    """Manages multi-window lifecycle for floating desktop widgets."""
    _instance: Optional["WindowManager"] = None

    def __init__(self, config: ConfigManager):
        WindowManager._instance = self
        self.config = config
        self.root = tk.Tk()
        self.root.withdraw()  # Hidden master controller
        self.windows: List["FloatingWidgetWindow"] = []

    @classmethod
    def get_instance(cls, config: Optional[ConfigManager] = None) -> "WindowManager":
        if cls._instance is None:
            cls._instance = WindowManager(config or ConfigManager())
        return cls._instance

    def create_window(
        self,
        widget_key: Optional[str] = None,
        x: Optional[int] = None,
        y: Optional[int] = None
    ) -> "FloatingWidgetWindow":
        """Spawn a new floating desktop widget window."""
        win = FloatingWidgetWindow(
            master=self.root,
            config=self.config,
            widget_key=widget_key,
            x=x,
            y=y,
            manager=self
        )
        self.windows.append(win)
        return win

    def remove_window(self, win: "FloatingWidgetWindow") -> None:
        """Remove window reference. If all windows are closed, terminate process."""
        if win in self.windows:
            self.windows.remove(win)
        if len(self.windows) == 0:
            try:
                self.root.quit()
            except Exception:
                pass
            try:
                self.root.destroy()
            except Exception:
                pass

    def run(self) -> None:
        """Run the main event loop."""
        self.root.mainloop()


class FloatingWidgetWindow(tk.Toplevel):
    """Floating desktop widget window providing frameless dragging, transparency,

    always-on-top, multi-window support, and right-click settings.
    """

    def __init__(
        self,
        master: Optional[tk.Misc] = None,
        config: Optional[ConfigManager] = None,
        widget_key: Optional[str] = None,
        x: Optional[int] = None,
        y: Optional[int] = None,
        manager: Optional[WindowManager] = None
    ):
        if config is None:
            config = ConfigManager()
        self.config = config

        if manager is None:
            manager = WindowManager.get_instance(config)
        self.manager = manager

        if master is None:
            master = manager.root

        super().__init__(master)

        # Load theme from config
        theme_name = self.config.get("theme_name", "obsidian")
        self.theme: Theme = THEMES.get(theme_name, DEFAULT_THEME)

        # Active widget reference
        self.active_widget: Optional[BaseWidget] = None
        self._timer_id: Optional[str] = None
        self._drag_start_x = 0
        self._drag_start_y = 0
        self.scale_factor: float = float(self.config.get("scale_factor", 1.0))

        # Window configuration
        self._setup_window_properties(x, y)
        self._build_title_bar()
        self._setup_context_menu()
        self._setup_event_bindings()

        # Mount initial widget
        initial_widget_key = widget_key or self.config.get("active_widget", "currency")
        self.mount_widget(initial_widget_key)

        # Start periodic update loop
        self._start_update_loop()

    def mainloop(self, *args, **kwargs) -> None:
        """Backward-compatible mainloop delegation to WindowManager."""
        if self.manager and self.manager.root:
            self.manager.run()
        else:
            super().mainloop(*args, **kwargs)

    def _setup_window_properties(self, custom_x: Optional[int] = None, custom_y: Optional[int] = None) -> None:
        """Apply frameless, transparency, and topmost window attributes."""
        self.title("Desk Widget")
        self.overrideredirect(True)  # Frameless
        self.configure(bg=self.theme.card_border)

        # Always on top
        is_topmost = self.config.get("always_on_top", True)
        self.wm_attributes("-topmost", is_topmost)

        # Transparency (alpha)
        alpha = self.config.get("alpha", 0.95)
        self.wm_attributes("-alpha", alpha)

        # Position (custom or config)
        x = custom_x if custom_x is not None else self.config.get("x", 120)
        y = custom_y if custom_y is not None else self.config.get("y", 120)

        # Guard against offscreen positions
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = max(0, min(x, screen_w - 100))
        y = max(0, min(y, screen_h - 100))
        self.geometry(f"+{x}+{y}")

    def _build_title_bar(self) -> None:
        """Create sleek minimal title bar with drag handle, add window, pin, and close buttons."""
        self.title_bar = tk.Frame(self, bg=self.theme.header_bg, height=26)
        self.title_bar.pack(side=tk.TOP, fill=tk.X, padx=1, pady=(1, 0))
        self.title_bar.pack_propagate(False)

        # Drag handle icon / grip
        self.grip_icon = tk.Label(
            self.title_bar,
            text="⠿",
            font=(self.theme.font_family, 10),
            fg=self.theme.text_muted,
            bg=self.theme.header_bg,
            cursor="fleur"
        )
        self.grip_icon.pack(side=tk.LEFT, padx=(8, 4))

        # Title label
        self.title_label = tk.Label(
            self.title_bar,
            text="WIDGET",
            font=(self.theme.font_family, 8, "bold"),
            fg=self.theme.text_secondary,
            bg=self.theme.header_bg,
            cursor="fleur"
        )
        self.title_label.pack(side=tk.LEFT, padx=2)

        # Close button (✕)
        self.btn_close = tk.Label(
            self.title_bar,
            text="✕",
            font=(self.theme.font_family, 9),
            fg=self.theme.text_muted,
            bg=self.theme.header_bg,
            cursor="hand2",
            padx=6
        )
        self.btn_close.pack(side=tk.RIGHT, padx=(0, 2))
        self.btn_close.bind("<Button-1>", lambda e: self.close_app())
        self.btn_close.bind("<Enter>", lambda e: self.btn_close.configure(fg=self.theme.danger))
        self.btn_close.bind("<Leave>", lambda e: self.btn_close.configure(fg=self.theme.text_muted))

        # Pin / Always-on-top button (📌)
        self.btn_pin = tk.Label(
            self.title_bar,
            text="📌",
            font=(self.theme.font_family, 8),
            fg=self.theme.accent if self.config.get("always_on_top", True) else self.theme.text_muted,
            bg=self.theme.header_bg,
            cursor="hand2",
            padx=4
        )
        self.btn_pin.pack(side=tk.RIGHT)
        self.btn_pin.bind("<Button-1>", lambda e: self.toggle_topmost())

        # New window button (➕)
        self.btn_new = tk.Label(
            self.title_bar,
            text="➕",
            font=(self.theme.font_family, 8),
            fg=self.theme.text_muted,
            bg=self.theme.header_bg,
            cursor="hand2",
            padx=4
        )
        self.btn_new.pack(side=tk.RIGHT)
        self.btn_new.bind("<Button-1>", self._show_add_window_popup)
        self.btn_new.bind("<Enter>", lambda e: self.btn_new.configure(fg=self.theme.accent))
        self.btn_new.bind("<Leave>", lambda e: self.btn_new.configure(fg=self.theme.text_muted))

        # Main content container frame
        self.content_container = tk.Frame(self, bg=self.theme.bg)
        self.content_container.pack(fill=tk.BOTH, expand=True, padx=1, pady=(0, 1))

        # Apply initial title bar scale
        self._apply_titlebar_scale()

        # Check initial titlebar visibility
        if not self.config.get("show_titlebar", True):
            self.title_bar.pack_forget()

    def _show_add_window_popup(self, event: tk.Event) -> str:
        """Show dropdown popup to choose which widget to open in a new window."""
        menu = tk.Menu(self, tearoff=0, bg="#1e2029", fg="#f8fafc", activebackground=self.theme.accent)
        menu.add_command(label="🪙 New Currency Window", command=lambda: self.spawn_new_window("currency"))
        menu.add_command(label="📊 New Graph Window", command=lambda: self.spawn_new_window("graph"))
        menu.add_command(label="🕒 New Clock Window", command=lambda: self.spawn_new_window("clock"))
        try:
            menu.tk_popup(event.x_root, event.y_root + 15)
        except (tk.TclError, Exception):
            pass
        finally:
            try:
                menu.grab_release()
            except Exception:
                pass
        return "break"

    def spawn_new_window(self, widget_key: str) -> "FloatingWidgetWindow":
        """Open a new floating widget window beside the current window."""
        new_x = self.winfo_x() + 35
        new_y = self.winfo_y() + 35
        if self.manager:
            return self.manager.create_window(widget_key=widget_key, x=new_x, y=new_y)
        return WindowManager.get_instance(self.config).create_window(widget_key=widget_key, x=new_x, y=new_y)

    def _setup_context_menu(self) -> None:
        """Create right-click context menu for quick settings."""
        self.context_menu = tk.Menu(self, tearoff=0, bg="#1e2029", fg="#f8fafc", activebackground=self.theme.accent)

        # Topmost toggle
        self.topmost_var = tk.BooleanVar(value=self.config.get("always_on_top", True))
        self.context_menu.add_checkbutton(
            label="Always On Top",
            variable=self.topmost_var,
            command=self.toggle_topmost
        )

        # Lock position toggle
        self.lock_var = tk.BooleanVar(value=self.config.get("locked", False))
        self.context_menu.add_checkbutton(
            label="Lock Position",
            variable=self.lock_var,
            command=self.toggle_lock
        )

        # Minimal View toggle (only shows current rates)
        self.minimal_var = tk.BooleanVar(value=self.config.get("minimal_view", False))
        self.context_menu.add_checkbutton(
            label="Minimal View (Rates Only)",
            variable=self.minimal_var,
            command=self.toggle_minimal_view
        )

        # Show Title Bar toggle
        self.titlebar_var = tk.BooleanVar(value=self.config.get("show_titlebar", True))
        self.context_menu.add_checkbutton(
            label="Show Title Bar",
            variable=self.titlebar_var,
            command=self.toggle_titlebar
        )

        # Open New Window Submenu
        new_win_menu = tk.Menu(self.context_menu, tearoff=0, bg="#1e2029", fg="#f8fafc", activebackground=self.theme.accent)
        for key in WIDGET_REGISTRY.keys():
            icon = "🪙" if key == "currency" else ("📊" if key == "graph" else "🕒")
            new_win_menu.add_command(
                label=f"{icon} {key.capitalize()} Window",
                command=lambda k=key: self.spawn_new_window(k)
            )
        self.context_menu.add_cascade(label="➕ Open New Window", menu=new_win_menu)

        # Window Size Submenu (Very Small to Very Big)
        size_menu = tk.Menu(self.context_menu, tearoff=0, bg="#1e2029", fg="#f8fafc", activebackground=self.theme.accent)
        self.size_var = tk.StringVar(value=self.config.get("window_size", "medium"))
        for s_key, s_label, _ in WINDOW_SIZE_PRESETS:
            size_menu.add_radiobutton(
                label=s_label,
                variable=self.size_var,
                value=s_key,
                command=lambda k=s_key: self.set_window_size(k)
            )
        self.context_menu.add_cascade(label="Window Size", menu=size_menu)

        # Opacity Submenu
        opacity_menu = tk.Menu(self.context_menu, tearoff=0, bg="#1e2029", fg="#f8fafc", activebackground=self.theme.accent)
        for pct in [100, 85, 70, 50, 30]:
            opacity_menu.add_command(
                label=f"{pct}%",
                command=lambda p=pct: self.set_opacity(p / 100.0)
            )
        self.context_menu.add_cascade(label="Opacity", menu=opacity_menu)

        # Widget Switcher Submenu
        widget_menu = tk.Menu(self.context_menu, tearoff=0, bg="#1e2029", fg="#f8fafc", activebackground=self.theme.accent)
        for key in WIDGET_REGISTRY.keys():
            widget_menu.add_command(
                label=key.capitalize(),
                command=lambda k=key: self.mount_widget(k)
            )
        self.context_menu.add_cascade(label="Switch Widget", menu=widget_menu)

        # Themes Submenu (Categorized by Dark and Light)
        theme_menu = tk.Menu(self.context_menu, tearoff=0, bg="#1e2029", fg="#f8fafc", activebackground=self.theme.accent)
        self.theme_var = tk.StringVar(value=self.config.get("theme_name", "obsidian"))

        theme_menu.add_command(label="── DARK PALETTES ──", state="disabled")
        for t_key, t_val in THEMES.items():
            if t_val.is_dark:
                theme_menu.add_radiobutton(
                    label=f"  {t_val.name}",
                    variable=self.theme_var,
                    value=t_key,
                    command=lambda k=t_key: self.set_theme(k)
                )

        theme_menu.add_separator()
        theme_menu.add_command(label="── LIGHT PALETTES ──", state="disabled")
        for t_key, t_val in THEMES.items():
            if not t_val.is_dark:
                theme_menu.add_radiobutton(
                    label=f"  {t_val.name}",
                    variable=self.theme_var,
                    value=t_key,
                    command=lambda k=t_key: self.set_theme(k)
                )

        self.context_menu.add_cascade(label="Theme Palette", menu=theme_menu)

        # Auto Refresh Submenu (in units of seconds)
        refresh_menu = tk.Menu(self.context_menu, tearoff=0, bg="#1e2029", fg="#f8fafc", activebackground=self.theme.accent)
        self.refresh_interval_var = tk.IntVar(value=self.config.get("currency_refresh_seconds", 30))
        for sec in [5, 10, 15, 30, 60, 120, 300]:
            label = f"{sec} seconds" if sec < 60 else f"{sec} seconds ({sec // 60}m)"
            refresh_menu.add_radiobutton(
                label=label,
                variable=self.refresh_interval_var,
                value=sec,
                command=lambda s=sec: self.set_currency_refresh_interval(s)
            )
        self.context_menu.add_cascade(label="Auto Refresh (Seconds)", menu=refresh_menu)

        # Currency API Provider Submenu
        provider_menu = tk.Menu(self.context_menu, tearoff=0, bg="#1e2029", fg="#f8fafc", activebackground=self.theme.accent)
        self.provider_var = tk.StringVar(value=self.config.get("currency_provider", "frankfurter"))
        provider_options = [
            ("frankfurter", "Frankfurter (Open API)"),
            ("api_co_id", "API.co.id (API Key)")
        ]
        for p_key, p_name in provider_options:
            provider_menu.add_radiobutton(
                label=p_name,
                variable=self.provider_var,
                value=p_key,
                command=lambda k=p_key: self.set_currency_provider(k)
            )
        self.context_menu.add_cascade(label="Currency API Source", menu=provider_menu)

        self.context_menu.add_separator()
        self.context_menu.add_command(label="Center on Screen", command=self.center_window)
        self.context_menu.add_command(label="Close This Window", command=lambda: self.after(10, self.close_app))

    def _setup_event_bindings(self) -> None:
        """Bind drag handlers and right click events."""
        # Right click for context menu
        self.bind("<Button-3>", self._show_context_menu)
        self.title_bar.bind("<Button-3>", self._show_context_menu)
        self.content_container.bind("<Button-3>", self._show_context_menu)

        # Dragging bindings (can drag via title bar or grip)
        for elem in [self.title_bar, self.title_label, self.grip_icon]:
            elem.bind("<Button-1>", self._on_drag_start)
            elem.bind("<B1-Motion>", self._on_drag_motion)
            elem.bind("<ButtonRelease-1>", self._on_drag_end)

    def _show_context_menu(self, event: tk.Event) -> str:
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        except (tk.TclError, Exception):
            pass
        finally:
            try:
                self.context_menu.grab_release()
            except Exception:
                pass
        return "break"

    def _on_drag_start(self, event: tk.Event) -> None:
        if not self.config.get("locked", False):
            self._drag_start_x = event.x_root - self.winfo_x()
            self._drag_start_y = event.y_root - self.winfo_y()

    def _on_drag_motion(self, event: tk.Event) -> None:
        if not self.config.get("locked", False):
            new_x = event.x_root - self._drag_start_x
            new_y = event.y_root - self._drag_start_y
            self.geometry(f"+{new_x}+{new_y}")

    def _on_drag_end(self, event: tk.Event) -> None:
        if not self.config.get("locked", False):
            self.config.set("x", self.winfo_x(), auto_save=False)
            self.config.set("y", self.winfo_y(), auto_save=True)

    def mount_widget(self, widget_key: str) -> None:
        """Mount and display a specific widget by key."""
        widget_cls = WIDGET_REGISTRY.get(widget_key)
        if not widget_cls:
            print(f"[FloatingWidgetWindow] Unknown widget: '{widget_key}'")
            return

        # Destroy existing widget
        if self.active_widget:
            self.active_widget.on_destroy()
            self.active_widget.destroy()

        # Instantiate new widget
        self.active_widget = widget_cls(self.content_container, self.theme, self.config)
        if hasattr(self.active_widget, "set_scale"):
            self.active_widget.set_scale(self.scale_factor)
        self.active_widget.pack(fill=tk.BOTH, expand=True)

        # Adjust window dimensions to match widget preferred size + title bar
        self.update_window_geometry()
        self._bind_mouse_events_recursively(self.active_widget)

        # Update title text
        self.title_label.configure(text=self.active_widget.get_title().upper())

        # Notify widget of mount
        self.active_widget.on_mount()
        self.active_widget.on_update()

        # Persist selection
        self.config.set("active_widget", widget_key)

    def _start_update_loop(self) -> None:
        """Periodic timer loop for driving widget updates."""
        if self.active_widget:
            try:
                self.active_widget.on_update()
            except Exception as e:
                print(f"[FloatingWidgetWindow] Error in on_update: {e}")

        rate_ms = self.config.get("refresh_rate_ms", 1000)
        self._timer_id = self.after(rate_ms, self._start_update_loop)

    def toggle_topmost(self) -> None:
        current = self.config.get("always_on_top", True)
        new_val = not current
        self.config.set("always_on_top", new_val)
        self.wm_attributes("-topmost", new_val)
        self.topmost_var.set(new_val)
        self.btn_pin.configure(fg=self.theme.accent if new_val else self.theme.text_muted)

    def toggle_lock(self) -> None:
        current = self.config.get("locked", False)
        new_val = not current
        self.config.set("locked", new_val)
        self.lock_var.set(new_val)

    def set_opacity(self, alpha: float) -> None:
        alpha = max(0.2, min(1.0, alpha))
        self.config.set("alpha", alpha)
        self.wm_attributes("-alpha", alpha)

    def set_theme(self, theme_key: str) -> None:
        new_theme = THEMES.get(theme_key)
        if not new_theme:
            return
        self.theme = new_theme
        self.config.set("theme_name", theme_key)
        if hasattr(self, "theme_var"):
            self.theme_var.set(theme_key)

        # Update root styles
        self.configure(bg=new_theme.card_border)
        self.title_bar.configure(bg=new_theme.header_bg)
        self.grip_icon.configure(bg=new_theme.header_bg, fg=new_theme.text_muted)
        self.title_label.configure(bg=new_theme.header_bg, fg=new_theme.text_secondary)
        self.btn_close.configure(bg=new_theme.header_bg, fg=new_theme.text_muted)
        self.btn_new.configure(bg=new_theme.header_bg, fg=new_theme.text_muted)
        is_top = self.config.get("always_on_top", True)
        self.btn_pin.configure(bg=new_theme.header_bg, fg=new_theme.accent if is_top else new_theme.text_muted)
        self.content_container.configure(bg=new_theme.bg)

        # Notify active widget
        if self.active_widget:
            self.active_widget.on_theme_change(new_theme)

    def set_currency_refresh_interval(self, seconds: int) -> None:
        """Update auto-refresh interval for currency widget in seconds."""
        self.config.set("currency_refresh_seconds", seconds)
        self.refresh_interval_var.set(seconds)
        if hasattr(self.active_widget, "set_refresh_interval"):
            self.active_widget.set_refresh_interval(seconds)

    def set_currency_provider(self, provider_key: str) -> None:
        """Update active currency API provider and notify widget."""
        self.config.set("currency_provider", provider_key)
        self.provider_var.set(provider_key)
        if hasattr(self.active_widget, "set_provider"):
            self.active_widget.set_provider(provider_key)

    def toggle_minimal_view(self) -> None:
        """Toggle minimal view mode (rates only) and resize the window."""
        current = self.config.get("minimal_view", False)
        new_val = not current
        self.config.set("minimal_view", new_val)
        self.minimal_var.set(new_val)
        if hasattr(self.active_widget, "set_minimal_mode"):
            self.active_widget.set_minimal_mode(new_val)
        self.update_window_geometry()

    def toggle_titlebar(self) -> None:
        """Toggle the window title bar visibility."""
        current = self.config.get("show_titlebar", True)
        new_val = not current
        self.config.set("show_titlebar", new_val)
        self.titlebar_var.set(new_val)
        if new_val:
            self.title_bar.pack(side=tk.TOP, fill=tk.X, padx=1, pady=(1, 0), before=self.content_container)
        else:
            self.title_bar.pack_forget()
        self.update_window_geometry()

    def set_window_size(self, size_key: str) -> None:
        """Apply a window size preset (very small to very big) and rescale contents."""
        preset = next((item for item in WINDOW_SIZE_PRESETS if item[0] == size_key), None)
        if not preset:
            return
        _, _, scale = preset
        self.scale_factor = scale
        self.config.set("window_size", size_key, auto_save=False)
        self.config.set("scale_factor", scale, auto_save=True)
        self.size_var.set(size_key)

        self._apply_titlebar_scale()

        if self.active_widget and hasattr(self.active_widget, "set_scale"):
            self.active_widget.set_scale(scale)

        self.update_window_geometry()

    def _apply_titlebar_scale(self) -> None:
        """Rescale title bar height and button fonts according to scale factor."""
        s = getattr(self, "scale_factor", 1.0)
        if hasattr(self, "title_bar"):
            self.title_bar.configure(height=max(18, int(26 * s)))
        if hasattr(self, "title_label"):
            self.title_label.configure(font=(self.theme.font_family, max(6, int(8 * s)), "bold"))
        if hasattr(self, "grip_icon"):
            self.grip_icon.configure(font=(self.theme.font_family, max(7, int(10 * s))))
        if hasattr(self, "btn_close"):
            self.btn_close.configure(font=(self.theme.font_family, max(7, int(9 * s))))
        if hasattr(self, "btn_pin"):
            self.btn_pin.configure(font=(self.theme.font_family, max(6, int(8 * s))))
        if hasattr(self, "btn_new"):
            self.btn_new.configure(font=(self.theme.font_family, max(6, int(8 * s))))

    def update_window_geometry(self) -> None:
        """Resize the window to snugly match the active widget's preferred size."""
        if self.active_widget:
            w, h = self.active_widget.get_preferred_size()
            has_titlebar = self.config.get("show_titlebar", True)
            s = getattr(self, "scale_factor", 1.0)
            total_h = h + (max(18, int(26 * s)) if has_titlebar else 2)
            total_w = max(w, int(160 * s))
            curr_x = self.winfo_x()
            curr_y = self.winfo_y()

            # Prevent window from clipping offscreen when enlarged
            screen_w = self.winfo_screenwidth()
            screen_h = self.winfo_screenheight()
            if curr_x + total_w > screen_w:
                curr_x = max(0, screen_w - total_w - 20)
            if curr_y + total_h > screen_h:
                curr_y = max(0, screen_h - total_h - 20)

            self.geometry(f"{total_w}x{total_h}+{curr_x}+{curr_y}")

    def _bind_mouse_events_recursively(self, widget: tk.Misc) -> None:
        """Recursively bind drag and context menu handlers to widget elements."""
        for event, handler in [
            ("<Button-1>", self._on_drag_start),
            ("<B1-Motion>", self._on_drag_motion),
            ("<ButtonRelease-1>", self._on_drag_end),
            ("<Button-3>", self._show_context_menu),
        ]:
            try:
                widget.bind(event, handler, add="+")
            except Exception:
                pass
        for child in widget.winfo_children():
            self._bind_mouse_events_recursively(child)

    def center_window(self) -> None:
        """Center the widget on the primary screen."""
        self.update_idletasks()
        w = self.winfo_width()
        h = self.winfo_height()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        cx = (sw - w) // 2
        cy = (sh - h) // 2
        self.geometry(f"+{cx}+{cy}")
        self.config.set("x", cx, auto_save=False)
        self.config.set("y", cy, auto_save=True)

    def close_app(self) -> None:
        """Safely clean up timer and exit this window."""
        if getattr(self, "_is_closing", False):
            return
        self._is_closing = True
        if self._timer_id:
            try:
                self.after_cancel(self._timer_id)
            except Exception:
                pass
            self._timer_id = None
        if self.active_widget:
            try:
                self.active_widget.on_destroy()
            except Exception:
                pass
            self.active_widget = None
        try:
            self.destroy()
        except Exception:
            pass
        if self.manager:
            self.manager.remove_window(self)
