# Stockbit Discord Presence

A small Python app that automatically displays a **Discord Rich Presence** whenever the **Stockbit Desktop** app is running on your computer. Discord will show a "Playing Stockbit Desktop" status complete with a logo and play time.

> **Note:** This project is not affiliated with Stockbit or Discord. Just a personal script for personal use.

## Requirements

- **OS:** Windows (Stockbit Desktop runs on Windows)
- **Python:** 3.10 or newer (uses `X | Y` type syntax)
- **uv:** optional but recommended — the launcher can bootstrap the venv for you
- **Discord:** the Discord desktop app must be installed and running
- **Stockbit Desktop:** installed with the process name `Stockbit.exe`

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/ikanlelebakar/stockbit-discord-presence.git
cd stockbit-discord-presence
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```
or using uv
```bash
uv venv .venv
```

Activate the virtual environment (Windows PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

Activate the virtual environment (CMD):

```cmd
.venv\Scripts\activate.bat
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```
or using uv
```bash
uv pip install -r requirements.txt
```

## How to Run

### Option A: Double-click the launcher (recommended)

Double-click:

```
stockbit_rpc.vbs
```

> Do **not** double-click `stockbit_rpc.pyw` directly. Without a system-wide Python install (e.g. when using uv only), Windows has no `.pyw` file association and nothing will happen.

### Option B: Run with a console (for debugging)

```powershell
.venv\Scripts\Activate.ps1
python stockbit_rpc.pyw
```

### Stopping the app

Double-click:

```
stockbit_rpc_stop.vbs
```

### Option C: Run automatically on Windows startup

The easiest way is the GUI: open the settings window (`python main.py`) and
enable **Run on Startup**. This writes a small launcher script
(`stockbit-discord-presence-startup.vbs`) into your Startup folder, and
disabling the checkbox removes it again.

Prefer doing it manually?

1. Press `Win + R`, type `shell:startup`, then press Enter.
2. Right-click inside that folder → **New → Shortcut**.
3. In the location field, enter the path to `stockbit_rpc.vbs` in quotes:

   ```
   "C:\path\to\stockbit-discord-presence\stockbit_rpc.vbs"
   ```

   Adjust the path to match your project location.
4. Click **Next**, name the shortcut (e.g. `Stockbit RPC`), then click **Finish**.
5. The script now runs automatically and hidden every time the computer starts, using the project's venv Python.

## Configuration

### Using the GUI (recommended)

Run the settings window:

```
python main.py
```

(or `uv run main.py`). From there you can edit the presence text, toggle
**Run on Startup**, and watch live detection of Stockbit Desktop and Discord.

Settings are saved to:

```
%APPDATA%\StockbitDiscordPresence\config.json
```

```json
{
  "state": "No Risk No Ferari",
  "details": "Ragumu Rugimu",
  "large_text": "Stockbit Desktop",
  "run_on_startup": false
}
```

The hidden RPC script re-reads this file every 5 seconds — changes from the
GUI apply without restarting it.

### Editing the script directly

`CLIENT_ID` and `LARGE_IMAGE_KEY` live at the top of `backend/presence.py`:

```python
CLIENT_ID = "1546369679885344809"   # Do not change
LARGE_IMAGE_KEY = "stockbit_logo_-_light_-_5389x2048_-_zonalogo_com_4_"
```

Want to use your own Discord Application and logo? See
[Use Your Own RPC Application](#use-your-own-rpc-application) below.

The watched process name defaults to `Stockbit.exe` — it is the
`process_name` argument of `run_forever(...)` in `backend/presence.py` (also
exposed as `STOCKBIT_PROCESS_NAME` in `system_probes.py`). Change it only if
Stockbit is not detected — the match is case-insensitive.

## Use Your Own RPC Application

By default this project uses a shared Discord Application (`CLIENT_ID` above). To set up your own, you will need a Discord Developer Portal account and follow these steps:

### 1. Create an Application in the Discord Developer Portal

1. Open [Discord Developer Portal → Applications](https://discord.com/developers/applications) and log in.
2. Click **New Application**, give it a name (e.g. `Stockbit RPC`), then click **Create**.

### 2. Copy the Application ID (CLIENT_ID)

1. On the application page, go to **General Information**.
2. Copy the **Application ID** — this is your `CLIENT_ID`.

### 3. Upload a Logo Asset (large_image_key)

1. On the application page, go to **Rich Presence → Art Assets**.
2. Click **Add Image**, upload your logo (e.g. the Stockbit logo), and give it a name (e.g. `stockbit_logo`).
3. Remember the asset name exactly — it is case-sensitive and becomes your `LARGE_IMAGE_KEY`.

> **Tip:** Uploading large images (e.g. 5000px+) is fine — Discord will scale them down. Just keep the asset name as-is.

### 4. Update `CLIENT_ID` and `LARGE_IMAGE_KEY` in the Script

Open `backend/presence.py` and change the top two constants:

```python
CLIENT_ID = "<your-application-id>"
LARGE_IMAGE_KEY = "<your-asset-name>"
```

Save the file, then restart the hidden RPC script (double-click `stockbit_rpc.vbs` again) to pick up the change.

## Troubleshooting

1. **Status doesn't appear** — Discord isn't running. Open the Discord desktop app first.
2. **Status doesn't appear** — Wrong `CLIENT_ID`. Make sure the Application ID is correct.
3. **Status doesn't appear** — `large_image` asset missing. Make sure the asset name matches the one uploaded in the Dev Portal.
4. **Status doesn't appear** — Different process name. Check Task Manager and adjust the default process name in `backend/presence.py` (`Stockbit.exe` — the match is case-insensitive).
5. **Discord was closed while the script ran** — No action needed. The script drops the connection and reconnects automatically once Discord is open again (checked every 5 seconds).
6. **Error `ModuleNotFoundError: No module named 'psutil'`** — Dependencies not installed. Run `pip install -r requirements.txt`.
7. **`pythonw` not recognized** — Python is not in PATH. Reinstall Python with the "Add to PATH" option checked.
8. **Status doesn't disappear after Stockbit is closed** — Scan delay. Wait up to 5 seconds (the loop interval).
9. **Can't stop the app** — It runs hidden as `pythonw.exe`. Double-click `stockbit_rpc_stop.vbs`, or use Task Manager: Details tab → find `pythonw.exe` → End task.

## Project Structure

```
stockbit-discord-presence/
├── stockbit_rpc.vbs           # Hidden launcher (double-click this)
├── stockbit_rpc_stop.vbs      # Stop the running app
├── stockbit_rpc.pyw           # Hidden RPC loop entry point
├── main.py                    # GUI entry point (settings window)
├── backend/presence.py        # Presence state machine (single IPC connection)
├── frontend/config.py         # Config load/save (%APPDATA%)
├── frontend/startup.py        # Startup shortcut management
├── frontend/ui.py             # Settings window (PyQt6)
├── frontend/theme.py          # Theme tokens for the settings window
├── system_probes.py           # Shared process/IPC detection
├── requirements.txt           # Python dependencies
├── README.md                  # This document
└── .gitignore                 # Files ignored by git (.venv, __pycache__)
```
