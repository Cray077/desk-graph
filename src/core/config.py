import sys
import json
import os
from pathlib import Path
from typing import Any, Dict

DEFAULT_CONFIG: Dict[str, Any] = {
    "x": 100,
    "y": 100,
    "alpha": 0.95,
    "always_on_top": True,
    "locked": False,
    "theme_name": "obsidian",
    "active_widget": "currency",
    "refresh_rate_ms": 1000,
    "currency_refresh_seconds": 30,
    "currency_provider": "frankfurter",
    "minimal_view": False,
    "show_titlebar": True,
    "window_size": "medium",
    "scale_factor": 1.0,
    "api_co_id_key": ""
}

class ConfigManager:
    """Handles loading and persisting widget settings to JSON."""

    def __init__(self, config_path: Path = None):
        if config_path is None:
            if getattr(sys, "frozen", False):
                # When running as compiled .exe, store right next to DeskGraph.exe
                base_dir = Path(sys.executable).resolve().parent
            else:
                # When running via Python script, store in project root / config
                base_dir = Path(__file__).resolve().parent.parent.parent

            self.config_dir = base_dir / "config"
            self.config_file = self.config_dir / "settings.json"
        else:
            self.config_file = Path(config_path)
            self.config_dir = self.config_file.parent

        self._data: Dict[str, Any] = dict(DEFAULT_CONFIG)
        self.load()

    def load(self) -> Dict[str, Any]:
        """Load settings from disk, applying defaults for any missing keys."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    self._data.update(loaded)
            except Exception as e:
                print(f"[ConfigManager] Error reading config: {e}. Using defaults.")
        else:
            self.save()
        return self._data

    def save(self) -> None:
        """Persist current settings to disk."""
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=4)
        except Exception as e:
            print(f"[ConfigManager] Error saving config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any, auto_save: bool = True) -> None:
        self._data[key] = value
        if auto_save:
            self.save()
