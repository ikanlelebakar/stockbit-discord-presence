"""Windows Startup shortcut management for the hidden RPC script."""

import os
from pathlib import Path

LAUNCHER_NAME = "stockbit_rpc.vbs"
STARTUP_FILE_NAME = "stockbit-discord-presence-startup.vbs"

_STARTUP_TEMPLATE = (
    'Set shell = CreateObject("WScript.Shell")\n'
    'shell.Run "wscript.exe ""{launcher}""", 0, False\n'
)


def default_launcher_path() -> Path:
    return Path(__file__).resolve().parent.parent / LAUNCHER_NAME


def default_startup_dir() -> Path:
    return (
        Path(os.environ["APPDATA"])
        / "Microsoft"
        / "Windows"
        / "Start Menu"
        / "Programs"
        / "Startup"
    )


def startup_file(startup_dir: Path | None = None) -> Path:
    base = Path(startup_dir) if startup_dir else default_startup_dir()
    return base / STARTUP_FILE_NAME


def is_enabled(startup_dir: Path | None = None) -> bool:
    return startup_file(startup_dir).exists()


def enable(launcher_path: Path | None = None, startup_dir: Path | None = None) -> Path:
    launcher = Path(launcher_path) if launcher_path else default_launcher_path()
    launcher_str = str(launcher)
    if '"' in launcher_str:
        raise ValueError(f"Launcher path contains invalid character: {launcher_str}")
    if not launcher.exists():
        raise FileNotFoundError(f"Launcher not found: {launcher}")

    target = startup_file(startup_dir)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(_STARTUP_TEMPLATE.format(launcher=launcher), encoding="utf-8")
    return target


def disable(startup_dir: Path | None = None) -> None:
    target = startup_file(startup_dir)
    if target.exists():
        target.unlink()
