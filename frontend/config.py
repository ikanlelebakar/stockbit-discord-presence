"""Persistence for presence text settings."""

import json
import os
from pathlib import Path

APP_DIR_NAME = "StockbitDiscordPresence"
CONFIG_FILE_NAME = "config.json"

DEFAULTS = {
    "state": "No Risk No Ferari",
    "details": "Ragumu Rugimu",
    "large_text": "Stockbit Desktop",
    "run_on_startup": False,
}


def default_path() -> Path:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise RuntimeError("APPDATA environment variable is not set")
    return Path(appdata) / APP_DIR_NAME / CONFIG_FILE_NAME


def load_config(path: Path | None = None) -> dict:
    target = Path(path) if path else default_path()
    if not target.exists():
        return dict(DEFAULTS)

    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return dict(DEFAULTS)

    if not isinstance(raw, dict):
        return dict(DEFAULTS)

    return {
        "state": _coerce_str(raw.get("state", DEFAULTS["state"])),
        "details": _coerce_str(raw.get("details", DEFAULTS["details"])),
        "large_text": _coerce_str(raw.get("large_text", DEFAULTS["large_text"])),
        "run_on_startup": bool(raw.get("run_on_startup", DEFAULTS["run_on_startup"])),
    }


def save_config(config: dict, path: Path | None = None) -> Path:
    target = Path(path) if path else default_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    clean = {key: config[key] for key in DEFAULTS}
    target.write_text(json.dumps(clean, indent=2), encoding="utf-8")
    return target


def _coerce_str(value) -> str:
    return value if isinstance(value, str) else str(value)
