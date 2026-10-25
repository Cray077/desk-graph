# 🪟 DeskGraph: Python Desktop Widget Template

> 🚀 **100% Vibe Coded with [Antigravity](https://deepmind.google/) by Google DeepMind**  
> Built iteratively in real-time through pair programming between human creativity and advanced agentic AI.

A sleek, borderless, floating **Python Tkinter Desktop Widget Application**. Built with zero mandatory third-party dependencies, featuring frameless movable windows, multi-window concurrent instances, dynamic size scaling, rich categorized themes, and real-time live canvas charts.

---

## 🤖 Vibe Coded with Antigravity

This entire project was **vibe coded** from scratch using **Antigravity**, Google DeepMind's agentic AI coding assistant:
- **Zero to Hero**: Scaffolded, architected, and refactored through conversational iteration.
- **Pure Python Canvas Magic**: Custom sparklines, smooth curves, and rounded cards rendered natively without heavy external graphics libraries.
- **Human + AI Synergy**: Crafted through rapid idea-to-execution cycles—adding multi-window spawning, live currency exchange APIs, light/dark themes, and dynamic window scaling in minutes.

---

## ✨ Features

- **🪟 Borderless Floating Windows**: Clean, minimal desktop aesthetics with a subtle, draggable header grip.
- **🖱️ Draggable Across Monitors**: Seamless multi-monitor positioning with lockable coordinates.
- **💾 Persistent State Memory**: Automatically remembers window coordinates `(x, y)`, opacity, active widget, size, and preferences in `config/settings.json`.
- **➕ Multi-Window Support**: Run multiple floating widgets concurrently! Spawn separate windows for Currency, System Graph, and Clock with a single click.
- **📐 Dynamic Window Sizing**: Instantly rescale the entire window from the right-click menu:
  - **Very Small (65%)**: Ultra-compact mini desktop ticker
  - **Small (80%)**: Sleek space-saving card
  - **Medium (100% / Default)**: Standard desktop view
  - **Large (130%)**: Comfortable readability
  - **Very Big (165%)**: Large prominent dashboard (fonts & charts scale up proportionally!)
- **📏 Ultra-Minimal Mode**: Right-click to strip down the widget to just the pure live rate numbers, removing headers, charts, and footers.
- **🎨 10 Curated Themes**:
  - **Dark Palettes**: Obsidian (Default), Emerald Glow, Cyberpunk Neon, Nordic Frost, Solar Amber, Midnight Purple
  - **Light Palettes**: Frost Slate (macOS style), Latte Cream (Warm Oat), Cherry Blossom (Soft Pastel), Sage Mint (Fresh Botanical)
- **🪙 USD/IDR Live Currency Tracker**:
  - **Dual API Providers**: Switch between Frankfurter (free, open API, zero keys needed) and API.co.id.
  - **Secondary Tickers**: Live SGD, EUR, and JPY exchange rates.
  - **Interactive Auto-Refresh**: Configurable timer (5s, 10s, 15s, 30s, 60s, 120s, 300s) with live countdown.
- **📊 Real-Time Canvas Graph**: Live CPU load monitor (via optional `psutil`) or smooth simulated activity chart.
- **🕒 Digital Clock & Calendar**: Clean timestamp, date, and day/week counter.
- **🪟 Opacity Control**: Adjust transparency on the fly (100%, 85%, 70%, 50%, 30%).
- **📌 Pinning**: Toggle Always-on-Top per window.

---

## 📁 Project Structure

```text
desk-graph/
├── config/
│   ├── settings.json            # Local user settings & API keys (auto-saved, git-ignored)
│   └── settings.example.json    # Example configuration template
├── src/
│   ├── core/
│   │   ├── config.py            # Settings manager (JSON serialization & defaults)
│   │   └── window.py            # Floating window, WindowManager, dragging, menus
│   ├── utils/
│   │   ├── canvas_helpers.py    # Native Tkinter Canvas sparkline & geometry renderers
│   │   └── theme.py             # Curated Dark & Light color palettes
│   └── widgets/
│       ├── base.py              # BaseWidget abstract class (lifecycle & scaling)
│       ├── registry.py          # Modular widget registry
│       ├── currency_widget.py   # USD/IDR exchange rate monitor with sparkline
│       ├── graph_widget.py      # System CPU / activity sparkline monitor
│       └── clock_widget.py      # Digital clock and calendar widget
├── main.py                      # Application entrypoint & CLI argument parser
├── build.bat                    # One-click Windows standalone .exe builder
├── requirements.txt             # Optional dependencies (psutil)
└── README.md                    # Project documentation
```

---

## 🚀 Getting Started

### 1. Run Directly with Python (Zero Dependencies)

DeskGraph runs out of the box using Python's standard library:

```bash
python main.py
```

### 2. Optional: Enable Hardware Monitoring

To enable real CPU and system statistics in the Graph widget, install `psutil`:

```bash
pip install -r requirements.txt
python main.py
```

### 3. Command-Line Options

You can customize the initial window state using CLI flags:

```bash
# Launch a specific widget (currency, graph, clock)
python main.py --widget currency
python main.py --widget clock
python main.py --widget graph

# Launch with custom themes
python main.py --theme cyberpunk   # Cyber Neon
python main.py --theme frost       # Clean Slate Light
python main.py --theme latte       # Warm Oat Cream
python main.py --theme sage        # Fresh Mint Botanical

# Launch in minimal view (rates only)
python main.py --minimal

# Launch with custom opacity (0.1 to 1.0)
python main.py --alpha 0.85

# Launch with custom auto-refresh interval in seconds
python main.py --refresh 15

# Choose default currency provider (frankfurter or api_co_id)
python main.py --provider frankfurter
python main.py --provider api_co_id
```

---

## 🔑 API Key & Currency Providers

DeskGraph supports two exchange rate providers for tracking live USD/IDR rates:

### 1. 🟢 Frankfurter (Default — No API Key Required)
- **Works immediately out of the box!**
- Uses the open [Frankfurter API](https://api.frankfurter.dev) (based on European Central Bank rates).
- Requires **zero configuration** and **no account or API key**.
- If you don't have an API key, simply launch DeskGraph and start tracking rates right away.

### 2. ⚡ API.co.id (High-Precision Indonesian IDR Rates)
- Provides dedicated real-time Indonesian Rupiah (IDR) exchange rates.
- Requires a free or personal API key from [api.co.id](https://api.co.id).

#### How to Add Your API Key:

> [!NOTE]
> For security, your API key is **never committed to git**. `config/settings.json` is automatically ignored in `.gitignore`.

1. **Via `config/settings.json` (Recommended)**:
   - Run the app once to generate `config/settings.json` (or copy `config/settings.example.json` to `config/settings.json`).
   - Open `config/settings.json` and paste your key into `"api_co_id_key"`:
     ```json
     {
         "currency_provider": "api_co_id",
         "api_co_id_key": "YOUR_API_CO_ID_KEY_HERE"
     }
     ```
   - Save the file. DeskGraph will automatically use your key!

2. **Via Environment Variable**:
   - You can also pass the key as an environment variable without modifying files:
     ```powershell
     # Windows PowerShell
     $env:API_CO_ID_KEY="YOUR_API_CO_ID_KEY_HERE"
     python main.py --provider api_co_id
     ```
     ```cmd
     # Windows Command Prompt
     set API_CO_ID_KEY=YOUR_API_CO_ID_KEY_HERE
     python main.py --provider api_co_id
     ```

3. **Switching Providers in the GUI**:
   - Right-click anywhere on the widget ➔ **Currency API Source** ➔ Choose **API.co.id (API Key)** or **Frankfurter (Open API)**.

---

## 🔨 Building Standalone Windows Executable (.exe)

You can compile DeskGraph into a portable Windows **`.exe`** file that runs without requiring Python:

### One-Click Build:
Double-click [`build.bat`](build.bat) or run from PowerShell / Command Prompt:

```cmd
build.bat
```

### How the Build Works:
1. Automatically verifies Python and installs `PyInstaller` if not present.
2. Compiles `main.py` with the `--noconsole` flag (no popup terminal window).
3. Produces a portable executable at:
   ```text
   dist\DeskGraph.exe
   ```
4. Place `dist\DeskGraph.exe` anywhere and double-click to launch!

---

## 🖱️ Controls & Right-Click Menu

| Control | Action |
| :--- | :--- |
| **Drag Window** | Left-click and drag the top title bar or grip icon (`⠿`) |
| **➕ Add Window** | Click `➕` on title bar to spawn a new floating widget window |
| **📌 Pin Window** | Click `📌` on title bar to toggle Always-on-Top |
| **✕ Close Window** | Click `✕` to close the active window (app exits when all windows close) |
| **Right-Click** | Opens the rich context menu anywhere on the widget |
| **Window Size** | Right-click ➔ `Window Size` ➔ Very Small / Small / Medium / Large / Very Big |
| **Minimal Mode** | Right-click ➔ `Minimal View (Rates Only)` |
| **Title Bar** | Right-click ➔ `Show Title Bar` (toggle header visibility) |
| **Palette Theme** | Right-click ➔ `Theme Palette` ➔ Select from 10 Dark/Light palettes |
| **Opacity** | Right-click ➔ `Opacity` ➔ 100%, 85%, 70%, 50%, or 30% |

---

## 🤝 Contributing & AI-Friendly

Contributions are **warmly welcomed**! Whether you want to:
- 💡 Add new widgets (crypto tickers, weather cards, pomodoro timers, notes, reminders)
- 🎨 Create beautiful new color themes
- ⚡ Improve Canvas rendering performance
- 🐛 Fix bugs or report issues

### 🤖 AI Usage is 100% Encouraged!
Feel free to use **AI coding assistants** (Antigravity, Claude, ChatGPT, GitHub Copilot, Cursor, etc.) to vibe-code your pull requests and features! 
1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/cool-widget`).
3. Vibe-code your changes and test with `python main.py`.
4. Submit a Pull Request.

---

## 📜 License

MIT License — Free to use, modify, and distribute for personal or commercial projects.
