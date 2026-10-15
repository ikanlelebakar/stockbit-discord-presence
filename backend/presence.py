"""Discord Rich Presence loop, driven by the saved config file.

The GUI owns settings; this module owns the single pypresence connection.
"""

import os
import sys
import time
from frontend.config import APP_DIR_NAME, load_config
from system_probes import STOCKBIT_PROCESS_NAME, is_process_running, stockbit_activity

CLIENT_ID = "1546369679885344809"
LARGE_IMAGE_KEY = "stockbit_logo_-_light_-_5389x2048_-_zonalogo_com_4_"

_MAX_TEXT_LEN = 128
_LOG_FILE_NAME = "rpc.log"


def _truncate(text: str) -> str:
    return text[:_MAX_TEXT_LEN] if isinstance(text, str) else text


def _log_path() -> str:
    appdata = os.environ.get("APPDATA")
    if appdata:
        return os.path.join(appdata, APP_DIR_NAME, _LOG_FILE_NAME)
    return os.path.join(os.getcwd(), _LOG_FILE_NAME)


def enrich_details(config: dict, activity: dict | None) -> dict:
    """Append ticker + focus/idle notes to the user's own config text.

    Ticker comes only from the allowlisted `` • TICKER`` dialog pattern; no account data ever reaches Discord.
    """
    details = config["details"]
    state = config["state"]
    if activity and activity.get("running"):
        if activity.get("ticker"):
            details = f"{details} • ${activity['ticker']}"
        focus_note = "Fokus" if activity.get("focused") else "Background"
        idle_note = " • Idle" if activity.get("idle") else ""
        details = f"{details} ({focus_note}{idle_note})"
        if activity.get("idle"):
            state = "Idle"
    return {
        "state": _truncate(state),
        "details": _truncate(details),
        "large_text": _truncate(config["large_text"]),
        "large_image": LARGE_IMAGE_KEY,
    }


def build_payload(config: dict, start: float, activity: dict | None = None) -> dict:
    return {**enrich_details(config, activity), "start": start}


class PresenceController:
    """State machine over one pypresence client.

    - Stockbit absent: nothing connected.
    - Stockbit present: connect once, update only when the payload changes,
      keep ``start`` stable so Discord's play time never resets.
    - Any transport failure: drop the client and retry next tick.
    """

    def __init__(self, client_factory=None, config_loader=None, is_running_probe=None, activity_probe=None):
        self._client_factory = client_factory or _default_client_factory
        self._config_loader = config_loader or load_config
        self._is_running = is_running_probe or (lambda: False)
        self._activity_probe = activity_probe or stockbit_activity

        self._client = None
        self._connected = False
        self._last_payload = None
        self._start: float = 0.0

    def tick(self):
        try:
            config = self._config_loader()
        except Exception as exc:
            _warn(f"config load failed: {exc}")
            return
        running = self._is_running()

        if not running:
            self._disconnect()
            return

        if not self._connected:
            self._connect()
            if not self._connected:
                return

        payload = build_payload(config, self._start, self._safe_activity())
        if payload != self._last_payload:
            try:
                self._client.update(**payload)
            except Exception as exc:
                _warn(f"presence update failed: {exc}")
                self._disconnect()
                return
            self._last_payload = payload


    def _safe_activity(self) -> dict | None:
        try:
            activity = self._activity_probe()
        except Exception:
            return None
        return activity if isinstance(activity, dict) else None

    def _connect(self):
        try:
            self._client = self._client_factory()
            self._client.connect()
            self._connected = True
            self._start = time.time()
            self._last_payload = None
        except Exception as exc:
            _warn(f"Discord IPC connect failed: {exc}")
            self._disconnect()

    def _disconnect(self):
        if self._client is not None:
            try:
                if self._connected:
                    self._client.clear()
                    self._client.close()
                else:
                    self._client.close()
            except Exception:
                pass
        self._client = None
        self._connected = False
        self._last_payload = None


def _default_client_factory():
    from pypresence import Presence

    return Presence(CLIENT_ID)


def _warn(message: str) -> None:
    line = f"[stockbit-rpc] {message}"
    print(line, file=sys.stderr)
    try:
        with open(_log_path(), "a", encoding="utf-8") as handle:
            handle.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {line}\n")
    except OSError:
        pass


def run_forever(
    process_name: str = STOCKBIT_PROCESS_NAME, interval: float = 5.0, ticks=None
):
    controller = PresenceController(
        is_running_probe=lambda: is_process_running(process_name)
    )
    count = 0
    while ticks is None or count < ticks:
        controller.tick()
        count += 1
        time.sleep(interval)
