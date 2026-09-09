# Contributing to Stockbit Discord Presence

Thanks for your interest in contributing! This is a small, personal-grade
utility, but improvements are welcome. Please read this guide first.

## Requirements

- **OS:** Windows 10/11 (the app is Windows-only by nature)
- **Python:** 3.10 or newer
- **Discord desktop app** installed
- **Stockbit Desktop** installed (for live testing)

## Getting Started

```bash
# 1. Clone your fork
git clone https://github.com/<your-username>/stockbit-discord-presence.git
cd stockbit-discord-presence

# 2. Create a virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1   # PowerShell
# or: .venv\Scripts\activate.bat   (CMD)
# or: uv venv .venv

# 3. Install dependencies
pip install -r requirements.txt
# or: uv pip install -r requirements.txt
```

Run the app:

```bash
python main.py        # settings window (GUI)
python stockbit_rpc.pyw   # hidden RPC loop (with console output)
```

## Testing

Unit tests are not part of the public repository, but the project is
developed with them locally. Before submitting a PR, please verify at least:

1. `python main.py` opens the settings window without errors.
2. Saving settings writes `%APPDATA%\StockbitDiscordPresence\config.json`.
3. `python stockbit_rpc.pyw` connects when Discord is running and Stockbit
   Desktop is open (presence appears on your Discord profile).
4. Closing Stockbit Desktop clears the presence within ~5 seconds.
5. The "Run on Startup" toggle creates/removes the startup file and does not
   crash when the launcher is missing.

## Coding Conventions

- Standard Python style (PEP 8); keep lines under 100 characters where
  practical.
- Type hints on public functions (`str`, `Path | None`, etc.).
- Immutability preferred: build new objects instead of mutating in place.
- Errors are handled explicitly and point at the real dependency — this
  project's principle is that error messages name the actual problem
  (Discord not running, wrong process name, missing asset), never vague
  failures.
- No new dependencies without discussion; the current footprint is
  intentionally tiny (`psutil`, `pypresence`, `PyQt6`).

## Architecture Notes

- **`main.py` + `frontend/`** — the settings window (PyQt6). It is a pure
  config editor plus a status glance; it must **never** open a second
  Discord IPC connection.
- **`stockbit_rpc.pyw` + `backend/presence.py`** — the hidden RPC loop. It
  owns the single pypresence client for the fixed `CLIENT_ID`.
- **`system_probes.py`** — shared process/IPC detection used by both sides.
- The GUI and the RPC script communicate only through the config file at
  `%APPDATA%\StockbitDiscordPresence\config.json`.

## Ground Rules

- **Do not change `CLIENT_ID`** in `backend/presence.py` — it belongs to the
  Discord application this project uses.
- **Keep the unaffiliated disclaimer** in the GUI and README. This project is
  not affiliated with Stockbit or Discord and must stay that way.
- **Windows-only is fine.** Cross-platform refactors are out of scope for
  now (Stockbit Desktop only exists on Windows).
- User-facing text (GUI copy, README, error messages) is written in English.

## Submitting a Pull Request

1. Fork the repository and create a branch from `main`:
   ```bash
   git checkout -b feat/my-change
   ```
2. Make your changes with focused commits.
3. Commit message format:
   ```
   <type>: <short description>

   Types: feat, fix, refactor, docs, test, chore
   ```
4. Push and open a PR using the provided template. Link the related issue
   if one exists.
5. Keep PRs small and focused — one feature or fix per PR.

## Reporting Issues

Use the issue templates:

- **Bug report** — include your Windows version, Python version, and what
  you saw on your Discord profile.
- **Feature request** — describe the use case first, then the proposed
  solution.

Thanks for helping make this little utility better!
