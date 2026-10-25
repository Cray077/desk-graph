"""USD to IDR Currency Exchange Rate desktop widget using api.co.id."""

import os
import time
import json
import queue
import threading
import urllib.request
import tkinter as tk
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any

from .base import BaseWidget
from ..utils.theme import Theme
from ..utils.canvas_helpers import draw_sparkline
from ..core.config import ConfigManager

DEFAULT_API_KEY = ""

CURRENCY_PROVIDERS: Dict[str, Dict[str, Any]] = {
    "frankfurter": {
        "name": "Frankfurter",
        "url": "https://api.frankfurter.dev/v2/rates?base=usd",
        "requires_key": False
    },
    "api_co_id": {
        "name": "API.co.id",
        "url": "https://use.api.co.id/currency/USD",
        "requires_key": True
    }
}


class CurrencyWidget(BaseWidget):
    """Desktop widget for real-time USD/IDR exchange rates with mini trend chart."""

    def __init__(self, master: tk.Misc, theme: Theme, config: ConfigManager, **kwargs):
        super().__init__(master, theme, config, **kwargs)

        self.api_key = os.environ.get("API_CO_ID_KEY") or self.config.get("api_co_id_key", "")
        self.provider_key = self.config.get("currency_provider", "frankfurter")
        self.current_idr: Optional[float] = None
        self.prev_idr: Optional[float] = None
        self.other_rates: Dict[str, float] = {}
        self.rate_history: List[float] = []
        self.max_history = 16
        self._msg_queue: queue.Queue = queue.Queue()

        self.last_updated_time_str = "--:--:--"
        self._is_fetching = False
        self._last_fetch_time = 0.0
        self._fetch_interval_seconds = int(self.config.get("currency_refresh_seconds", 30))
        self.is_minimal = bool(self.config.get("minimal_view", False))

        self._build_ui()

    def get_title(self) -> str:
        return "USD / IDR FX"

    def get_preferred_size(self) -> Tuple[int, int]:
        s = getattr(self, "scale_factor", 1.0)
        if self.is_minimal:
            return (max(160, int(240 * s)), max(36, int(48 * s)))
        return (max(200, int(300 * s)), max(130, int(185 * s)))

    def _build_ui(self) -> None:
        s = getattr(self, "scale_factor", 1.0)

        # Top banner: USD -> IDR tag and LIVE status
        self.top_row = tk.Frame(self, bg=self.theme.bg)
        self.top_row.pack(fill=tk.X, padx=max(6, int(12 * s)), pady=(max(4, int(8 * s)), max(1, int(2 * s))))

        provider_name = CURRENCY_PROVIDERS.get(self.provider_key, {}).get("name", "API")
        self.pair_badge = tk.Label(
            self.top_row,
            text=f"USD ➔ IDR • {provider_name}",
            font=(self.theme.font_family, max(6, int(8 * s)), "bold"),
            fg=self.theme.accent,
            bg=self.theme.card_bg,
            padx=max(3, int(6 * s)),
            pady=max(1, int(2 * s))
        )
        self.pair_badge.pack(side=tk.LEFT)

        self.status_label = tk.Label(
            self.top_row,
            text="● CONNECTING",
            font=(self.theme.font_family, max(5, int(7 * s)), "bold"),
            fg=self.theme.text_muted,
            bg=self.theme.bg
        )
        self.status_label.pack(side=tk.RIGHT)

        # Main rate readout row
        self.rate_row = tk.Frame(self, bg=self.theme.bg)
        self.rate_row.pack(fill=tk.X, padx=max(6, int(12 * s)), pady=(max(2, int(4 * s)), max(1, int(2 * s))))

        self.rate_label = tk.Label(
            self.rate_row,
            text="Rp ---,---",
            font=(self.theme.font_family, max(11, int(18 * s)), "bold"),
            fg=self.theme.text_primary,
            bg=self.theme.bg
        )
        self.rate_label.pack(side=tk.LEFT)

        self.diff_label = tk.Label(
            self.rate_row,
            text="",
            font=(self.theme.font_family, max(6, int(8 * s)), "bold"),
            fg=self.theme.text_muted,
            bg=self.theme.bg
        )
        self.diff_label.pack(side=tk.RIGHT, pady=max(2, int(4 * s)))

        # Mini Canvas Sparkline for trend
        self.canvas_width = max(160, int(276 * s))
        self.canvas_height = max(30, int(48 * s))
        self.canvas = tk.Canvas(
            self,
            width=self.canvas_width,
            height=self.canvas_height,
            bg=self.theme.card_bg,
            highlightthickness=1,
            highlightbackground=self.theme.card_border
        )
        self.canvas.pack(padx=max(6, int(12 * s)), pady=(max(1, int(2 * s)), max(2, int(4 * s))))

        # Secondary currency ticker (SGD, EUR, JPY)
        self.sec_rates_frame = tk.Frame(self, bg=self.theme.bg)
        self.sec_rates_frame.pack(fill=tk.X, padx=max(6, int(12 * s)), pady=(0, max(2, int(4 * s))))

        self.sec_rates_label = tk.Label(
            self.sec_rates_frame,
            text="SGD: --  •  EUR: --  •  JPY: --",
            font=(self.theme.font_family, max(5, int(7 * s))),
            fg=self.theme.text_secondary,
            bg=self.theme.bg
        )
        self.sec_rates_label.pack(side=tk.LEFT)

        # Footer row: Last updated timestamp and Refresh button
        self.footer_row = tk.Frame(self, bg=self.theme.bg)
        self.footer_row.pack(fill=tk.X, padx=max(6, int(12 * s)), pady=(0, max(3, int(6 * s))))

        self.updated_label = tk.Label(
            self.footer_row,
            text="Updated: --:--:--",
            font=(self.theme.font_family, max(5, int(7 * s))),
            fg=self.theme.text_muted,
            bg=self.theme.bg
        )
        self.updated_label.pack(side=tk.LEFT)

        self.btn_refresh = tk.Label(
            self.footer_row,
            text="🔄 Refresh",
            font=(self.theme.font_family, max(5, int(7 * s)), "bold"),
            fg=self.theme.accent,
            bg=self.theme.bg,
            cursor="hand2"
        )
        self.btn_refresh.pack(side=tk.RIGHT)
        self.btn_refresh.bind("<Button-1>", lambda e: self.trigger_fetch(force=True))

        # Apply initial minimal mode if configured
        if self.is_minimal:
            self.top_row.pack_forget()
            self.canvas.pack_forget()
            self.sec_rates_frame.pack_forget()
            self.footer_row.pack_forget()
            self.rate_row.pack_configure(padx=max(8, int(14 * s)), pady=max(4, int(8 * s)))

    def on_scale_change(self, scale: float) -> None:
        """Dynamically adjust fonts, canvas dimensions, and paddings when scale changes."""
        self.scale_factor = scale
        s = scale
        if hasattr(self, "pair_badge"):
            self.pair_badge.configure(
                font=(self.theme.font_family, max(6, int(8 * s)), "bold"),
                padx=max(3, int(6 * s)),
                pady=max(1, int(2 * s))
            )
        if hasattr(self, "status_label"):
            self.status_label.configure(font=(self.theme.font_family, max(5, int(7 * s)), "bold"))
        if hasattr(self, "rate_label"):
            self.rate_label.configure(font=(self.theme.font_family, max(11, int(18 * s)), "bold"))
        if hasattr(self, "diff_label"):
            self.diff_label.configure(font=(self.theme.font_family, max(6, int(8 * s)), "bold"))
        if hasattr(self, "canvas"):
            self.canvas_width = max(160, int(276 * s))
            self.canvas_height = max(30, int(48 * s))
            self.canvas.configure(width=self.canvas_width, height=self.canvas_height)
        if hasattr(self, "sec_rates_label"):
            self.sec_rates_label.configure(font=(self.theme.font_family, max(5, int(7 * s))))
        if hasattr(self, "updated_label"):
            self.updated_label.configure(font=(self.theme.font_family, max(5, int(7 * s))))
        if hasattr(self, "btn_refresh"):
            self.btn_refresh.configure(font=(self.theme.font_family, max(5, int(7 * s)), "bold"))

        if self.is_minimal:
            if hasattr(self, "rate_row"):
                self.rate_row.pack_configure(padx=max(8, int(14 * s)), pady=max(4, int(8 * s)))
        else:
            if hasattr(self, "canvas"):
                self._render_trend()

    def set_minimal_mode(self, is_minimal: bool) -> None:
        """Toggle minimal display mode (shows current rates only, removing top banner and graph)."""
        self.is_minimal = is_minimal
        s = getattr(self, "scale_factor", 1.0)
        if is_minimal:
            self.top_row.pack_forget()
            self.canvas.pack_forget()
            self.sec_rates_frame.pack_forget()
            self.footer_row.pack_forget()
            self.rate_row.pack_configure(padx=max(8, int(14 * s)), pady=max(4, int(8 * s)))
        else:
            # Unpack and repack all elements in exact vertical order
            self.rate_row.pack_forget()
            self.top_row.pack(fill=tk.X, padx=max(6, int(12 * s)), pady=(max(4, int(8 * s)), max(1, int(2 * s))))
            self.rate_row.pack(fill=tk.X, padx=max(6, int(12 * s)), pady=(max(2, int(4 * s)), max(1, int(2 * s))))
            self.canvas.pack(padx=max(6, int(12 * s)), pady=(max(1, int(2 * s)), max(2, int(4 * s))))
            self.sec_rates_frame.pack(fill=tk.X, padx=max(6, int(12 * s)), pady=(0, max(2, int(4 * s))))
            self.footer_row.pack(fill=tk.X, padx=max(6, int(12 * s)), pady=(0, max(3, int(6 * s))))
            self._render_trend()

    def set_provider(self, provider_key: str) -> None:
        """Switch active currency provider and immediately trigger a fresh fetch."""
        if provider_key in CURRENCY_PROVIDERS:
            self.provider_key = provider_key
            self.config.set("currency_provider", provider_key)
            provider_name = CURRENCY_PROVIDERS[provider_key]["name"]
            self.pair_badge.configure(text=f"USD ➔ IDR • {provider_name}")
            self.trigger_fetch(force=True)

    def set_refresh_interval(self, seconds: int) -> None:
        """Update auto-refresh interval in seconds."""
        self._fetch_interval_seconds = max(1, seconds)
        self._update_footer_text()

    def _update_footer_text(self, remaining: Optional[int] = None) -> None:
        """Render last updated timestamp and countdown in seconds."""
        if remaining is not None:
            text = f"Updated: {self.last_updated_time_str} ({remaining}s)"
        else:
            text = f"Updated: {self.last_updated_time_str} ({self._fetch_interval_seconds}s)"
        self.updated_label.configure(text=text)

    def on_mount(self) -> None:
        """Trigger an initial background fetch on mount."""
        self.trigger_fetch(force=True)

    def on_update(self) -> None:
        """Periodic tick (every second). Drain thread queue, update countdown, and refresh."""
        # Process any pending messages from background thread
        try:
            while True:
                msg_type, payload = self._msg_queue.get_nowait()
                if msg_type == "success":
                    self._handle_fetch_success(payload)
                elif msg_type == "error":
                    self._handle_fetch_error(payload)
        except queue.Empty:
            pass

        now = time.time()
        if self._last_fetch_time > 0:
            elapsed = now - self._last_fetch_time
            remaining = max(0, int(self._fetch_interval_seconds - elapsed))
            self._update_footer_text(remaining)
            if elapsed >= self._fetch_interval_seconds:
                self.trigger_fetch()
        else:
            self._update_footer_text()

    def trigger_fetch(self, force: bool = False) -> None:
        """Spawn a background thread to fetch exchange rates without blocking GUI."""
        if self._is_fetching:
            return

        self._is_fetching = True
        self.status_label.configure(text="● UPDATING...", fg=self.theme.accent_secondary)

        thread = threading.Thread(target=self._fetch_worker, daemon=True)
        thread.start()

    def _fetch_worker(self) -> None:
        """Network worker running in a background thread supporting multiple providers."""
        provider = CURRENCY_PROVIDERS.get(self.provider_key, CURRENCY_PROVIDERS["frankfurter"])
        url = provider["url"]
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) DeskGraph/1.0"
        }
        if provider.get("requires_key"):
            key = os.environ.get("API_CO_ID_KEY") or self.config.get("api_co_id_key", "") or self.api_key
            if key:
                headers["x-api-co-id"] = key

        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                raw_data = response.read().decode("utf-8")
                data = json.loads(raw_data)
                self._msg_queue.put(("success", (self.provider_key, data)))
        except Exception as e:
            print(f"[CurrencyWidget] Fetch error ({self.provider_key}): {e}")
            self._msg_queue.put(("error", str(e)))

    def _handle_fetch_success(self, payload: Tuple[str, Any]) -> None:
        provider_key, data = payload
        self._is_fetching = False
        self._last_fetch_time = time.time()

        rates: Dict[str, float] = {}

        if provider_key == "frankfurter":
            # Frankfurter returns a list of quote objects: [{"quote": "IDR", "rate": 18060}, ...]
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "quote" in item and "rate" in item:
                        try:
                            rates[item["quote"]] = float(item["rate"])
                        except (ValueError, TypeError):
                            pass
            elif isinstance(data, dict) and "rates" in data:
                rates = data["rates"]
        elif provider_key == "api_co_id":
            # api.co.id returns {"is_success": true, "data": {"rates": {"IDR": 18000}}}
            if isinstance(data, dict) and data.get("is_success") and "data" in data:
                rates = data["data"].get("rates", {})
            else:
                msg = data.get("message", "API response error") if isinstance(data, dict) else "Error"
                self.status_label.configure(text=f"● {msg.upper()}", fg=self.theme.danger)
                return

        idr_rate = rates.get("IDR")
        # print(idr_rate) // print the exchange rate to terminal

        if idr_rate is not None:
            if self.current_idr is not None:
                self.prev_idr = self.current_idr
            self.current_idr = float(idr_rate)

            # Keep rate history for trend chart
            self.rate_history.append(self.current_idr)
            if len(self.rate_history) > self.max_history:
                self.rate_history.pop(0)

            # Format IDR with comma separators
            formatted_rate = f"Rp {self.current_idr:,.0f}"
            self.rate_label.configure(text=formatted_rate)

            # Show difference if previous rate exists
            if self.prev_idr is not None and self.prev_idr != 0:
                diff = self.current_idr - self.prev_idr
                pct = (diff / self.prev_idr) * 100
                if diff > 0:
                    self.diff_label.configure(text=f"+{diff:,.0f} (+{pct:.2f}%)", fg=self.theme.danger)
                elif diff < 0:
                    self.diff_label.configure(text=f"{diff:,.0f} ({pct:.2f}%)", fg=self.theme.success)
                else:
                    self.diff_label.configure(text="0.00%", fg=self.theme.text_muted)
            else:
                self.diff_label.configure(text="BASE USD", fg=self.theme.text_muted)

        # Secondary rates
        sgd = rates.get("SGD", "--")
        eur = rates.get("EUR", "--")
        jpy = rates.get("JPY", "--")
        self.sec_rates_label.configure(text=f"SGD: {sgd}  •  EUR: {eur}  •  JPY: {jpy}")

        # Status and timestamp
        self.last_updated_time_str = datetime.now().strftime("%H:%M:%S")
        self._update_footer_text()
        self.status_label.configure(text="● LIVE", fg=self.theme.success)

        # Redraw sparkline
        self._render_trend()

    def _handle_fetch_error(self, error_str: str) -> None:
        self._is_fetching = False
        self._last_fetch_time = time.time()
        self.status_label.configure(text="● OFFLINE", fg=self.theme.danger)
        self._update_footer_text()

    def _render_trend(self) -> None:
        """Render the mini rate trend line on the canvas."""
        self.canvas.delete("all")
        if len(self.rate_history) < 2:
            # If only 1 data point, show placeholder baseline
            mid_y = self.canvas_height / 2
            self.canvas.create_line(
                10, mid_y, self.canvas_width - 10, mid_y,
                fill=self.theme.card_border, width=1, dash=(2, 4)
            )
            self.canvas.create_text(
                self.canvas_width / 2, mid_y,
                text="Tracking price movements...",
                font=(self.theme.font_family, 7),
                fill=self.theme.text_muted
            )
            return

        min_val = min(self.rate_history) * 0.999
        max_val = max(self.rate_history) * 1.001
        if min_val == max_val:
            max_val += 1.0

        draw_sparkline(
            canvas=self.canvas,
            data=self.rate_history,
            x=8,
            y=6,
            width=self.canvas_width - 16,
            height=self.canvas_height - 12,
            min_val=min_val,
            max_val=max_val,
            line_color=self.theme.accent,
            line_width=2,
            baseline_color=self.theme.card_border
        )

    def on_theme_change(self, new_theme: Theme) -> None:
        super().on_theme_change(new_theme)
        self.top_row.configure(bg=new_theme.bg)
        self.pair_badge.configure(bg=new_theme.card_bg, fg=new_theme.accent)
        self.status_label.configure(bg=new_theme.bg)
        self.rate_row.configure(bg=new_theme.bg)
        self.rate_label.configure(bg=new_theme.bg, fg=new_theme.text_primary)
        self.diff_label.configure(bg=new_theme.bg)
        self.canvas.configure(
            bg=new_theme.card_bg,
            highlightbackground=new_theme.card_border
        )
        self.sec_rates_frame.configure(bg=new_theme.bg)
        self.sec_rates_label.configure(bg=new_theme.bg, fg=new_theme.text_secondary)
        self.footer_row.configure(bg=new_theme.bg)
        self.updated_label.configure(bg=new_theme.bg, fg=new_theme.text_muted)
        self.btn_refresh.configure(bg=new_theme.bg, fg=new_theme.accent)
        self._render_trend()
