"""Entry point for the Desktop Widget application.

Run with:
    python main.py
Or with options:
    python main.py --widget clock
    python main.py --theme cyberpunk
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.core.config import ConfigManager
from src.core.window import WindowManager, FloatingWidgetWindow
from src.widgets import WIDGET_REGISTRY
from src.utils.theme import THEMES


def parse_args():
    parser = argparse.ArgumentParser(description="Floating Desktop Widget App")
    parser.add_argument(
        "--widget",
        choices=list(WIDGET_REGISTRY.keys()),
        help=f"Initial widget to launch ({', '.join(WIDGET_REGISTRY.keys())})"
    )
    parser.add_argument(
        "--theme",
        choices=list(THEMES.keys()),
        help=f"Color theme ({', '.join(THEMES.keys())})"
    )
    parser.add_argument(
        "--alpha",
        type=float,
        help="Window opacity (0.2 to 1.0)"
    )
    parser.add_argument(
        "--refresh",
        type=int,
        help="Auto-refresh interval in seconds (e.g. 10, 30, 60)"
    )
    parser.add_argument(
        "--provider",
        choices=["frankfurter", "api_co_id"],
        help="Currency API provider (frankfurter or api_co_id)"
    )
    parser.add_argument(
        "--minimal",
        action="store_true",
        help="Launch in minimal view (rates only)"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    config = ConfigManager()

    # Apply command-line overrides if supplied
    if args.widget:
        config.set("active_widget", args.widget, auto_save=False)
    if args.theme:
        config.set("theme_name", args.theme, auto_save=False)
    if args.alpha is not None:
        config.set("alpha", max(0.2, min(1.0, args.alpha)), auto_save=False)
    if args.refresh is not None:
        config.set("currency_refresh_seconds", max(1, args.refresh), auto_save=False)
    if args.provider:
        config.set("currency_provider", args.provider, auto_save=False)
    if args.minimal:
        config.set("minimal_view", True, auto_save=False)

    manager = WindowManager(config)
    manager.create_window(widget_key=config.get("active_widget", "currency"))

    try:
        manager.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
