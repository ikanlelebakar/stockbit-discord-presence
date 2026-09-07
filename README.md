# Stockbit Discord Presence

A small Python app that automatically displays a **Discord Rich Presence** whenever the **Stockbit Desktop** app is running on your computer. Discord will show a "Playing Stockbit Desktop" status complete with a logo and play time.

> **Note:** This project is not affiliated with Stockbit or Discord. Just a personal script for personal use.

## Requirements

- **OS:** Windows (Stockbit Desktop runs on Windows)
- **Python:** 3.8 or newer
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

### Option C: Run automatically on Windows startup

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

All configuration lives at the top of `stockbit_rpc.pyw`:

```python
CLIENT_ID = "1546369679885344809"   # Do not change
PROCESS_NAME = "Stockbit.exe"       # Change only if Stockbit is not detected
```

### Changing the status text

Edit the `rpc.update(...)` section:

```python
rpc.update(
    state="No Risk No Ferari",
    details="Ragumu Rugimu",
    large_text="Stockbit Desktop",
    start=time.time()
)
```

## Troubleshooting

1. **Status doesn't appear** — Discord isn't running. Open the Discord desktop app first.
2. **Status doesn't appear** — Wrong `CLIENT_ID`. Make sure the Application ID is correct.
3. **Status doesn't appear** — `large_image` asset missing. Make sure the asset name matches the one uploaded in the Dev Portal.
4. **Status doesn't appear** — Different process name. Check Task Manager and adjust `PROCESS_NAME` (e.g. `Stockbit.exe` vs `stockbit.exe` — the script is case-insensitive).
5. **Script stops when Discord is closed** — IPC connection dropped. Close and rerun the script.
6. **Error `ModuleNotFoundError: No module named 'psutil'`** — Dependencies not installed. Run `pip install -r requirements.txt`.
7. **`pythonw` not recognized** — Python is not in PATH. Reinstall Python with the "Add to PATH" option checked.
8. **Status doesn't disappear after Stockbit is closed** — Scan delay. Wait up to 5 seconds (the loop interval).

## Project Structure

```
stockbit-discord-presence/
├── stockbit_rpc.vbs     # Hidden launcher (double-click this)
├── stockbit_rpc.pyw     # Main script
├── requirements.txt     # Python dependencies
├── README.md            # This document
└── .gitignore           # Files ignored by git (.venv)
```
