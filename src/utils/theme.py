"""Theme definitions and color palettes for the desktop widget app."""

from dataclasses import dataclass

@dataclass(frozen=True)
class Theme:
    name: str
    bg: str
    card_bg: str
    card_border: str
    header_bg: str
    text_primary: str
    text_secondary: str
    text_muted: str
    accent: str
    accent_glow: str
    accent_secondary: str
    danger: str
    success: str
    font_family: str = "Segoe UI"
    is_dark: bool = True

# Pre-configured sleek dark & light themes
THEMES = {
    # --- DARK PALETTES ---
    "obsidian": Theme(
        name="Obsidian (Dark Indigo)",
        bg="#12131a",
        card_bg="#1a1c26",
        card_border="#2e3247",
        header_bg="#161822",
        text_primary="#f8fafc",
        text_secondary="#94a3b8",
        text_muted="#64748b",
        accent="#6366f1",          # Indigo
        accent_glow="#3730a3",
        accent_secondary="#38bdf8", # Sky
        danger="#f43f5e",
        success="#10b981",
        font_family="Segoe UI",
        is_dark=True,
    ),
    "emerald": Theme(
        name="Emerald Matrix (Dark)",
        bg="#0d1411",
        card_bg="#13201b",
        card_border="#1f382f",
        header_bg="#0f1a16",
        text_primary="#ecfdf5",
        text_secondary="#6ee7b7",
        text_muted="#047857",
        accent="#10b981",          # Emerald
        accent_glow="#065f46",
        accent_secondary="#34d399",
        danger="#f87171",
        success="#34d399",
        font_family="Segoe UI",
        is_dark=True,
    ),
    "cyberpunk": Theme(
        name="Cyber Neon (Dark)",
        bg="#140f1d",
        card_bg="#1f162e",
        card_border="#3d2b59",
        header_bg="#191225",
        text_primary="#fdf4ff",
        text_secondary="#f0abfc",
        text_muted="#a21caf",
        accent="#ec4899",          # Neon Pink
        accent_glow="#831843",
        accent_secondary="#a855f7", # Purple
        danger="#f43f5e",
        success="#06b6d4",
        font_family="Segoe UI",
        is_dark=True,
    ),
    "nordic": Theme(
        name="Nordic Aurora (Dark Navy)",
        bg="#0f172a",
        card_bg="#1e293b",
        card_border="#334155",
        header_bg="#152238",
        text_primary="#f8fafc",
        text_secondary="#94a3b8",
        text_muted="#64748b",
        accent="#38bdf8",          # Ice Blue
        accent_glow="#0284c7",
        accent_secondary="#2dd4bf", # Mint
        danger="#f43f5e",
        success="#34d399",
        font_family="Segoe UI",
        is_dark=True,
    ),
    "solar": Theme(
        name="Solar Ember (Dark Amber)",
        bg="#1a130e",
        card_bg="#261c15",
        card_border="#443124",
        header_bg="#1f1610",
        text_primary="#fffbeb",
        text_secondary="#fde68a",
        text_muted="#b45309",
        accent="#f97316",          # Orange Glow
        accent_glow="#7c2d12",
        accent_secondary="#eab308", # Gold
        danger="#ef4444",
        success="#10b981",
        font_family="Segoe UI",
        is_dark=True,
    ),
    "midnight": Theme(
        name="Midnight Onyx (Pure Dark)",
        bg="#08080a",
        card_bg="#121216",
        card_border="#24242c",
        header_bg="#0e0e12",
        text_primary="#ffffff",
        text_secondary="#a1a1aa",
        text_muted="#52525b",
        accent="#f43f5e",          # Crimson
        accent_glow="#881337",
        accent_secondary="#a855f7",
        danger="#ef4444",
        success="#10b981",
        font_family="Segoe UI",
        is_dark=True,
    ),

    # --- LIGHT PALETTES ---
    "frost": Theme(
        name="Frost White (Light Slate)",
        bg="#f1f5f9",
        card_bg="#ffffff",
        card_border="#cbd5e1",
        header_bg="#e2e8f0",
        text_primary="#0f172a",    # Dark Slate 900
        text_secondary="#334155",  # Slate 700
        text_muted="#64748b",      # Slate 500
        accent="#2563eb",          # Royal Blue
        accent_glow="#dbeafe",
        accent_secondary="#0284c7",
        danger="#dc2626",
        success="#16a34a",
        font_family="Segoe UI",
        is_dark=False,
    ),
    "latte": Theme(
        name="Latte Cream (Warm Light)",
        bg="#f5f0eb",
        card_bg="#ffffff",
        card_border="#ded2c5",
        header_bg="#ebe2d8",
        text_primary="#292524",    # Dark Warm Coffee
        text_secondary="#57534e",  # Stone 600
        text_muted="#78716c",      # Stone 500
        accent="#d97706",          # Honey Amber
        accent_glow="#fef3c7",
        accent_secondary="#ea580c", # Cinnamon
        danger="#dc2626",
        success="#15803d",
        font_family="Segoe UI",
        is_dark=False,
    ),
    "cherry": Theme(
        name="Cherry Blossom (Pastel Rose)",
        bg="#fff1f2",
        card_bg="#ffffff",
        card_border="#fecdd3",
        header_bg="#ffe4e6",
        text_primary="#4c0519",    # Deep Rosewood
        text_secondary="#881337",  # Deep Rose
        text_muted="#9f1239",      # Rose 700
        accent="#e11d48",          # Vivid Rose
        accent_glow="#fecdd3",
        accent_secondary="#ec4899", # Pink
        danger="#e11d48",
        success="#059669",
        font_family="Segoe UI",
        is_dark=False,
    ),
    "sage": Theme(
        name="Sage Mint (Botanical Light)",
        bg="#f0f7f4",
        card_bg="#ffffff",
        card_border="#c6e2d7",
        header_bg="#dceee7",
        text_primary="#064e3b",    # Deep Evergreen
        text_secondary="#047857",  # Emerald 700
        text_muted="#059669",      # Green 600
        accent="#059669",          # Mint Emerald
        accent_glow="#d1fae5",
        accent_secondary="#0d9488", # Teal
        danger="#dc2626",
        success="#059669",
        font_family="Segoe UI",
        is_dark=False,
    ),
}

DEFAULT_THEME = THEMES["obsidian"]
